from pathlib import Path

path_resolve = lambda x: str(Path(x).expanduser().resolve())


def call_params(fn_name, fn_params):
    return globals()[f'params_{fn_name}'](fn_params)


def params_read_parquet(fn_params):
    params = {}
    params['path'] = path_resolve(fn_params['datasource']['path'])

    if fn_params['datasource'].get('env', None):
        for k, v in fn_params['datasource']['env'].get('parquet', {}).items():
            if k not in fn_params:
                params[k] = v
    return params


def params_write_parquet(fn_params):
    params = {}
    params['path'] = path_resolve(fn_params['datasource']['path'])
    params['overwrite'] = fn_params['datasource'].get('overwrite', True)
    params['write_index'] = fn_params['datasource'].get('write_index', False)
    return params


def params_read_csv(fn_params):
    params = {}
    params['path'] = path_resolve(fn_params['datasource']['path'])
    params['sep'] = fn_params['datasource'].get('sep', ',')
    params['header'] = 0 if fn_params['datasource'].get('header', True) else None
    params['encoding'] = fn_params['datasource'].get('encoding', 'utf-8')
    params['na_values'] = fn_params['datasource'].get('na_values', None)

    if fn_params['datasource'].get('schema', None):
        params['names'] = list(fn_params['datasource']['schema'].keys())

    if fn_params['datasource'].get('env', None):
        for k, v in fn_params['datasource']['env'].get('csv', {}).items():
            if k not in fn_params:
                params[k] = v

    return params


def params_write_csv(fn_params):
    params = {}
    params['path'] = path_resolve(fn_params['datasource']['path'])
    params['single_file'] = fn_params['datasource'].get('single_file', True)
    params['header_first_partition_only'] = (
        True if params['single_file'] else fn_params['datasource'].get('header_first_partition_only', None)
    )
    params['sep'] = fn_params['datasource'].get('sep', ',')
    params['encoding'] = fn_params['datasource'].get('encoding', 'utf-8')
    params['header'] = fn_params['datasource'].get('header', True)
    params['index'] = fn_params['datasource'].get('index', False)
    params['columns'] = fn_params['datasource'].get('columns', None)
    return params
