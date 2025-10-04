import os
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Args:
    path: str


class Argv:

    @staticmethod
    def get_folder_name(argv: list):
        if len(argv) > 1:
            if argv[-1].is_dir():
                return argv[-1]
            else:
                raise ValueError(f'invalid path {argv[-1]}')
        return str(Path.cwd())

    def parse_argv(self, argv: list):
        return Args(path=self.get_folder_name(argv))

class InfoProvide:

    @staticmethod
    def list_names(args: Args):
        return [n for n in os.listdir(args.path)]

    def provide_names(self, args: Args):
        return self.list_names(args)

class Printing:

    @staticmethod
    def print_inline(list_names):
        for f in list_names:
            print(f, end=' ')

    def _print(self, info):
        return self.print_inline(info)



def main(argv: list):
    args = Argv()
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv(argv)
    _info = info.provide_names(_args)
    printing._print(_info)

if __name__ == '__main__':
    main(sys.argv)
