from ups.util import (
    load_ymls,
    PathAction,
    ListAction,
    create_parser
)

def main():
    # 파서 생성 및 사용
    parser = create_parser()
    args = parser.parse_args()
    
    # YAML 파일 로드
    configs = load_ymls(['config1', 'config2'])
    
    # PathAction 사용 예시
    path_action = PathAction(option_strings=['--path'], dest='path')
    
    # ListAction 사용 예시
    list_action = ListAction(option_strings=['--items'], dest='items')

if __name__ == '__main__':
    main() 