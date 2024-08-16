# Minecraft Protobuf Queries (MCPQ) Python Client Library

This library is designed to control a Minecraft Java Server, such as [Spigot](https://www.spigotmc.org/) or [Paper](https://papermc.io/) running the **[mcpq plugin](https://github.com/mcpq/mcpq-plugin)**, with Python.

This library is heavily inspired by [MCPI](https://github.com/martinohanlon/mcpi) (and its corresponding plugin [RaspberryJuice](https://github.com/zhuowei/RaspberryJuice)) and attempts a more modern approach for communication between server and client that also works for more modern versions of Minecraft.

This library uses [Protocol Buffers](https://github.com/mcpq/mcpq-proto) and the [gRPC](https://grpc.io/) library and protocols to communicate with the [plugin](https://github.com/mcpq/mcpq-plugin) on the server.

Due to the use of the new type annotations **Python 3.10+** is required!


## Usage

After getting a [server](https://papermc.io/) and [compatible plugin](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions) setup and running, the only thing left to do is to install the python library:

```bash
pip3 install mcpq
```

Get coding!

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

To learn everything about the library checkout [the docs](https://mcpq.github.io/mcpq-python/) where the *most recent version* of the docs are available.

Only the most recent version of the docs is published. 
If you want to checkout older versions of the documentation, `git checkout` the branch or tag you want to see and use `make show_docs` to locally host the current docs at `localhost:8000`. 


## Versions

First off, to see which version of the plugin is compatible with which **Minecraft version**, checkout [this Minecraft version table](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions).

The three tuple `major.minor.patch` of the version refers to the following:

* major: [protocol version/tag](https://github.com/mcpq/mcpq-proto)
* minor: [plugin version/tag](https://github.com/mcpq/mcpq-plugin)
* patch: is incremented with patches and additional functionality of this library independend of protocol or plugin 

In other words, the first two numbers (`major.minor`) refer to the [plugin](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions) version the library was written against.

> E.g. the Python library version 1.0.X would require plugin version 1.0 or newer

This Python library *should* work for any newer versions of the plugin if everything works out and no breaking changes are introduced, at least across *minor* versions (see [table](https://github.com/mcpq/mcpq-plugin?tab=readme-ov-file#versions)).
On the other hand, the library will most likely not work for older versions of the plugin, especially not across *major* versions.

TLDR; make sure the first 2 numbers (`major.minor`) of the library version are the same as the plugin's and choose the last number as high as possible.


## Build Instructions

The library is currently [published on PyPI](https://pypi.org/project/mcpq/). The package can be downloaded from there with `pip3 install mcpq`.

You can also install this package directly by using `pip install git+https://github.com/mcpq/mcpq-python.git@<tag/branch>` to install it directly from Github (`git` is required for this).
If you cloned the repository already then `pip install .` can be used.

Building the library locally can be done by using `python -m build`, which will build the wheel and dist packages in `dist/*`.
Afterwards the tar file can be installed with pip: `pip install mcpq-0.0.0.tar.gz`.

If you want to play around with the library itself you can also clone the repository as [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

If you want to rebuild the protobuf files, for example, because you switched to a new `major` version of the [protocol](https://github.com/mcpq/mcpq-proto), first clone the `proto` submodule with `git submodule update --init --recursive`, then `cd` into the directory and `git checkout <tag>` the version you want to use.
Afterwards you can use `make proto` to re-build the stubs.


## License

[LGPLv3](LICENSE)

> Note: The *intent* behind the chosen license, is to allow the licensed software to be *used* (as is) in any type of project, even commercial or closed-source ones.
> However, changes or modifications *to the licensed software itself* must be shared via the same license openly.
> Checkout [this blog](https://fossa.com/blog/open-source-software-licenses-101-lgpl-license/) for an in-depth explanation.
