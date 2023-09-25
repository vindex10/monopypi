import dataclasses
import os


@dataclasses.dataclass
class Config:
    root_dir: str = os.path.realpath(".")
    cache_dir: str = os.path.realpath("dist")
    editable: bool = False
    pypi_fallback: str = "https://pypi.org/simple"
    pypi_fallback_timeout: int = 5


def read_cfg():
    fields = {}
    if (cache_dir := os.environ.get("CACHE_DIR")) is not None:
        fields["cache_dir"] = os.path.realpath(cache_dir)
    if (root_dir := os.environ.get("ROOT_DIR")) is not None:
        fields["root_dir"] = os.path.realpath(root_dir)
    if (editable := os.environ.get("EDITABLE")) is not None:
        fields["editable"] = editable.lower() == "true"
    return Config(**fields)


_CFG = None


def CFG():
    global _CFG
    if _CFG is None:
        _CFG = read_cfg()
    return _CFG
