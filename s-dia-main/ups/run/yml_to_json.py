import os
import yaml
from pathlib import Path


def convert_yaml_to_openapi():
    # OpenAPI 기본 구조
    openapi = {
        'openapi': '3.1.0',
        'info': {'title': 'UPS Schema API', 'version': '1.0.0', 'description': 'UPS Schema Documentation'},
        'components': {'schemas': {}},
    }

    # schemas 디렉토리 경로
    schemas_dir = Path('../ups/run/schemas')

    # 모든 YAML 파일 처리
    for root, dirs, files in os.walk(schemas_dir):
        for file in files:
            if file.endswith('.yml'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    schema = yaml.safe_load(f)

                    # 스키마 이름 추출 (파일명에서 .yml 제거)
                    schema_name = os.path.splitext(file)[0]

                    # components/schemas 아래에 스키마 추가
                    if 'components' in schema and 'schemas' in schema['components']:
                        for name, content in schema['components']['schemas'].items():
                            openapi['components']['schemas'][name] = content

    # OpenAPI YAML 파일 저장
    output_path = 'schemas/openapi.yaml'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(openapi, f, allow_unicode=True, sort_keys=False)


if __name__ == '__main__':
    convert_yaml_to_openapi()
