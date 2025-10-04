import os
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Args:
    path: str


class Argv:

    @staticmethod
    def parse_argv():
        origin_path = str(Path.cwd())
        return Args(path=origin_path)

class InfoProvide:

    @staticmethod
    def list_names(args: Args):
        return [n for n in os.listdir(args.path)]


class Printing:

    @staticmethod
    def _print(list_names):
        for f in list_names:
            print(f, end=' ')



def main(argv: list):
    args = Argv.parse_argv()
    info = InfoProvide.list_names(args)
    Printing._print(info)

if __name__ == '__main__':
    main(sys.argv)
