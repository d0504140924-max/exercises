import os
import sys
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import ctypes

class Flags(Enum):
    all = 'hidden files'


@dataclass
class Args:
    path: str
    flags: list

FILE_ATTRIBUTE_HIDDEN = 0x2

class Argv:

    @staticmethod
    def valid_path(path: str):
        return Path(path).exists()

    @staticmethod
    def valid_flags(flag: str):
        return flag in Flags.__members__


    def check_new_path(self, argv: list):
        if len(argv) > 1 and not argv[-1].startswith("-"):
            if not self.valid_path(argv[-1]):
                raise ValueError(f'invalid path {argv[-1]}')
            else:
                return argv[-1]
        return

    def get_folder_name(self, argv: list):
        return str(Path.cwd()) if len(argv) == 1 else self.check_new_path(argv)

    def split_argv(self, argv: list):
        _flag = ''
        current_flags = []
        for arg in argv:
            if arg[2] == '-':
                for letter in arg:
                    if letter.isalpha():
                        _flag += letter
                if self.valid_flags(_flag):
                    current_flags.append(_flag)
                else:
                    raise ValueError(f'invalid flag {_flag}')
            else:
                for letter in _flag:
                    if self.valid_flags(letter):
                        current_flags.append(letter)
                    else:
                        raise ValueError(f'invalid flag {_flag}')
        return current_flags


    def parse_argv(self, argv: list):
        argv1 = Args(path=self.get_folder_name(argv), flags=self.split_argv(argv))
        return argv1

class InfoProvide:

    @staticmethod
    def list_names(path: str):
        visible = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return visible

    @staticmethod
    def hidden_files(path: str):
        return [n for n in os.listdir(path)]

    def provide_names(self, args: Args):
        if 'all' in args.flags:
            return self.hidden_files(args.path)
        else:
            return self.list_names(args.path)

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
