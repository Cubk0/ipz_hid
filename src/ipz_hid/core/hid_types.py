from __future__ import annotations
from dataclasses import dataclass

from ipz_hid.core.hid_items import HIDCollectionType

@dataclass
class HIDUsage:
    page: int
    usage: int

@dataclass
class Point:
    x: int
    y: int

@dataclass
class HIDInput:
    usage: HIDUsage
    value: int = 1
    def __str__(self):
        return f"HIDInput(usage_page={self.usage.page}, usage={self.usage.usage}, value={self.value})"

class HIDInputField:
    def __init__(self,field:HIDField):
         self.field = field
         self.input_array: list[HIDInput] = []

@dataclass
class HIDCollection():
    usage: HIDUsage
    type: HIDCollectionType
    parent_index: int = -1
    tlc_index: int = -1

@dataclass
class GlobalState():
    usage_page: int = 0
    logical_max: int = 0
    logical_min: int = 0
    physical_max: int = 0
    physical_min: int = 0
    unit_exponent: int = 0
    unit: int = 0
    report_size: int = 0
    report_id: int = -1
    report_count: int = 0
