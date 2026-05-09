from ipz_hid.core.hid_types import HIDInputField
from ipz_hid.linux.input_state import *
from ipz_hid.linux.mapper import HIDLinuxMapper
from typing import Dict, Sequence
from typing import Dict, List
from evdev import UInput,AbsInfo, ecodes as e

class UInputDevice:
    def __init__(
        self,
        name: str,
        event_gen: EventGenerator,
        mapper: HIDLinuxMapper,
    ):
        self.supported_keys = event_gen.supported_keys
        self.supported_rel = event_gen.supported_rel
        self.abs_info = event_gen.abs_info
        self.event_gen = event_gen
        self.mapper = mapper
        self.prev_state = InputState()
        self.device = UInput(
            events=self._build_capabilities(),
            name=name,
        )

    def _build_capabilities(self) -> dict[int, Sequence[int]]:
        caps: Dict[int, Sequence[int]] = {}

        # EV_KEY
        if self.event_gen.supported_keys:
            caps[ecodes.EV_KEY] = list(self.event_gen.supported_keys)

        # EV_REL
        if self.event_gen.supported_rel:
            caps[ecodes.EV_REL] = list(self.event_gen.supported_rel)

        # EV_ABS
        if self.event_gen.abs_info:
            abs_caps = []
            for axis, info in self.event_gen.abs_info.items():
                abs_caps.append(
                    (
                        axis,
                        AbsInfo(
                            value=0,
                            min=info.minimum,
                            max=info.maximum,
                            fuzz=0,
                            flat=0,
                            resolution=0,
                        )
                    )
                )
            caps[ecodes.EV_ABS] = abs_caps

        return caps

    def process_fields(self, fields: list[HIDInputField]) -> None:
        curr_state = self.mapper.map(fields)
        events = self.event_gen.diff(self.prev_state, curr_state)

        for ev in events:
            self._emit(ev)

        self.prev_state = curr_state

    def _emit(self, ev: InputEvent) -> None:
        if ev.type == ecodes.EV_SYN:
            self.device.syn()
            return
        self.device.write(ev.type,ev.code, ev.value)
        self.device.syn()
