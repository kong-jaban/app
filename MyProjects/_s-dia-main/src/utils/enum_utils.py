from defined import DataType, DeIdentificationAttribute, ColumnType

def cnv_str_to_datatype(data:str):
    if data:
        if data.lower() in ["int", "int32", "int64"]:
            return DataType.LONG
        elif data.lower() in ["float", "float32", "float64", "double", "decimal"]:
            return DataType.DOUBLE
        elif data.lower() == "datetime":
            return DataType.DATETIME
        elif data.lower() == "date":
            return DataType.DATE
        
    return DataType.STRING

def cnv_datatype_to_str(datatype: DataType):
    if datatype in [DataType.INTEGER, DataType.LONG]:
        return DataType.LONG
    elif datatype in [DataType.FLOAT, DataType.DECIMAL, DataType.DOUBLE]:
        return DataType.DOUBLE
    elif datatype == DataType.DATETIME:
        return "datetime"
    elif datatype == DataType.DATE:
        return "date"
        
    return 'string'

def sdataTypeToView(data_type):
    if data_type == "FLOAT" and data_type == "DECIMAL" or data_type == "DOUBLE":
        return f"실수"
    elif data_type == "INTEGER" or data_type == "LONG":
        return f"정수"
    elif data_type == "DATETIME":
        return f"일시"
    elif data_type == "DATE":
        return f"날짜"
    return f"문자"

def dataTypeToView(data_type):
    if data_type == DataType.FLOAT and data_type == DataType.DECIMAL or data_type == DataType.DOUBLE:
        return f"실수"
    elif data_type == DataType.INTEGER or data_type == DataType.LONG:
        return f"정수"
    elif data_type == DataType.DATETIME:
        return f"일시"
    elif data_type == DataType.DATE:
        return f"날짜"
    return f"문자"

def viewToDataType(vDataType):
    if vDataType == '실수':
        return DataType.DOUBLE
    elif vDataType == '정수':
        return DataType.LONG
    elif vDataType == '일시':
        return DataType.DATETIME
    elif vDataType == '날짜':
        return DataType.DATE
    return DataType.STRING

def deIdentificationAttributeToView(vDeidAttr):
    if vDeidAttr == DeIdentificationAttribute.ID:
        return 'ID'
    elif vDeidAttr == DeIdentificationAttribute.QI:
        return 'QI'
    elif vDeidAttr == DeIdentificationAttribute.NSA:
        return 'NSA'
    elif vDeidAttr == DeIdentificationAttribute.SA:
        return 'SA'
    return ''

def viewToDeIdentificationAttribute(vDeidAttr):
    if vDeidAttr == 'ID':
        return DeIdentificationAttribute.ID
    elif vDeidAttr == 'QI':
        return DeIdentificationAttribute.QI
    elif vDeidAttr == 'NSA':
        return DeIdentificationAttribute.NSA
    elif vDeidAttr == 'SA':
        return DeIdentificationAttribute.SA
    return DeIdentificationAttribute.NONE

def ColumnTypeToView(vColumnType):
    if vColumnType == ColumnType.DEFAULT:
        return 'DEFAULT'
    elif vColumnType == ColumnType.USERDEFINED:
        return 'USERDEFINED'
    return 'DEFAULT'

def viewToColumnType(vColumnType):
    if vColumnType == 'DEFAULT':
        return ColumnType.DEFAULT
    elif vColumnType == 'USERDEFINED':
        return ColumnType.USERDEFINED
    return ColumnType.DEFAULT