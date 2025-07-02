from enum import Enum, unique

class DeIdentificationAttribute(Enum):
    NONE = ""
    ID = "ID"
    QI = "QI"
    NSA = "NSA"
    SA = "SA"
    
class ColumnType(Enum):
    DEFAULT = "DEFAULT"
    USERDEFINED = "USERDEFINED"


@unique
class DataType(Enum):
    """
    자료 타입 정의
    """
    STRING = "String"
    INTEGER = "Integer"
    LONG = "Long"
    DOUBLE = "Double"
    DECIMAL = "Decimal"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATETIME = "Datetime"
    DATE = "Date"