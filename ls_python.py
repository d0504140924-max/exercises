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
    size: str
    time: str
    permission: str
    def __str__(self):
        str_to_print = f'{self.filename} {self.size} {self.time} {self.permission}'
        return str_to_print


@dataclass
class Folder:
    details: list[File]

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
    def conflict_flags() -> dict:
        conflict_flags = {}
        conflict_flags[Flags.one] =  [Flags.zero]
        conflict_flags[Flags.zero] =  [Flags.one, Flags.size, Flags.time, Flags.permission]
        return conflict_flags

    @staticmethod
    def is_valid_flags(flag: str):
        if not flag in Flags.__members__:
            return True
        return False

    def dependant_flags(self, flags: list[Flags])->list[Flags]:
        dependant_flags = []
        if Flags.size in flags or Flags.time in flags or Flags.permission in flags:
            _add = self.check_add_flag(flags, Flags['one'])
            dependant_flags.append(_add)
        return dependant_flags

    def return_conflict(self, flags: list[Flags], flag: Flags):
        conflict_flags = self.conflict_flags()
        for key in conflict_flags:
            if key == flag:
                for _flag in conflict_flags[key]:
                    if _flag in flags:
                        return [True, (key, _flag)]
        return [False, None]

    def check_add_flag(self, current_flags: list[Flags],flag: Flags):
        if not self.is_valid_flags(flag):
            raise Exception(f'Invalid flag {flag}')
        if flag in current_flags:
            raise Exception(f'exist flag {flag}')
        con = self.return_conflict(current_flags, flag)
        if con[0]:
            raise Exception(f'Conflict {con[1]}')
        return flag


class Argv:
    def __init__(self, default_flags: AutoFlags, check_flags: CheckFlags):
        self.default_flags = default_flags
        self.check_flags = check_flags

    @staticmethod
    def valid_path(path: str):
        return Path(path).exists()


    def get_double_dash_flags(self, args: list):
        valid_double_flags = []
        input_flags =  list(filter(lambda arg: arg.startswith('--'), args))
        for flag in input_flags:
            flag = flag.replace('-', '')
            if self.check_flags.is_valid_flags(flag):
                raise ValueError(f'Invalid flag: {flag}')
            con = self.check_flags.return_conflict(valid_double_flags, Flags[flag])
            if con[0]:
                raise ValueError(f'Conflict {con[1]}')
            valid_double_flags.append(Flags[flag])
        return valid_double_flags

    def get_one_dash_flags(self, args: list):
        one_dash_flags = []
        one_dash = list(filter(lambda arg: arg.startswith('-') and arg[1] != '-', args))
        for flag in one_dash:
            flag = flag.replace('-', '')
            for letter in flag:
                if not self.check_flags.is_valid_flags(flag):
                    raise ValueError(f'Invalid flag: {flag}')
                con = self.check_flags.return_conflict(one_dash_flags, Flags[flag])
                if con[0]:
                    raise ValueError(f'Conflict {con[1]}')
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
        current_flags.extend(self.check_flags.dependant_flags(current_flags))
        current_flags.extend(self.default_flags.get_auto_flags(current_flags))
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

    def info_for_print(self, args: Args)->Folder:
        names = self.provide_files(args)
        final_names = []
        for name in names:
            full_path = os.path.join(args.path, name)
            _name = File(filename=name, size='', time='', permission='')
            if Flags.size in args.flags:
                _name.size = self.get_size(full_path)
            if Flags.time in args.flags:
                _name.time = self.get_time(full_path)
            if Flags.permission in args.flags:
                _name.permission = self.get_permission(full_path)
            final_names.append(_name)
        return Folder(final_names)


class Printing:

    @staticmethod
    def print_inline(list_names: list[File], end=' '):
        for f in list_names:
            print(f, end=end)


    @staticmethod
    def paint_folders(list_names, base='.'):
        painted = []
        for f in list_names:
            full_path = os.path.join(base, f.filename)
            if os.path.isdir(full_path):
                painted += [f'{Fore.BLUE}{str(f)}{Style.RESET_ALL} ']
            else:
                    painted += [f'{Fore.LIGHTWHITE_EX}{str(f)}{Style.RESET_ALL} ']
        return painted


    @staticmethod
    def format_row(args: Args):
        if Flags.one in args.flags:
            return '\n'
        else:
            return ' '


    def _print(self,args: Args, info: Folder):
        end_format = self.format_row(args)
        if Flags.color in args.flags:
            painted = self.paint_folders(info.details, base=args.path)
            return self.print_inline(painted, end=end_format)
        else:
            return self.print_inline(info.details, end=end_format)



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
