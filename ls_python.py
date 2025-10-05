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
    one = 'one in row'
    zero = 'end with space'
    size = 'size in bytes'


@dataclass
class Args:
    path: str
    flags: list[Flags]

class AutoFlags:

    @staticmethod
    def default_flags():
        return [Flags.color, Flags.zero]

    @staticmethod
    def check_conflicting_flags(flag: Flags, flags: list[Flags]):
        if flag == Flags.zero and Flags.one in flags:
            return True
        return False

    def get_auto_flags(self, flags: list[Flags]):
        default_flags = self.default_flags()
        auto_flags = list(filter(lambda flag: not self.check_conflicting_flags(flag, flags), default_flags))
        return set(flags + auto_flags)


FILE_ATTRIBUTE_HIDDEN = 0x2

class Argv:
    def __init__(self, default_flags: AutoFlags):
        self.default_flags = default_flags

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
        current_flags.extend(self.default_flags.get_auto_flags(argv))
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

    @staticmethod
    def only_folders(path: str):
        folders = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                folders.append(name)
        return folders


    def provide_files(self, args: Args):
        visibles = self.get_vision_files(args.path)
        if Flags.directory in args.flags:
            return self.only_folders(args.path)
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
                    painted += [f'{Fore.LIGHTWHITE_EX}{f}{Style.RESET_ALL} ']
        return painted


    @staticmethod
    def format_row(args: Args):
        if Flags.one in args.flags:
            return '\n'
        else:
            return ' '


    def _print(self,args: Args, info):
        end_format = self.format_row(args)
        if Flags.color in args.flags:
            painted = self.paint_folders(info, base=args.path)
            return self.print_inline(painted, end=end_format)
        else:
            return self.print_inline(info, end=end_format)



def main(argv: list):
    auto_flags = AutoFlags()
    args = Argv(auto_flags)
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv(argv)
    _info = info.provide_files(_args)
    printing._print(_args, _info)

if __name__ == '__main__':
    main(sys.argv)
