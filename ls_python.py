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

    @staticmethod
    def get_double_dash_flags(args: list):
        return list(filter(lambda flag: flag.startswith('--'), args))

    @staticmethod
    def get_one_dash_flags(args: list):
        double_dash_flags = []
        double_dash = list(filter(lambda flag: flag.startswith('-'), args))
        for flag in double_dash:
            _flag = (l for l in flag if not l == '-')
            double_dash_flags.append(_flag)
        return double_dash_flags


    def get_folder_name(self, argv: list):
        if len(argv) > 1 and not argv[-1].startswith("-"):
            if not self.valid_path(argv[-1]):
                raise ValueError(f'invalid path {argv[-1]}')
            else:
                return argv[-1]
        return str(Path.cwd())


    def get_flags(self, argv: list):
        current_flags = []
        one_dash = self.get_one_dash_flags(argv)
        for i in one_dash:
            for letter in i:
                if lettre.isalpha():
                    if self.valid_flags(letter):
                        current_flags.append(Flags[letter])
                    else:
                        raise ValueError(f'invalid flag {letter}')
        double_dash = self.get_double_dash_flags(argv)
        for flag in double_dash:
            if flag in Flags.__members__:
                current_flags.append(Flags[flag])
            else:
                raise ValueError(f'invalid flag {flag}')
        return current_flags


    def parse_argv(self, argv: list):
        argv1 = Args(path=self.get_folder_name(argv), flags=self.get_flags(argv))
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
            if not attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return hidden


    def provide_files(self, args: Args):
        if Flags.all in args.flags:
            visibles = self.get_vision_files(args.path)
            hidden = self.only_hidden(args.path)
            for file in hidden:
                visibles.append(file)
            return visibles

        else:
            return self.get_vision_files(args.path)

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
