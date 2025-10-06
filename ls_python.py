import os
import sys
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import ctypes
from colorama import Style, Fore
import stat
import time


class Flags(Enum):
    all = 'hidden files'
    color = 'colors'
    directory = 'only folders'
    one = 'one in row'
    zero = 'end with space'
    size = 'size in bytes'
    time = 'last time'
    permission = 'permissions'


@dataclass
class Args:
    path: str
    flags: list[Flags]

@dataclass
class File:
    filename: str
    size: int
    time: str
    permission: str

@dataclass
class Folder:
    names: list[File]

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


class CheckFlags:

    @staticmethod
    def conflict_flags() -> list[list[Flags]]:
        conflict_flags = []
        conflict1 = [Flags.one, Flags.zero]
        conflict_flags.append(conflict1)
        return conflict_flags

    @staticmethod
    def dependant_flags(flags: list[Flags])->list[Flags]:
        dependant_flags = []
        if Flags.size in flags or Flags.time in flags or Flags.permission in flagsand:
            dependant_flags.append(Flags['one'])
        return dependant_flags

    @staticmethod
    def valid_flags(flag: Flags):
        if not flag in Flags.__members__:
            return True
        return False

    def return_conflict(self, flags: list[Flags], flag: Flags):
        conflict_flags = self.conflict_flags()
        for list_flag in conflict_flags:
            if flag in list_flag:
                for _flag in list_flag:
                    if _flag != flag and _flag in flags:
                        return [True, list_flag]
        return [False, None]

    def check_add_flags(self, current_flags: list[Flags], add_flags: list[Flags]):
        for flag in add_flags:
            if not self.valid_flags(flag):
                raise Exception(f'Invalid flag {flag}')
            if flag in current_flags:
                raise Exception(f'exist flag {flag}')
        conflict = map(lambda _flag: self.return_conflict(current_flags_flags, _flag), add_flags)
        for con in lst(conflict):
            if con[0]:
                raise Exception(f'Conflict{con[1]}')
        return add_flags

    def add_flags(self, current_flags: list[Flags]):
        dependant_flags = self.dependant_flags(current_flags)
        add_flags = self.check_add_flags(current_flags, dependant_flags)
        return add_flags

class Argv:
    def __init__(self, default_flags: AutoFlags, check_flags: CheckFlags):
        self.default_flags = default_flags
        self.check_flags = check_flags

    @staticmethod
    def valid_path(path: str):
        return Path(path).exists()


    def get_double_dash_flags(self, args: list):
        valid_flags = []
        input_flags =  list(filter(lambda arg: arg.startswith('--'), args))
        for flag in input_flags:
            flag = flag.replace('-', '')
            if not self.check_flags.valid_flags(flag):
                raise ValueError(f'Invalid flag: {flag}')
            else:
                valid_flags.append(Flags[flag])
            if self.check_flags.the_one_flag(valid_flags):
                valid_flags.append(Flags['one'])
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
        if self.check_flags.check(argv):
            raise ValueError(f'invalid flag/s ')
        current_flags = self.get_one_dash_flags(argv)
        current_flags.extend(self.get_double_dash_flags(argv))
        current_flags.extend(self.default_flags.get_auto_flags(current_flags))
        current_flags.extend(self.check_flags.add_flags(current_flags))
        return list(set(current_flags))


    def parse_argv(self, argv: list):
        if len(argv) > 1 and not argv[-1].startswith("-"):
            path = self.get_folder_name(argv[-1])
        else:
            path = str(Path.cwd())
        argv1 = Args(path=path, flags=self.get_flags(argv))
        return argv1




FILE_ATTRIBUTE_HIDDEN = 0x2

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

    @staticmethod
    def get_size(path : str):
        st = os.stat(path)
        return f"{st.st_size:}"

    @staticmethod
    def get_time(path : str):
        st = os.stat(path)
        dt = time.localtime(st.st_mtime)
        date_s = time.strftime("%d/%m/%Y", dt)
        time_s = time.strftime("%H:%M", dt)
        return f'[{date_s}, {time_s}]'

    @staticmethod
    def get_permission(path : str):
        st = os.stat(path)
        perm = stat.filemode(st.st_mode)
        return f'{perm}'

    def provide_files(self, args: Args)->list:
        if Flags.directory in args.flags:
            names =  self.only_folders(args.path)
            if Flags.all in args.flags:
                names.extend(self.only_hidden(args.path))
        else:
            names = self.get_vision_files(args.path)
            if Flags.all in args.flags:
                names.extend(self.only_hidden(args.path))
        return names

    def info_for_print(self, args: Args)->list[list]:
        names = self.provide_files(args)
        final_names = []
        for name in names:
            full_path = os.path.join(args.path, name)
            _name = name
            if Flags.size in args.flags:
                _name += f'. size= {self.get_size(full_path)}'
            if Flags.time in args.flags:
                _name += f'. time= {self.get_time(full_path)}'
            if Flags.permission in args.flags:
                _name += f'. perm= {self.get_permission(full_path)}'
            final_names.append([name, _name])
        return final_names


class Printing:

    @staticmethod
    def print_inline(list_names: list, end=' '):
        for f in list_names:
            print(f, end=end)


    @staticmethod
    def paint_folders(list_names, base='.'):
        painted = []
        for f in list_names:
            full_path = os.path.join(base, f[0])
            if os.path.isdir(full_path):
                painted += [f'{Fore.BLUE}{f[1]}{Style.RESET_ALL} ']
            else:
                    painted += [f'{Fore.LIGHTWHITE_EX}{f[1]}{Style.RESET_ALL} ']
        return painted


    @staticmethod
    def format_row(args: Args):
        if Flags.one in args.flags:
            return '\n'
        else:
            return ' '


    def _print(self,args: Args, info: list):
        end_format = self.format_row(args)
        if Flags.color in args.flags:
            painted = self.paint_folders(info, base=args.path)
            return self.print_inline(painted, end=end_format)
        else:
            return self.print_inline(info, end=end_format)



def main(argv: list):
    auto_flags = AutoFlags()
    check_flags = CheckFlags()
    args = Argv(auto_flags, check_flags)
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv(argv)
    _info = info.info_for_print(_args)
    printing._print(_args, _info)

if __name__ == '__main__':
    main(sys.argv)
