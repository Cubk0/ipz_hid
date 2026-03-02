from ipz_hid.linux.input_state import *
from typing import Dict, List, Optional
from ipz_hid.core.HID_usages import *
from ipz_hid.core.HID_classes import *
from ipz_hid.core.HID_helpers import *
from evdev import ecodes


unk	= ecodes.KEY_UNKNOWN
hid_keyboard= [
	  0,  0,  0,  0, 30, 48, 46, 32, 18, 33, 34, 35, 23, 36, 37, 38,
	 50, 49, 24, 25, 16, 19, 31, 20, 22, 47, 17, 45, 21, 44,  2,  3,
	  4,  5,  6,  7,  8,  9, 10, 11, 28,  1, 14, 15, 57, 12, 13, 26,
	 27, 43, 43, 39, 40, 41, 51, 52, 53, 58, 59, 60, 61, 62, 63, 64,
	 65, 66, 67, 68, 87, 88, 99, 70,119,110,102,104,111,107,109,106,
	105,108,103, 69, 98, 55, 74, 78, 96, 79, 80, 81, 75, 76, 77, 71,
	 72, 73, 82, 83, 86,127,116,117,183,184,185,186,187,188,189,190,
	191,192,193,194,134,138,130,132,128,129,131,137,133,135,136,113,
	115,114,unk,unk,unk,121,unk, 89, 93,124, 92, 94, 95,unk,unk,unk,
	122,123, 90, 91, 85,unk,unk,unk,unk,unk,unk,unk,111,unk,unk,unk,
	unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,
	unk,unk,unk,unk,unk,unk,179,180,unk,unk,unk,unk,unk,unk,unk,unk,
	unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,
	unk,unk,unk,unk,unk,unk,unk,unk,111,unk,unk,unk,unk,unk,unk,unk,
	 29, 42, 56,125, 97, 54,100,126,164,166,165,163,161,115,114,113,
	150,158,159,128,136,177,178,176,142,152,173,140,unk,unk,unk,unk
]
class HIDLinuxMapper:
    def get_abs_axis_info(self, input_fields: List[HIDField]) -> List[Dict[int, AbsAxisInfo]]:
        max_index = max(field.application_collection.tlc_index for field in input_fields)
        result: List[Dict[int, AbsAxisInfo]] = [{} for _ in range(max_index + 1)]

        for field in input_fields:
            if field.attributes.is_constant or not field.attributes.is_variable or field.attributes.is_relative:
                continue

            tlc_idx = field.application_collection.tlc_index
            for usage in field.usage_table:

                info = AbsAxisInfo(
                    minimum=field.logical_min,
                    maximum=field.logical_max
                )

                if usage.usage == GenericDesktopUsage.HAT_SWITCH:
                    hat_info = AbsAxisInfo(
                        minimum=-1,
                        maximum=1
                    )
                    result[tlc_idx][ecodes.ABS_HAT0X] = hat_info
                    result[tlc_idx][ecodes.ABS_HAT0Y] = hat_info
                else:
                    abs_code = self._map_hid_to_linux_abs(field,usage)
                    if abs_code != -1:
                        result[tlc_idx][abs_code] = info
        return result


    def get_supported_keys(self, input_fields: List[HIDField]) -> List[List[int]]:
        max_index = max(field.application_collection.tlc_index for field in input_fields)
        keys: List[List[int]] = [[] for _ in range(max_index + 1)]
        for field in input_fields:
            tlc_idx = field.application_collection.tlc_index
            for usage in field.usage_table:
                key_code = self._map_hid_to_linux_key(field, usage)
                if key_code != -1 and key_code not in keys[tlc_idx]:
                    keys[tlc_idx].append(key_code)
        return keys 


    def get_supported_rel(self, input_fields: List[HIDField]) -> List[List[int]]:
        max_index = max(field.application_collection.tlc_index for field in input_fields)
        rels: List[List[int]] = [[] for _ in range(max_index + 1)]
        for field in input_fields:
            if not field.attributes.is_relative:
                continue
            tlc_idx = field.application_collection.tlc_index
            for usage in field.usage_table:
                rel_code = self._map_hid_to_linux_rel(field, usage)
                if rel_code != -1 and rel_code not in rels[tlc_idx]:
                    rels[tlc_idx].append(rel_code)
        return rels
    def _map_hid_to_linux_key(self, field: HIDField,usage: HIDUsage) -> int:
        if usage.page == UsagePage.KEYBOARD_KEYPAD:
            if usage.usage < len(hid_keyboard):
                key = hid_keyboard[usage.usage]
                if key != ecodes.KEY_RESERVED:
                    return key
        app_usage = field.application_collection.usage
        phys_usage = (
            field.physical_collection.usage
            if field.physical_collection is not None
            else None
        )
        if usage.page == UsagePage.BUTTON:
            button_number = usage.usage
            if (
                app_usage == HIDUsage(page=UsagePage.GENERIC_DESKTOP, usage=GenericDesktopUsage.MOUSE)
                or phys_usage == HIDUsage(page=UsagePage.GENERIC_DESKTOP, usage=GenericDesktopUsage.POINTER)
            ):

                mouse_map = {
                    1: ecodes.BTN_LEFT,
                    2: ecodes.BTN_RIGHT,
                    3: ecodes.BTN_MIDDLE,
                    4: ecodes.BTN_SIDE,
                    5: ecodes.BTN_EXTRA,
                }
                return mouse_map.get(button_number, -1)

            if 1 <= button_number <= 32:
                return ecodes.BTN_0 + (button_number - 1)

            return -1

        return -1
    def _map_hid_to_linux_abs(self, field: HIDField, usage: HIDUsage) -> int:
        if usage.page == UsagePage.SIMULATION_CONTROLS:
            sim_map = {
                SimulationUsage.RUDDER: ecodes.ABS_RUDDER,
                SimulationUsage.THROTTLE: ecodes.ABS_THROTTLE,
                SimulationUsage.ACCELERATOR: ecodes.ABS_GAS,
                SimulationUsage.BRAKE: ecodes.ABS_BRAKE,
            }
            return sim_map.get(SimulationUsage(usage.usage), -1)
        if usage.page != UsagePage.GENERIC_DESKTOP:
            return -1
        mapping = {
            GenericDesktopUsage.X: ecodes.ABS_X,
            GenericDesktopUsage.Y: ecodes.ABS_Y,
            GenericDesktopUsage.Z: ecodes.ABS_Z,
            GenericDesktopUsage.RX: ecodes.ABS_RX,
            GenericDesktopUsage.RY: ecodes.ABS_RY,
            GenericDesktopUsage.RZ: ecodes.ABS_RZ,
            GenericDesktopUsage.SLIDER: ecodes.ABS_THROTTLE,
            GenericDesktopUsage.DIAL: ecodes.ABS_RUDDER,
            GenericDesktopUsage.WHEEL: ecodes.ABS_WHEEL,
        }

        return mapping.get(GenericDesktopUsage(usage.usage), -1)
    def _map_hid_to_linux_rel(self, field: HIDField, usage:HIDUsage) -> int:
        if usage.page != UsagePage.GENERIC_DESKTOP:
            return -1
        mapping = {
            GenericDesktopUsage.X: ecodes.REL_X,
            GenericDesktopUsage.Y: ecodes.REL_Y,
            GenericDesktopUsage.Z: ecodes.REL_Z,
            GenericDesktopUsage.RX: ecodes.REL_RX,
            GenericDesktopUsage.RY: ecodes.REL_RY,
            GenericDesktopUsage.RZ: ecodes.REL_RZ,
            GenericDesktopUsage.WHEEL: ecodes.REL_WHEEL,
        }
        return mapping.get(GenericDesktopUsage(usage.usage), -1)
     
        
    def map(self, input_fields: list[HIDInputField]) -> InputState:
        output = InputState()
        for input_field in input_fields:
            for input in input_field.input_array:
                match input.usage.page:

                    case UsagePage.KEYBOARD_KEYPAD|UsagePage.BUTTON:
                        key_code = self._map_hid_to_linux_key(input_field.field, input.usage)
                        if key_code != -1:
                            output.keys[key_code] = 1 if input.value != 0 else 0
                    case UsagePage.GENERIC_DESKTOP:
                        match input.usage.usage:
                            case GenericDesktopUsage.X|GenericDesktopUsage.Y|GenericDesktopUsage.Z|GenericDesktopUsage.RX|GenericDesktopUsage.RY|GenericDesktopUsage.RZ|GenericDesktopUsage.SLIDER|GenericDesktopUsage.DIAL|GenericDesktopUsage.WHEEL:
                                if(input_field.field.attributes.is_relative):
                                    rel_code = self._map_hid_to_linux_rel(input_field.field, input.usage)
                                    if rel_code != -1:
                                        output.rel_axes[rel_code] = input.value
                                else:
                                    abs_code = self._map_hid_to_linux_abs(input_field.field, input.usage)
                                    if abs_code != -1:
                                        output.abs_axes[abs_code] = input.value
                            case GenericDesktopUsage.HAT_SWITCH:
                                # 0=Up, 1=Up-Right, 2=Right, 3=Down-Right,
                                # 4=Down, 5=Down-Left, 6=Left, 7=Up-Left,

                                value = input.value
                                hat_x = 0
                                hat_y = 0
                                if value in range(8, 15):
                                    continue
                                else:
                                    directions = {
                                        0: (0, -1),
                                        1: (1, -1),
                                        2: (1, 0),
                                        3: (1, 1),
                                        4: (0, 1),
                                        5: (-1, 1),
                                        6: (-1, 0),
                                        7: (-1, -1),
                                    }
                                    hat_x, hat_y = directions.get(value, (0, 0))
                                output.abs_axes[ecodes.ABS_HAT0X] = hat_x
                                output.abs_axes[ecodes.ABS_HAT0Y] = hat_y

                    case UsagePage.SIMULATION_CONTROLS:
                        if(input_field.field.attributes.is_relative):
                            rel_code = self._map_hid_to_linux_rel(input_field.field, input.usage)
                            if rel_code != -1:
                                output.rel_axes[rel_code] = input.value
                        else:
                            abs_code = self._map_hid_to_linux_abs(input_field.field, input.usage)
                            if abs_code != -1:
                                output.abs_axes[abs_code] = input.value
        return output
