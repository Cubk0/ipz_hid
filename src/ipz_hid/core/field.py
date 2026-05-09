from __future__ import annotations
from typing import TYPE_CHECKING

from ipz_hid.core.hid_helpers import get_int_from_bytes
from ipz_hid.core.hid_items import HIDCollectionType, HIDFieldAttributes, HIDMainTag
from ipz_hid.core.hid_types import HIDCollection, HIDInput, HIDInputField

if TYPE_CHECKING:
    from ipz_hid.core.device import HIDDevice

class HIDField():
    def __init__(self,
                 tag:HIDMainTag,
                 attributes:HIDFieldAttributes,
                 device:HIDDevice,
                 report_id:int,
                 usage_table,
                 collection:HIDCollection,
                 report_size:int,
                 report_count:int,
                 logical_max:int=0,
                 logical_min:int=0
                 ):
        self.attributes = attributes
        self.device =device
        self.collection = collection
        self.physical_collection = device._get_collection_with_type(collection,HIDCollectionType.PHYSICAL)
        application_collection= device._get_collection_with_type(collection, HIDCollectionType.APPLICATION)
        if application_collection is None:
            raise ValueError("No APPLICATION collection found")
        self.application_collection:HIDCollection =application_collection
        self.logical_collection = device._get_collection_with_type(collection,HIDCollectionType.LOGICAL)
        self.tag =  tag
        self.usage_table = usage_table
        self.report_size = report_size
        self.report_count = report_count
        self.report_id = report_id
        self.logical_max = logical_max
        self.logical_min = logical_min
        self.report_items = []
        self.bit_offset = 0
        self._variable_usages_parsed = False
    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return (
            f"HIDField\n"
            f"  Tag: {self.tag}\n"
            f"  Report ID: {self.report_id}\n"
            f"  Report Size: {self.report_size} bits\n"
            f"  Report Count: {self.report_count}\n"
            f"  Logical Range: [{self.logical_min}, {self.logical_max}]\n"
            f"  Attributes: {self.attributes}\n"
            f"  Usage Table size: {len(self.usage_table)}\n"
            f"  Application Collection: {self.application_collection}\n"
            f"  Physical Collection: {self.physical_collection}\n"
            f"  Logical Collection: {self.logical_collection}\n"
            f"  Bit Offset: {self.bit_offset}\n"
            f"  Report Items: {len(self.report_items)} item(s)"
        )
    def get_size_bits(self):
        return self.report_size * self.report_count
    def parse_array(self,report:bytes,output:list[list[HIDInputField]]):
        input_field = HIDInputField(field= self)
        for i in range(self.report_count):
            value = get_int_from_bytes(report, self.report_size * i+self.bit_offset, self.report_size)
            if(self.logical_min<0 and value >2**(self.report_size-1)-1):
                value = value- 2**self.report_size
            usage_index = value - self.logical_min

            usage = self.usage_table[usage_index] if 0 <= usage_index < len(self.usage_table) else self.usage_table[-1]
            if(usage.page >=0xFF00):
                continue
            input_field.input_array.append(HIDInput(usage,1))
        index = self.application_collection.tlc_index
        while len(output) <= index:
            output.append([])
        output[index].append(input_field)


    def parse_variable(self,report:bytes,output:list[list[HIDInputField]]):
        usage_count = len(self.usage_table)
        input_field = HIDInputField(field=self)
        for i in range(self.report_count):
            value = get_int_from_bytes(report, self.report_size * i+self.bit_offset, self.report_size)
            if(self.logical_min<0 and value >2**(self.report_size-1)-1):
                value = value- 2**self.report_size
            index =i
            if i >= usage_count:
                index = usage_count -1
            usage = self.usage_table[index]
            if(usage.page >=0xFF00):
                continue
            if (not self.attributes.is_null_state and (value < self.logical_min or value > self.logical_max)):
                print(f"Variable usage value {value} out of logical range {self.logical_min} to {self.logical_max}")
            input_field.input_array.append(HIDInput(usage,value))
        index = self.application_collection.tlc_index
        while len(output) <= index:
            output.append([])
        output[index].append(input_field)


    def parse_and_add(self,report:bytes,output:list[list[HIDInputField]]):
        if self.attributes.is_constant:
            return;
        if self.attributes.is_variable:
            self.parse_variable(report,output)
        else:
            self.parse_array(report,output)
