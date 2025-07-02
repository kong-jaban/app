import argparse
from pathlib import Path
import yaml


###########################################
def load_ymls(ymls: list[str], encoding: str = 'utf-8') -> any:
    def _join(loader, node):
        seq = loader.construct_sequence(node)
        return ''.join([str(x) for x in seq])

    yml_str = ''
    for x in ymls:
        with open(x, encoding=encoding) as f:
            yml_str += f.read() + '\n'

    yaml.add_constructor('!join', _join, Loader=yaml.SafeLoader)
    return yaml.load(yml_str, Loader=yaml.SafeLoader)


###########################################
# for command line action
class PathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, str(Path(values).expanduser().resolve()))
