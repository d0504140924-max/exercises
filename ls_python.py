import os
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Args:
    path: str


class Argv:

    @staticmethod
    def get_folder_name():
        return str(Path.cwd())

    def parse_argv(self):
        return Args(path=self.get_folder_name())

class InfoProvide:

    @staticmethod
    def list_names(args: Args):
        return [n for n in os.listdir(args.path)]

    def provide_names(self, args: Args):
        return self.list_names(args)

class Printing:

    @staticmethod
    def _print(list_names):
        for f in list_names:
            print(f, end=' ')

    def print_inline(self, info):
        return self._print(info)



def main(argv: list):
    args = Argv()
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv()
    _info = info.provide_names(_args)
    printing.print_inline(_info)

if __name__ == '__main__':
    main(sys.argv)
