from __future__ import annotations

from ipz_hid.core.field import HIDField
from ipz_hid.core.hid_types import HIDInputField

class HIDReportParser():
    def __init__(self,fields:list[HIDField]):
        self.id = -1
        self.fields = fields
    def parse_report(self,report:bytes)->list[list[HIDInputField]]:
        input_fields =[]
        for field in self.fields:
            field.parse_and_add(report,input_fields)
        return input_fields
