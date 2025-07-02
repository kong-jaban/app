# -*- encoding: utf-8 -*-

from defined import DataType, ColumnType, DeIdentificationAttribute

from typing import Optional
from enum import Enum, unique 

import json


class Schema():
    column_type: ColumnType = ColumnType.DEFAULT

    name: str = ""
    comment: str = ""

    data_type: DataType = DataType.STRING

    de_identi_attr: DeIdentificationAttribute = DeIdentificationAttribute.NONE
    is_distribution: bool = True
    is_statistics: bool = False
    exception_text: str = ""
    
    json: str = ""
    
    # def __init__(self, name: str, data_type: DataType):
    #     self.name = name
    #     self.data_type = data_type

    def toJson(self):
        return {
            "column_type": self.column_type.value,
            "name": self.name,
            "comment": self.comment,
            "data_type": self.data_type.value,
            "de_identi_attr": self.de_identi_attr.value,
            "is_distribution": self.is_distribution,
            "is_statistics": self.is_statistics,
            "exception_text": self.exception_text,
            "json": self.json,
        }
    
    @classmethod
    def fromJson(cls, json_string: str) -> Optional['Schema']:
        try:
            data = json.loads(json_string)
            schema = cls()
            schema.column_type = ColumnType(data.get("column_type", ColumnType.DEFAULT.value))
            schema.name = data.get("name", "")
            schema.comment = data.get("comment", "")
            schema.data_type = DataType(data.get("data_type", DataType.STRING.value))
            schema.de_identi_attr = DeIdentificationAttribute(data.get("de_identi_attr", DeIdentificationAttribute.NONE.value))
            schema.is_distribution = data.get("is_distribution", True)
            schema.is_statistics = data.get("is_statistics", True)
            schema.is_nullable = data.get("is_nullable", True)
            schema.exception_text = data.get("exception_text", "")
            schema.json = data.get("json", "")
            return schema
        except json.JSONDecodeError:
            print("유효하지 않은 JSON 문자열입니다.")
            return None
        except ValueError as e:
            print(f"값 변환 오류: {e}")
            return None
        
        