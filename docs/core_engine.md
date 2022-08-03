# Core Engine

PySQLXEngine uses [Prisma core](https://github.com/prisma/prisma-engines) to perform database queries.

[Prisma binaries](https://www.prisma.io/docs/concepts/components/prisma-engines) are written in [Rust](https://www.rust-lang.org/), so this engine wraps this core and communicates between the database and python.


## [Prisma engines](https://www.prisma.io)

At the core of each module, there typically is a [Prisma engine](https://www.prisma.io/docs/concepts/components/prisma-engines) that implements the core set of functionality. Engines are implemented in [Rust](https://www.rust-lang.org/) and expose a low-level API that is used by the higher-level interfaces.

A [Prisma engine](https://www.prisma.io/docs/concepts/components/prisma-engines) is the direct interface to the database, any higher-level interfaces always communicate with the database through the engine-layer.

As an example, [PySQLXEngine](/) connects to the query engine in order to read and write data in a database:

<figure markdown>
  ![PySQLXEngine Core](./img/core.png){ width="100%" }
  <figcaption>PySQLXEngine Core</figcaption>
</figure>


If you want something closer to the [Prisma orm](https://www.prisma.io) in python, there is the [prisma-client-py](https://prisma-client-py.readthedocs.io) that seeks to bring a very good experience and similar to what you have in [NodeJS](https://nodejs.org).
