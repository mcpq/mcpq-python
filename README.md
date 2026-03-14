# Minecraft Protobuf Queries (MCPQ) Python Client Library

[![pypi](https://img.shields.io/pypi/v/mcpq)](https://pypi.org/project/mcpq/)
[![license: lgpl](https://img.shields.io/badge/license-LGPL-purple)](https://github.com/mcpq/mcpq-python?tab=License-1-ov-file#readme)
[![docs](https://img.shields.io/badge/docs-online-brightgreen)](https://mcpq.github.io/mcpq-python)
[![plugin](https://img.shields.io/github/v/release/mcpq/mcpq-plugin?label=plugin&color=%2300b9c6)](https://github.com/mcpq/mcpq-plugin/releases)
[![minecraft](https://img.shields.io/badge/minecraft-v1%2E20%2E1%2B-blue?color=%2300b9c6)](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions)
[![downloads](https://img.shields.io/pypi/dm/mcpq)](https://pypi.org/project/mcpq/)
[![stars](https://img.shields.io/github/stars/mcpq/mcpq-python?style=social)](https://github.com/mcpq/mcpq-python)

This Python library is designed to control a Minecraft Java Server like [Paper](https://papermc.io/), or alternatively [Spigot](https://www.spigotmc.org/), running the **[mcpq plugin](https://github.com/mcpq/mcpq-plugin)**.

This library is heavily inspired by [MCPI](https://github.com/martinohanlon/mcpi) (and its corresponding plugin [RaspberryJuice](https://github.com/zhuowei/RaspberryJuice)) and attempts a more modern approach for communication between server and client that also works for more modern versions of Minecraft.

This library uses [Protocol Buffers](https://github.com/mcpq/mcpq-proto) and the [gRPC](https://grpc.io/) library and protocols to communicate with the [plugin](https://github.com/mcpq/mcpq-plugin) on the server.

Due to the use of the new type annotations **Python 3.10+** is required!


## Usage

After getting a [server](https://papermc.io/) and [compatible plugin](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions) setup and running, the only thing left to do is to install the python library:

```bash
pip install mcpq
```
> Some of the extra features in `mcpq.tools` need additional dependencies, if you want to use them install with: `pip install mcpq[tools]`

Get coding and checkout [the docs](https://mcpq.github.io/mcpq-python/) for more examples!

```python
from mcpq import Minecraft, Vec3

mc = Minecraft()  # connect to server on localhost

mc.postToChat("Hello Minecraft!")
pos = Vec3(0, 0, 0)  # origin of world, coordinates x, y and z = 0
block = mc.getBlock(pos)  # get block at origin
mc.setBlock("obsidian", pos)  # replace block with obsidian
mc.postToChat("Replaced", block, "with obsidian at", pos)
```

A good place to start is the turtle module:

```python
from mcpq import Minecraft, Vec3
from mcpq.tools import Turtle

mc = Minecraft()  # connect to server on localhost
t = Turtle(mc)  # spawn turtle at player position
t.speed(10)

for i in range(4):
    t.fd(10).right(90)
```


## Documentation

You can explore the full documentation for the library by visiting [the docs](https://mcpq.github.io/mcpq-python/), which hosts the *latest released version*.

Only the most recent version of the documentation is published there. 
If you need to view older versions, you can use `git checkout vX.Y.Z` to switch to a desired release, then run `make show_docs` to serve the `docs` folder locally at `localhost:8000`.

For documentation related to *non-tagged commits*, run `make live_docs` to build the docs first, as the `docs` folder is only committed for tagged releases.


## Versions

First off, to see which version of the plugin is compatible with which **Minecraft version**, checkout [this Minecraft version table](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions).

The three tuple `major.minor.patch` of the version refers to the following:

* major: [protocol version/tag](https://github.com/mcpq/mcpq-proto)
* minor: [plugin version/tag](https://github.com/mcpq/mcpq-plugin)
* patch: is incremented with patches and additional functionality of this library independend of protocol or plugin 

In other words, the first two numbers (`major.minor`) refer to the [plugin](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions) version the library was written against.

> E.g. the Python library version 2.0.X would require plugin version 2.0 or newer

This Python library *should* work for any newer versions of the plugin if everything works out and no breaking changes are introduced, at least across *minor* versions (see [table](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions)).
On the other hand, the library will most likely not work for older versions of the plugin, especially not across *major* versions.

TLDR; make sure the first 2 numbers (`major.minor`) of the library version are the same as the plugin's and choose the last number as high as possible.


## Build Instructions

The library is currently [published on PyPI](https://pypi.org/project/mcpq/). The package can be downloaded from there with `pip install mcpq`.

You can also install this package directly by using `pip install git+https://github.com/mcpq/mcpq-python.git@<tag/branch>` to install it directly from Github (`git` is required for this).
If you cloned the repository already then `pip install .` can be used.

Building the library locally can be done by using `python -m build`, which will build the wheel and dist packages in `dist/*`.
Afterwards the tar file can be installed with pip: `pip install mcpq-0.0.0.tar.gz`.

If you want to play around with the library itself you can also clone the repository as [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

If you want to rebuild the protobuf files, for example, because you switched to a new `major` version of the [protocol](https://github.com/mcpq/mcpq-proto), first clone the `proto` submodule with `git submodule update --init --recursive`, then `cd` into the directory and `git checkout <tag>` the version you want to use.
Afterwards you can use `make proto` to re-build the stubs.


## License

[LGPLv3](LICENSE)

> Note: The *intent* behind the chosen license is to allow the licensed software to be *used* (without modification) in any type of project, even commercial or closed-source ones.
> However, if you make changes or modifications *to the licensed software itself*, those modifications must be shared under the same license.
> Checkout [this blog](https://fossa.com/blog/open-source-software-licenses-101-lgpl-license/) for an in-depth explanation.
