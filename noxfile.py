# noxfile.py
import nox


@nox.session(python="3.10", venv_backend="uv|virtualenv")
@nox.parametrize(
    "protobuf_version",
    ["6.30.2", "5.29.4", "5.28.0", "5.26.0", "4.23.0", "3.20.0"],
)
@nox.parametrize(
    "grpcio_version",
    [
        "1.71.0",
        "1.69.0",
        "1.68.0",
        "1.66.0",
        "1.65.4",
        "1.64.0",
        "1.63.0",
    ],
)
def deps_tests(session: nox.Session, protobuf_version, grpcio_version):
    session.install("pytest", "pytest-integration", "pytest-mock", "pytest-timeout")
    session.install(f"grpcio=={grpcio_version}", "--no-deps")
    session.install(f"protobuf=={protobuf_version}", "--no-deps")
    session.install(".", "--no-deps")  # prevent upgrades
    if session.venv_backend == "uv":
        session.run("uv", "pip", "freeze")
    else:
        session.run("pip", "freeze")
    session.run("pytest")
    # session.run("pytest --no-integration")


@nox.session(python=["3.10", "3.11", "3.12", "3.13"], venv_backend="uv|virtualenv")
def py_version_tests(session: nox.Session):
    session.install("pytest", "pytest-integration", "pytest-mock", "pytest-timeout")
    # session.install("grpcio")
    # session.install("protobuf")
    session.install(".")  # install latest according to pyproject.toml
    if session.venv_backend == "uv":
        session.run("uv", "pip", "freeze")
    else:
        session.run("pip", "freeze")
    session.run("pytest")
