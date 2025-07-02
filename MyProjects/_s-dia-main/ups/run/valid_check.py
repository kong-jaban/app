from pathlib import Path
from ups.util.util import load_ymls
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
import jsonschema

from jsonschema import Draft201909Validator as draftvalidator

# from jsonschema import Draft202012Validator as draftvalidator

yml_root = Path('c:/wsw/lib/test/flow').resolve()
schema_root = Path('c:/wsw/lib/ups/run/schemas').resolve()
schema_file = Path(schema_root, 'flow_test.yml')

# 기본 타입 정의를 먼저 등록
schema_includes = [
    'definitions',
]

# table 관련 스키마
schema_includes.extend(
    [
        'table/read_csv',
        'table/read_parquet',
        'table/write_csv',
        'table/write_parquet',
        'table/cast_data_type',
        'table/orderby',
        'table/drop_columns',
        'table/select_columns',
        'table/rename_columns',
        'table/drop_duplicates',
        'table/filter',
        'table/union',
        'table/join',
        'table/get_distribution',
        'table/make_map_groupby_count',
    ]
)

# column 관련 스키마
schema_includes.extend(
    [
        'column_date/date_add',
        'column_date/date_diff',
        'column_encrypt/blake2s',
        'column_encrypt/blake2b',
        'column_encrypt/sha2',
        'column_encrypt/sha3',
        'column_encrypt/shake_128',
        'column_encrypt/shake_256',
        'column_mix/apply_conditions',
        'column_mix/fill_by_mapping',
        'column_numeric/categorize_by_equal_width',
        'column_numeric/categorize_by_interval',
        'column_numeric/categorize_by_unit',
        'column_numeric/fill_random_float',
        'column_numeric/fill_random_int',
        'column_numeric/fill_random_normal',
        'column_numeric/fill_random_sequence',
        'column_numeric/round_down',
        'column_numeric/round_up',
        'column_numeric/round',
        'column_numeric/top_bottom_3sigma',
        'column_numeric/top_bottom_15iqr',
        'column_numeric/top_bottom_coding',
        'column_numeric/top_bottom_percentile',
        'column_numeric/truncate_to_left',
        'column_string/combine_columns',
        'column_string/replace_string',
        'column_string/substring',
        'column_string/to_lower',
        'column_string/to_upper',
    ]
)


def main():
    # flow.yml 로드
    flow_schema = load_ymls([schema_file])
    registry = build_registry(schema_includes)
    validator = draftvalidator(schema=flow_schema, registry=registry)

    if 1 != 1:
        if not check_references(flow_schema, registry):
            print("검증을 진행할 수 없습니다: $ref 참조 문제 발생")
            return

        for x in schema_includes:
            print(f'========== {x} ==========')
            schema = load_ymls([Path(schema_root, f'{x}.yml')])
            if not check_references(schema, registry):
                print("검증을 진행할 수 없습니다: $ref 참조 문제 발생")
                return

    validate_flow(validator, yml_root)


def validate_flow(validator, path):
    for f in Path(path).glob('*'):
        if f.is_dir():
            validate_flow(validator, f)

        if f.is_file() and f.name != 'env.yml' and f.suffix == '.yml':
            if f.name != '01read_write.yml':
                continue
            data = load_ymls([f'{yml_root}/env.yml', f])
            validator.validate(data)


def build_registry(file_list):
    registry = Registry()

    for f in file_list:
        path = Path(schema_root, f'{f}.yml')
        # $ref 에 쓴 것과 똑같아야 함
        uri = str(path).replace(str(schema_root), '').replace('\\', '/')[1:]
        # print(uri)

        schema = load_ymls([path])
        registry = registry.with_resource(uri, Resource.from_contents(schema))

    return registry


# $ref 참조 확인
def check_references(schema, registry):
    try:
        # Draft201909Validator 초기화로 기본 $ref 해결 여부 확인
        validator = Draft201909Validator(schema=schema, registry=registry)
        print("스키마 초기화 성공: $ref 참조가 기본적으로 해결됨")

        # $ref 값을 수집
        def collect_refs(node, refs=None, path=""):
            if refs is None:
                refs = []
            if isinstance(node, dict):
                if "$ref" in node:
                    ref = node["$ref"]
                    if not isinstance(ref, str):
                        print(f"잘못된 $ref 형식 (경로: {path}): {ref} (문자열이어야 함)")
                        return refs
                    refs.append((ref, path))
                for key, value in node.items():
                    collect_refs(value, refs, f"{path}.{key}" if path else key)
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    collect_refs(item, refs, f"{path}[{i}]")
            return refs

        # $ref 확인
        refs = collect_refs(schema)
        if not refs:
            print("스키마에 $ref가 없습니다.")
            return True

        for ref, path in refs:
            print(f"$ref 확인 중: '{ref}' (경로: {path})")
            if ref.startswith("#"):
                # 내부 참조: JSON Pointer로 직접 확인
                pointer = ref[1:].strip('/')  # '#' 제거
                try:
                    # JSON Pointer로 스키마 내 경로 탐색
                    current = schema
                    for part in pointer.split('/'):
                        current = current.get(part, {})
                    if not current:
                        print(f"내부 $ref '{ref}'를 해결할 수 없습니다 (경로: {path}): 정의 없음")
                        return False
                    print(f"내부 $ref '{ref}'가 성공적으로 참조됨 (경로: {path}): {current}")
                except Exception as e:
                    print(f"내부 $ref '{ref}'를 해결할 수 없습니다 (경로: {path}): {e}")
                    return False
            else:
                # 외부 참조: Registry에서 확인
                uri = ref.split("#")[0] if "#" in ref else ref
                try:
                    resolved = registry.get(uri)
                    if resolved is None:
                        print(f"외부 $ref '{ref}'가 Registry에 등록되지 않았습니다.")
                        return False
                    print(f"외부 $ref '{ref}'가 성공적으로 참조됨 (경로: {path}): {resolved.contents}")
                except Unresolvable as e:
                    print(f"외부 $ref '{ref}'를 해결할 수 없습니다 (경로: {path}): {e}")
                    return False
                except Exception as e:
                    print(f"예상치 못한 에러 ($ref: {ref}, 경로: {path}): {e}")
                    return False
        return True
    except jsonschema.exceptions.SchemaError as e:
        print(f"스키마 오류: {e}")
        return False
    except jsonschema.exceptions.RefResolutionError as e:
        print(f"참조 오류: $ref를 해결할 수 없습니다: {e}")
        return False
    except Exception as e:
        print(f"예상치 못한 에러: {e}")
        return False


if __name__ == '__main__':
    main()
