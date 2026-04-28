from __future__ import annotations
import dataclasses
from enum import IntEnum
from dataclasses import dataclass
from typing import Dict, List, Optional
from ipz_hid.core.HID_usages import *
from ipz_hid.core.HID_helpers import *
from ipz_hid.core.HID_items import *

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


class HIDDescriptor():
    def __init__(self,items: list[HIDItem] = []):
        self.items = items
    @classmethod
    def from_bytes(cls,data:bytes):
        index =0
        items=[]
        while (index < len(data)):
            item = HIDItem.from_bytes(data[index:])
            items.append(item)
            index += 1 + len(item.item_data)
        return cls(items)
    def __str__(self):
        res= ""
        indentation = 0;
        for item in self.items:
            if item.item_tag == HIDMainTag.END_COLLECTION:
                indentation -=1
            res += indentation* "  " +str(item) + "\n"
            if item.item_tag == HIDMainTag.COLLECTION:
                indentation +=1
        return res;

@dataclass
class HIDCollection():
    usage: HIDUsage
    type: HIDCollectionType
    parent_index: int = -1
    tlc_index: int = -1

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
            usage = self.usage_table[value] if value < len(self.usage_table) else self.usage_table[-1]
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

class HIDReportParser():
    def __init__(self,fields:list[HIDField]):
        self.id = -1
        self.fields = fields
    def parse_report(self,report:bytes)->list[list[HIDInputField]]:
        input_fields =[]
        for field in self.fields:
            field.parse_and_add(report,input_fields)
        return input_fields
class HIDDevice():
    def __init__(self):
        self.collections = []
        self.collection_index_stack = []
        self.fields:list[HIDField] = []
        self.input_report_parsers = {}
        self.output_report_parsers = {}
        self.feature_report_parsers = {} # TODO maybe not needed?
        self.global_state_stack = [] 
        self.global_state = GlobalState();
        self.local_usage_min = -1
        self.local_usage_min_usage_page = -1
        self.local_usage_max = -1
        self.local_usage_max_usage_page = -1
        self.local_usage_list = []
        self.using_report_ids = False
        self.top_level_collection_count = 0
        self.descriptor=None
    def _get_collection_with_type(self,collection:HIDCollection,collection_type:HIDCollectionType)-> Optional[HIDCollection]:
        if collection.type == collection_type:
            return collection
        while True:
            if collection.type == collection_type:
                return collection
            else:
                if(collection.parent_index==-1):
                    return None
                collection = self.collections[collection.parent_index]


        return None
    def _start_collection(self,usage:HIDUsage,type:HIDCollectionType):
        index = len(self.collections)
        new_collection = HIDCollection(usage,type,index)
        new_collection.parent_index = self.collection_index_stack[-1] if len(self.collection_index_stack)>0 else -1
        if(new_collection.parent_index== -1):
            new_collection.tlc_index = self.top_level_collection_count
            self.top_level_collection_count+=1
        else:
            new_collection.tlc_index = self.collections[new_collection.parent_index].tlc_index
        self.collections.append(new_collection)
        self.collection_index_stack.append(index)
    def _end_collection(self):
        if len(self.collection_index_stack)>0:
            self.collection_index_stack.pop()
        else:
            raise ValueError("Collection stack underflow")
    def _bytes_to_usage(self,usage_bytes:bytes)->HIDUsage:
       return HIDUsage(page=self.global_state.usage_page, usage=int.from_bytes(usage_bytes,'little') if len(usage_bytes)>0 else 0)
    def _parse_main(self,item:HIDItem):
        match item.item_tag:
            case HIDMainTag.COLLECTION:
                if len(self.local_usage_list) == 0:
                    raise ValueError("No usage defined for collection")
                usage = self.local_usage_list[0]
                
                if(len(self.local_usage_list)>1):
                    print("Warning: Multiple usages defined for collection, using first usage in list\n")
                self._start_collection(usage,HIDCollectionType(item.item_data[0]))
            case HIDMainTag.END_COLLECTION:
                self._end_collection()
            case HIDMainTag.INPUT | HIDMainTag.OUTPUT | HIDMainTag.FEATURE:
                if self.global_state.report_size == 0 or self.global_state.report_count == 0:
                    raise ValueError("Report size and count must be set before defining fields")
                attributes = HIDFieldAttributes.from_byte(item.item_data[0])
                new_field = HIDField(
                    device = self,
                    attributes=attributes,
                    collection=self.collections[self.collection_index_stack[-1]],
                    report_id= self.global_state.report_id,
                    tag = item.item_tag,
                    usage_table = self.local_usage_list.copy(),
                    report_size = self.global_state.report_size,
                    report_count = self.global_state.report_count,
                    logical_max = self.global_state.logical_max,
                    logical_min = self.global_state.logical_min,
                )
                self.fields.append(new_field)
        
        self.local_usage_max=-1;
        self.local_usage_min=-1;
        self.local_usage_min_usage_page=-1;
        self.local_usage_max_usage_page=-1;
        self.local_usage_min=-1;
        self.local_usage_list.clear()
    def _parse_global(self,item:HIDItem):
        match item.item_tag:
            case HIDGlobalTag.USAGE_PAGE:
                self.global_state.usage_page = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.LOGICAL_MINIMUM:
                self.global_state.logical_min = int.from_bytes(item.item_data,'little',signed=True) # TODO check signed
            case HIDGlobalTag.LOGICAL_MAXIMUM:
                self.global_state.logical_max = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.PHYSICAL_MINIMUM:
                self.global_state.physical_min = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.PHYSICAL_MAXIMUM:
                self.global_state.physical_max = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.UNIT_EXPONENT:
                self.global_state.unit_exponent = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.UNIT:
                self.global_state.unit = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.REPORT_SIZE:
                self.global_state.report_size = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.REPORT_ID:
                self.global_state.report_id = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.REPORT_COUNT:
                self.global_state.report_count = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.PUSH:
                self.global_state_stack.append(self.global_state)
                self.global_state = GlobalState()
            case HIDGlobalTag.POP:
                if len(self.global_state_stack)>0:
                    self.global_state = self.global_state_stack.pop()
                else:
                    raise ValueError("Global state stack underflow")
    def _parse_local(self,item:HIDItem):
        match item.item_tag:
            case HIDLocalTag.USAGE:
                usage = self._bytes_to_usage(item.item_data)
                self.local_usage_list.append(usage)
            case HIDLocalTag.USAGE_MINIMUM:
                self.local_usage_min = int.from_bytes(item.item_data,'little')
                self.local_usage_min_usage_page = self.global_state.usage_page
            case HIDLocalTag.USAGE_MAXIMUM:
                self.local_usage_max = int.from_bytes(item.item_data,'little')
                if self.local_usage_min == -1:
                    raise ValueError("Usage maximum defined before usage minimum")
                if self.local_usage_min_usage_page != self.global_state.usage_page:
                    raise ValueError("Usage maximum usage page does not match usage minimum usage page")
                for u in range(self.local_usage_min,self.local_usage_max+1):
                    usage = HIDUsage(self.global_state.usage_page,u)
                    if usage not in self.local_usage_list:
                        self.local_usage_list.append(usage)
                self.local_usage_min=-1
                self.local_usage_min_usage_page=-1
                self.local_usage_max=-1
                self.local_usage_max_usage_page=-1
            case _:
                raise ValueError(f"Unsupported local tag {item.item_tag}")
    def set_descriptor(self,descriptor:HIDDescriptor):
        self.descriptor = descriptor
        if len(self.collections) !=0:
            self.collections = []
            self.collection_index_stack = []
            self.fields:list[HIDField] = []
            self.input_report_parsers = {}
            self.output_report_parsers = {}
            self.feature_report_parsers = {} # TODO maybe not needed?
            self.global_state_stack = [] 
            self.global_state = GlobalState();
            self.local_usage_min = -1
            self.local_usage_min_usage_page = -1
            self.local_usage_max = -1
            self.local_usage_max_usage_page = -1
            self.local_usage_list = []
            self.using_report_ids = False
            self.top_level_collection_count = 0
            self.descriptor=None
        for item in descriptor.items:
            match item.item_type:
                case HIDItemType.MAIN:
                    self._parse_main(item)
                case HIDItemType.GLOBAL:
                    self._parse_global(item)
                case HIDItemType.LOCAL:
                    self._parse_local(item)
                case _:
                    raise ValueError(f"Unsupported item type {item.item_type}")
        for field in self.fields:
            if field.report_id != -1:
                self.using_report_ids = True
            match field.tag:
                case HIDMainTag.INPUT:
                    if field.report_id not in self.input_report_parsers:
                        self.input_report_parsers[field.report_id] = HIDReportParser([])
                    else:
                        prev_field = self.input_report_parsers[field.report_id].fields[-1]
                        field.bit_offset = prev_field.bit_offset + prev_field.get_size_bits()
                    self.input_report_parsers[field.report_id].fields.append(field)
                case HIDMainTag.OUTPUT:
                    if field.report_id not in self.output_report_parsers:
                        self.output_report_parsers[field.report_id] = HIDReportParser([])
                    else:
                        prev_field = self.input_report_parsers[field.report_id].fields[-1]
                        field.bit_offset = prev_field.bit_offset + prev_field.get_size_bits()
                    self.output_report_parsers[field.report_id].fields.append(field)
                case HIDMainTag.FEATURE:
                    if field.report_id not in self.feature_report_parsers:
                        self.feature_report_parsers[field.report_id] = HIDReportParser([])
                    else:
                        prev_field = self.input_report_parsers[field.report_id].fields[-1]
                        field.bit_offset = prev_field.bitoffset + prev_field.get_size_bits()
                    self.feature_report_parsers[field.report_id].fields.append(field)
                case _:
                    raise ValueError(f"Unsupported field tag {field.tag}")
            if -1 in self.input_report_parsers and self.using_report_ids:
                raise ValueError("Report with no ID used while other reports have IDs\nPlease ensure all reports have IDs or none do")
    def get_descriptor(self):
        return self.descriptor
    def parse_input_report(self,report:bytes):
        if len(self.input_report_parsers) == 0:
            raise ValueError("No field defined in descriptor")
        if(self.using_report_ids):
            return self.input_report_parsers[report[0]].parse_report(report[1:])
        else:
            return self.input_report_parsers[-1].parse_report(report)
    def parse_output_report(self,report:bytes):
        if len(self.output_report_parsers) == 0:
            raise ValueError("No field defined in descriptor")
        if(self.using_report_ids):
            return self.output_report_parsers[report[0]].parse_report(report)
        else:
            return self.output_report_parsers[-1].parse_report(report)





            
 