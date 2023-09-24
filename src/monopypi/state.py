import dataclasses
import threading
from typing import Mapping


@dataclasses.dataclass
class State:
    scheme: Mapping[str, str] = dataclasses.field(default_factory=dict)
    build_locks: Mapping[str, threading.Lock] = dataclasses.field(default_factory=dict)


STATE = State()
