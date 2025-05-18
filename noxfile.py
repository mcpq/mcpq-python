import atexit
import filecmp
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import nox

# PARAMTERS:

# whether to run integration tests
# if True: if a server is running, use that one, else download and run own servers
INTEGRATION = True
# location of plugin (can be built or downloaded to root)
SERVER_PLUGIN_SEARCH_LOCATION = [
    Path(__file__).parent,
    Path(__file__).parent / "mcpq-plugin" / "build" / "libs",
    Path.home() / "mcpq-plugin" / "build" / "libs",
]
# location of the java 21 executable
SERVER_JAVA_EXE = Path("java")
# location to download servers to
SERVER_VERSIONS_FOLDER = Path(__file__).parent / ".nox_servers"

# VERSIONS (always sort from newest to oldest!)

PY_VERSIONS = [
    "3.13",
    "3.12",
    "3.11",
    "3.10",
]
MC_VERSIONS = [
    # 1.21
    "1.21.5",
    "1.21.4",
    "1.21.3",
    "1.21.1",
    "1.21",
    # 1.20
    "1.20.6",
    "1.20.5",  # TODO: entity is not loaded?
    "1.20.4",
    "1.20.2",
    "1.20.1",
]
PROTOBUF_VERSIONS = [
    "6.30.2",
    "5.29.4",
    "5.28.0",  # pinned version
    "5.26.0",
    "4.23.0",
    "3.20.0",
]
GRPCIO_VERSIONS = [
    "1.71.0",
    "1.69.0",
    "1.68.0",
    "1.66.0",
    "1.65.4",  # compiled proto / pinned version
    "1.64.0",
    "1.63.0",
]

if INTEGRATION:
    atexit.register(lambda: ServerStatus.read().kill())


@nox.session(python=PY_VERSIONS[-1], venv_backend="uv|virtualenv")
@nox.parametrize("protobuf_version", PROTOBUF_VERSIONS)
@nox.parametrize("grpcio_version", GRPCIO_VERSIONS)
def dep_test(session: nox.Session, protobuf_version, grpcio_version):
    session.install("pytest", "pytest-integration", "pytest-mock", "pytest-timeout")
    grpcio_dep = f"grpcio=={grpcio_version}"
    protobuf_dep = f"protobuf=={protobuf_version}"
    # install dependencies and local package without upgrading dependencies
    session.install(grpcio_dep, "--no-deps")
    session.install(protobuf_dep, "--no-deps")
    session.install(".", "--no-deps")
    check_installed_deps(session, [grpcio_dep, protobuf_dep, "mcpq"])
    if INTEGRATION:
        start_server(session, MC_VERSIONS[0])
        session.run("pytest")
    else:
        session.run("pytest", "--without-integration")


@nox.session(python=PY_VERSIONS, venv_backend="uv|virtualenv")
def py_test(session: nox.Session):
    session.install("pytest", "pytest-integration", "pytest-mock", "pytest-timeout")
    session.install(".")  # install latest according to pyproject.toml
    check_installed_deps(session, ["grpcio", "protobuf", "mcpq"])
    if INTEGRATION:
        start_server(session, MC_VERSIONS[0])
        session.run("pytest")
    else:
        session.run("pytest", "--without-integration")


@nox.session(python=PY_VERSIONS[-1], venv_backend="uv|virtualenv")
@nox.parametrize("mc_version", MC_VERSIONS)
def mc_test(session: nox.Session, mc_version: str):
    status = start_server(session, mc_version)
    if not status.is_nox:
        session.error("Cannot test mc versions with an already running server")
    session.install("pytest", "pytest-integration", "pytest-mock", "pytest-timeout")
    session.install(".")  # install latest according to pyproject.toml
    check_installed_deps(session, ["grpcio", "protobuf", "mcpq"])
    session.run("pytest")


def check_installed_deps(session: nox.Session, expected_installs: list[str]):
    if session.venv_backend == "uv":
        output = session.run("uv", "pip", "freeze", silent=True)
    else:
        output = session.run("pip", "freeze", silent=True)
    installed_packages = output.splitlines()
    for installed in installed_packages:
        for expected in expected_installs:
            if installed.startswith(expected):
                session.log(f"Package version {installed} was installed")
                expected_installs.remove(expected)
                break
    if expected_installs:
        session.warn(output)
        session.error(f"The following packages were not installed: {', '.join(expected_installs)}")


@dataclass(frozen=True)
class ServerStatus:
    is_nox: bool
    running: bool
    pid: int = 0
    version: str = ""
    PROC_LOCK: ClassVar[Path] = SERVER_VERSIONS_FOLDER / ".nox_server_running"

    @staticmethod
    def is_port_open(host: str, port: int, timeout: float):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
                return True
            except (ConnectionRefusedError, socket.timeout):
                return False

    @classmethod
    def read(cls) -> "ServerStatus":
        port = cls.is_port_open("localhost", 1789, 0.1)
        lock = cls.PROC_LOCK.exists()
        if lock:
            proc_pid, mc_version = cls.PROC_LOCK.read_text().strip().split(" ", 1)
            return cls(True, port, int(proc_pid), mc_version)
        return cls(False, port)

    @classmethod
    def write(cls, pid: int, mc_version: str) -> "ServerStatus":
        cls.PROC_LOCK.write_text(f"{pid} {mc_version}")
        return cls(True, True, pid, mc_version)

    def kill(self) -> "ServerStatus":
        if self.is_nox and self.pid:
            os.kill(self.pid, signal.SIGKILL)
            self.PROC_LOCK.unlink()
            return self.__class__(False, False)
        return self


def download_paper(session: nox.Session, mc_version: str, target_dir: Path) -> Path:
    uri = f"https://api.papermc.io/v2/projects/paper/versions/{mc_version}"
    if not target_dir.is_dir():
        session.error(f"Target {target_dir.resolve().as_posix()} is not a directory")
    with urllib.request.urlopen(uri) as response:
        version_info = json.loads(response.read().decode("utf-8"))
    build_version = version_info["builds"][-1]
    with urllib.request.urlopen(f"{uri}/builds/{build_version}") as response:
        build_info = json.loads(response.read().decode("utf-8"))
    download_name = str(build_info["downloads"]["application"]["name"])
    download_sha256 = str(build_info["downloads"]["application"]["sha256"])
    server_path = (target_dir / download_name).with_suffix(".jar")
    if server_path.exists():
        session.log(f"File '{server_path.resolve().as_posix()}' exists already")
        with server_path.open("rb") as existing_jar:
            existing_sha256 = hashlib.sha256(existing_jar.read()).hexdigest()
        if existing_sha256 == download_sha256:
            session.log("Hashes match, skipping download")
            return server_path
        else:
            session.warn("Hashes do NOT match, re-downloading and overwriting...")
    session.log(f"Downloading newest papermc: {download_name}")
    with urllib.request.urlopen(
        f"{uri}/builds/{build_version}/downloads/{download_name}"
    ) as response:
        response_bytes = response.read()
    response_sha256 = hashlib.sha256(response_bytes).hexdigest()
    if download_sha256 != response_sha256:
        session.error(
            f"Hashes of download '{download_name}' does not match expected hash '{download_sha256}' was '{response_sha256}'"
        )
    with server_path.open("wb") as jar_file:
        jar_file.write(response_bytes)
    session.log(f"Downloaded '{server_path.resolve().as_posix()}', hashes match")
    return server_path


def prepare_server_folder(session: nox.Session, mc_version: str) -> Path:
    folder = (SERVER_VERSIONS_FOLDER / mc_version).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    jars = list(f for f in folder.glob("*.jar") if f.is_file())
    if len(jars) == 0:
        server_path = download_paper(session, mc_version, folder)
    elif len(jars) == 1:
        server_path = jars[0]
    else:
        session.error(f"Too many jar files in {folder.as_posix()}")
    for location in SERVER_PLUGIN_SEARCH_LOCATION:
        if plugins := list(f for f in location.glob("mcpq-*.jar") if f.is_file()):
            if len(plugins) > 1:
                session.error(f"Too many mcpq plugins at location {location.as_posix()}")
            plugin = plugins[0]
            break
    else:
        session.error("MCPQ plugin could not be found in given locations")
    plugin_loc: Path = folder / "plugins" / plugin.name
    if not plugin_loc.is_file() or not filecmp.cmp(plugin, plugin_loc):
        session.log(f"Copying plugin {plugin.as_posix()}")
        if plugin_loc.parent.exists():
            shutil.rmtree(plugin_loc.parent)
        plugin_loc.parent.mkdir()
        shutil.copy(plugin, plugin_loc)
    if not (eula_loc := (folder / "eula.txt")).is_file():
        session.log(f"Accepting eula {eula_loc.as_posix()}")
        eula_loc.write_text("eula=true\n")
    if not (props := (folder / "server.properties")).is_file():
        session.log(f"Writing {props.as_posix()}")
        props.write_text("snooper-enabled=false\nspawn-protection=0\nonline-mode=false\n")
    return server_path


def start_server(session: nox.Session, mc_version: str) -> ServerStatus:
    status = ServerStatus.read()
    if not status.running and status.is_nox:
        session.error(
            f"Server SHOULD be running but is not ({ServerStatus.PROC_LOCK.as_posix()} exists, delete manually to proceed)"
        )
    if status.running and not status.is_nox:
        session.warn(
            "There is a server running but not one started with nox (cannot determine Minecraft version)"
        )
        return status
    if status.running and status.is_nox:
        if status.version != mc_version:
            session.warn(
                f"Running nox server ({status.version}) has different version (want {mc_version})"
            )
            status = status.kill()
            time.sleep(1)
        else:
            session.log("Running nox server has the correct version, already started")
            return status
    session.log(f"No servers running, setup server {mc_version}")
    server_path = prepare_server_folder(session, mc_version)
    session.log(f"Starting nox server {mc_version}")
    with session.chdir(server_path.parent):
        proc = subprocess.Popen(
            [
                SERVER_JAVA_EXE,
                "-jar",
                "-DIReallyKnowWhatIAmDoingISwear=true",
                "-Xms1G",
                "-Xmx2G",
                server_path.name,
                "nogui",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,  # Line-buffered
            # detached mode
            start_new_session=(os.name != "nt"),
            creationflags=(0x00000008 if os.name == "nt" else 0),
        )
    try:
        mcpq_running = False
        for line in proc.stdout:
            session.log(f"[server] {line.strip()}")
            if "Plugin ready: gRPC server waiting on" in line:
                mcpq_running = True
            if "Done" in line and "For help" in line:
                session.log("Server is ready")
                if not mcpq_running:
                    proc.kill()
                    session.error("Plugin was not loaded correctly")
                proc.stdout.close()
                return ServerStatus.write(proc.pid, mc_version)
    except Exception as e:
        proc.kill()
        session.error(f"Error from server: {e}")
    proc.kill()
    session.error("Server could not be started or stopped running early")


@nox.session
def stop_server(session: nox.Session):
    # keep this session last
    status = ServerStatus.read()
    if status.running and status.is_nox:
        session.log(f"Stopping server version {status.version}")
        status.kill()
