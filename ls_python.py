import os
import sys
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import ctypes
from colorama import Style, Fore

class Flags(Enum):
    all = 'hidden files'
    color = 'colors'
    directory = 'only folders'


@dataclass
class Args:
    path: str
    flags: list[Flags]

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
        input_flags =  list(filter(lambda arg: arg.startswith('--'), args))
        for flag in input_flags:
            flag = flag.replace('-', '')
            if not self.valid_flags(flag):
                raise ValueError(f'Invalid flag: {flag}')
            else:
                valid_flags.append(Flags[flag])
        return valid_flags

    def get_one_dash_flags(self, args: list):
        one_dash_flags = []
        one_dash = list(filter(lambda arg: arg.startswith('-') and arg[1] != '-', args))
        for flag in one_dash:
            flag = flag.replace('-', '')
            for letter in flag:
                if not self.valid_flags(letter):
                    raise ValueError(f'Invalid flag: {letter}')
                else:
                    one_dash_flags.append(Flags[letter])
        return one_dash_flags


    def get_folder_name(self, path: str):
        if not self.valid_path(path):
            raise ValueError(f'invalid path {path}')
        else:
            return path

    def get_flags(self, argv: list):
        current_flags = self.get_one_dash_flags(argv)
        current_flags.extend(self.get_double_dash_flags(argv))
        return current_flags


    def parse_argv(self, argv: list):
        if len(argv) > 1 and not argv[-1].startswith("-"):
            path = self.get_folder_name(argv[-1])
        else:
            path = str(Path.cwd())
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
            if  attrs != -1 and (attrs & FILE_ATTRIBUTE_HIDDEN):
                hidden.append(name)
        return hidden


    def provide_files(self, args: Args):
        visibles = self.get_vision_files(args.path)
        if Flags.directory in args.flags:
            visibles = [f for f in visibles if os.path.isdir(f)]
        if Flags.all in args.flags:
            visibles.extend(self.only_hidden(args.path))
        return visibles


class Printing:

    @staticmethod
    def print_inline(list_names: list, end=' '):
        for f in list_names:
            print(f, end=end)


    @staticmethod
    def paint_folders(list_names, base='.'):
        painted = []
        for f in list_names:
            full_path = os.path.join(base, f)
            if os.path.isdir(full_path):
                painted += [f'{Fore.BLUE}{f}{Style.RESET_ALL} ']
            else:
                    painted += [f'{Fore.LIGHTWHITE}{f}{Style.RESET_ALL} ']
        return painted


    def _print(self,args: Args, info):
        if Flags.color in args.flags:
            painted = self.paint_folders(info, base=args.path)
            return self.print_inline(painted)
        else:
            return self.print_inline(info)



def main(argv: list):
    args = Argv()
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv(argv)
    _info = info.provide_files(_args)
    printing._print(_args, _info)

if __name__ == '__main__':
    main(sys.argv)
