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


    def get_double_dash_flags(self, args: list):
        valid_flags = []
        input_flags =  list(filter(lambda flag: flag.startswith('--'), args))
        for flag in input_flags:
            if not self.valid_flags(flag)
                raise ValueError(f'Invalid flag: {flag}')
            else:
                valid_flags.append(flag)
        return valid_flags

    def get_one_dash_flags(self, args: list):
        double_dash_flags = []
        double_dash = list(filter(lambda flag: flag.startswith('-'), args))
        for flag in double_dash:
            _flag = (l for l in flag if not l == '-')
            for letter in _flag:
                if not self.valid_flags(letter)
                    raise ValueError(f'Invalid flag: {letter}')
                else:
                    double_dash_flags.append(letter)
        return double_dash_flags


    def get_folder_name(self, path: str):
        if not self.valid_path(path):
            raise ValueError(f'invalid path {path}')
        else:
            return path



    def get_flags(self, argv: list):
        current_flags = self.get_one_dash_flags(argv)
        double_dash = self.get_double_dash_flags(argv)
        for flag in double_dash:
            current_flags.append(flag)
        return current_flags


    def parse_argv(self, argv: list):
        if len(argv) > 1 and not argv[-1].startswith("-"):
            path = get_folder_name(argv[-1])
        else:
            path = Path.cwd()
        argv1 = Args(path=path, flags=self.get_flags(argv))
        return argv1

class InfoProvide:

    @staticmethod
    def get_vision_files(path: str):
        visible = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return visible
    @staticmethod
    def only_hidden(path: str):
        hidden = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if  attrs == -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return hidden


    def provide_files(self, args: Args):
        visibles = self.get_vision_files(args.path)
        if Flags.all in args.flags:
            visibles.extend(self.only_hidden(args.path))
        return visibles


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
