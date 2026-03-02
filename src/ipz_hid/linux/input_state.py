from dataclasses import dataclass
from typing import Dict, List, Optional
from evdev import ecodes

@dataclass
class InputEvent:
    type: int      
    code: int     
    value: int

@dataclass
class AbsAxisInfo:
    minimum: int
    maximum: int
    def normalize_signed(self, value: int) -> float:
        if self.maximum == self.minimum:
            return 0.0
        c = (self.maximum + self.minimum) * 0.5
        if value >= c:
            return (value - c) / (self.maximum - c)
        else:
            return (value - c) / (c - self.minimum)

    def normalize_unsigned(self, value: int) -> float:
        if self.maximum == self.minimum:
            return 0.0
        return (value - self.minimum) / (self.maximum - self.minimum)



class InputState:
    def __init__(
        self,
        keys: Optional[Dict[int,int]] = None,
        rel_axes: Optional[Dict[int,int]] = None,
        abs_axes: Optional[Dict[int,int]] = None
    ):
        self.keys: Dict[int, int] = keys or {}
        self.rel_axes: Dict[int, int] = rel_axes or {}
        self.abs_axes: Dict[int, int] = abs_axes or {}
    def __eq__(self, other):
        if not isinstance(other, InputState):
            return NotImplemented
        return (
            self.keys == other.keys and
            self.rel_axes == other.rel_axes and
            self.abs_axes == other.abs_axes
        )
    def __str__(self):
        return (
            f"InputState(\n"
            f"  keys={self.keys},\n"
            f"  rel_axes={self.rel_axes},\n"
            f"  abs_axes={self.abs_axes}\n"
            f")"
        )

    __repr__ = __str__

class EventGenerator:
    def __init__(
        self,
        supported_keys: List[int],
        supported_rel: List[int],
        abs_axis_info: Dict[int, AbsAxisInfo]
    ):
        self.supported_keys: List[int] = supported_keys
        self.supported_rel: List[int] = supported_rel
        self.abs_info: Dict[int, AbsAxisInfo] = abs_axis_info

    def diff(self, prev: InputState, curr: InputState) -> List[InputEvent]:
        events: List[InputEvent] = []

        # KEYS
        for code in self.supported_keys:
            pv = prev.keys.get(code, 0)
            cv = curr.keys.get(code, 0)
            if pv != cv:
                events.append(InputEvent(ecodes.EV_KEY, code, cv))

        # ABS
        for code, info in self.abs_info.items():
            pv = prev.abs_axes.get(code, 0)
            cv = curr.abs_axes.get(code, 0)
            if pv != cv:
                events.append(InputEvent(ecodes.EV_ABS, code, cv))

        # REL
        for code in self.supported_rel:
            delta = curr.rel_axes.get(code, 0)
            if delta != 0:
                events.append(InputEvent(ecodes.EV_REL, code, delta))

        # SYN_REPORT
        if len(events) > 0:
            events.append(InputEvent(ecodes.EV_SYN, ecodes.SYN_REPORT, 0))
        return events
