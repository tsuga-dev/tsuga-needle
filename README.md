# needle

`needle` is the on-disk format Tsuga writes to object storage.
A `.needle` file is a concatenation of independent [Vortex](https://vortex.dev/) files plus a footer recording each one's byte range.

## This repository

| | |
|---|---|
| [unpacker.py](unpacker.py) | extract one `.vortex` file per entry, using no Tsuga code |
| [example.needle](example.needle) | a real example needle file |

## Quickstart

Requires Python 3.8 and the Vortex [`vx`](https://docs.vortex.dev/getting-started/install) CLI.

```
$ python3 unpacker.py example.needle
example/latency_ms__dh.vortex
example/rx__g.vortex

$ vx tree layout example/rx__g.vortex
```

## License

[Apache-2.0](LICENSE).
