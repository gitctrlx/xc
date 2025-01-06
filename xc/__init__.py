from importlib import metadata

try:
    __version__ = metadata.version("xc-cli")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
