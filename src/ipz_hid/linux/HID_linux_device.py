from ipz_hid.core.HID_classes import *
from ipz_hid.linux.mapper import *
from ipz_hid.linux.input_state import *
from typing import Dict, List,Optional

from ipz_hid.linux.virtual_device import UInputDevice
from ipz_hid.raw.HID_raw import HIDRaw


@dataclass
class HIDLinuxDeviceOptions:
    attach_hidraw: bool = False
    make_virtual_device: bool = False
    grab_events: bool = False

class HIDLinuxDevice(HIDDevice):
    def __init__(self):
        super().__init__()
        self.event_generator: Optional[EventGenerator] = None
        self.mapper: HIDLinuxMapper = HIDLinuxMapper()
        self.options: HIDLinuxDeviceOptions = HIDLinuxDeviceOptions()
        self.virtual_device: Optional[UInputDevice] = None
        self.hidraw: Optional[HIDRaw] = None
        self.event_queue = []
        self.prev_state = InputState()
    
    def set_descriptor(self, descriptor: HIDDescriptor) -> None:
        super().set_descriptor(descriptor)
        self.event_generator = EventGenerator(
            supported_keys=self.mapper.get_supported_keys(self.fields)[0],
            supported_rel=self.mapper.get_supported_rel(self.fields)[0],
            abs_axis_info=self.mapper.get_abs_axis_info(self.fields)[0]
        )
        if self.options != None and self.options.make_virtual_device:
            if self.virtual_device is not None:
                self.virtual_device.device.close()
            self.virtual_device = UInputDevice(
                name=f"Virtual HID device",
                event_gen=self.event_generator,
                mapper=self.mapper,
            )
    def get_events(self):
        if self.options.make_virtual_device:
            print("Events are processsed through the virtual device. Use that interface to read events.")
        else:
            to_ret =self.event_queue
            self.event_queue = []
            return to_ret


    @classmethod
    def from_hidraw(cls,hidraw:HIDRaw,options: HIDLinuxDeviceOptions) -> "HIDLinuxDevice":
        if not options.attach_hidraw:
            raise ValueError("attach_hidraw option must be True to create device from hidraw.")
        instance = cls()
        instance.options = options
        instance.hidraw = hidraw
        descriptor = HIDDescriptor.from_bytes( hidraw.dev_descriptor)
        instance.set_descriptor(descriptor)
        event_generator = EventGenerator(
            supported_keys=instance.mapper.get_supported_keys(instance.fields)[0] if instance.fields else [],
            supported_rel=instance.mapper.get_supported_rel(instance.fields)[0] if instance.fields else [],
            abs_axis_info=instance.mapper.get_abs_axis_info(instance.fields)[0] if instance.fields else {}
        )
        if(options.make_virtual_device):
            instance.virtual_device = UInputDevice(
                name=f"Virtual HID device",
                event_gen=event_generator,
                mapper=instance.mapper,
            )
        return instance
    @classmethod
    def from_device_name(cls,name,options: HIDLinuxDeviceOptions) -> "HIDLinuxDevice":
        hidraw = HIDRaw.from_name(name)
        return cls.from_hidraw(hidraw, options)
    @classmethod
    def from_device_path(cls, path: str, options: HIDLinuxDeviceOptions) -> "HIDLinuxDevice":
        hidraw = HIDRaw(path)
        return cls.from_hidraw(hidraw, options)
    def start(self):
        if self.hidraw is None:
            raise RuntimeError("No HIDRaw to start.")
        self.hidraw.start()
        if self.options.grab_events:
            self.hidraw.grab_all_events()
    def stop(self):
        if self.hidraw is None:
            raise RuntimeError("No HIDRaw to stop.")
        self.hidraw.close()
        if self.options.grab_events:
            self.hidraw.release()
    def read_input_report_raw(self):
        if self.hidraw is None:
            raise RuntimeError("No HIDRaw to read from.")
        data = self.hidraw.read()
        return data

    def process_input_report(self, report: bytes):
        if self.virtual_device is None:
            parsed = super().parse_input_report(report)
            curr_state = self.mapper.map(parsed[0])
            if self.event_generator is not None:
                events = self.event_generator.diff(self.prev_state, curr_state)
            else:
                print("No event generator available, cannot generate events from input report.")
                events = []
            self.event_queue.extend(events)
            return
        parsed = super().parse_input_report(report)
        if parsed is not None:
            self.virtual_device.process_fields(parsed[0])
    
    def write_output_report_raw(self,data: bytes):
        if self.hidraw is None:
            raise RuntimeError("No HIDRaw to write to.")
        self.hidraw.write(data)
