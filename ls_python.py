import os
import sys
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import ctypes
from typing import Optional, Union
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
    long = 'all details'
    u = 'access time'
    c = 'change time'


@dataclass
class Args:
    path: str
    flags: list[Flags]


@dataclass
class File:
    filename: str
    size: Optional[str]
    time: Optional[str]
    permission: Optional[str]

    def __str__(self)->str:
        str_to_print = f'{self.filename}'
        if self.size:
            str_to_print += f' {self.size}'
        if self.time:
            str_to_print += f' {self.time}'
        if self.permission:
            str_to_print += f' {self.permission}'
        return str_to_print


@dataclass
class Folder:
    folder_details: Optional[File]
    files_details: Optional[list[Union['Folder',File]]]


class CheckFlags:

    @staticmethod
    def conflict_flags() -> dict:
        conflict_flags = {}
        conflict_flags[Flags.one] =  [Flags.zero]
        conflict_flags[Flags.zero] =  [Flags.one, Flags.size, Flags.time, Flags.permission, Flags.long]
        conflict_flags[Flags.all] = []
        conflict_flags[Flags.color] = []
        conflict_flags[Flags.directory] = []
        conflict_flags[Flags.size] = [Flags.zero]
        conflict_flags[Flags.time] = [Flags.zero]
        conflict_flags[Flags.permission] = [Flags.zero]
        conflict_flags[Flags.long] = [Flags.zero]
        conflict_flags[Flags.c] = []
        conflict_flags[Flags.u] = []
        return conflict_flags

    @staticmethod
    def to_flag(name: str)->Flags:
        try:
            return Flags[name]
        except KeyError:
            raise ValueError(f'Unknown flag {name}')

    @staticmethod
    def list_dependant_flags(flags: list[Flags])->list[Flags]:
        dependant_flags = []
        if Flags.size in flags or Flags.time in flags or Flags.permission in flags or Flags.long in flags:
            dependant_flags += [Flags.one]
        if Flags.long in flags:
            dependant_flags += [Flags.size, Flags.time, Flags.permission]
        if Flags.u in flags or Flags.c in flags:
            dependant_flags += [Flags.time]
        return dependant_flags

    def dependant_flags(self, flags: list[Flags])->list[Flags]:
        dependant_flags = self.list_dependant_flags(flags)
        for flag in flags:
            _add = self.check_add_flag(flags, flag)
            if _add:
                dependant_flags.append(self.to_flag(_add.name))
        return dependant_flags

    def return_conflict(self, flags: list[Flags], flag: Flags):
        conflict_flags = self.conflict_flags()
        for _flag in flags:
            if _flag in conflict_flags[flag]:
                        raise ValueError(f'conflict{flag}{_flag}')

    def check_add_flag(self, current_flags: list[Flags],flag: Flags)->Optional[Flags]:
        if flag in current_flags:
            return None
        self.return_conflict(current_flags, flag)
        return flag


class AutoFlags:

        def __init__(self, check_flags: CheckFlags):
            self.check_flags = check_flags

        @staticmethod
        def default_flags() -> list[Flags]:
            return [Flags.color, Flags.zero]

        def get_auto_flags(self, flags: list[Flags]) -> list[Flags]:
            default_flags = self.default_flags()
            conflict_flags = self.check_flags.conflict_flags()
            for key in conflict_flags:
                for flag in default_flags:
                    if flag in conflict_flags[key]:
                        if key in flags:
                            default_flags.remove(flag)
            return default_flags


class Argv:
    def __init__(self, default_flags: AutoFlags, check_flags: CheckFlags):
        self.default_flags = default_flags
        self.check_flags = check_flags

    @staticmethod
    def valid_path(path: str)->bool:
        return Path(path).exists()

    def get_double_dash_flags(self, args: list)->list[Flags]:
        valid_double_flags = []
        input_flags =  list(filter(lambda arg: arg.startswith('--'), args))
        input_flags = list(map(lambda _flag: _flag.replace('-', ''),  input_flags))
        for flag in input_flags:
            in_flag = self.check_flags.to_flag(flag)
            self.check_flags.return_conflict(valid_double_flags, in_flag)
            valid_double_flags.append(in_flag)
        return valid_double_flags

    def get_one_dash_flags(self, args: list)->list[Flags]:
        one_dash_flags = []
        input_flags = list(filter(lambda arg: arg.startswith('-') and arg[1] != '-', args))
        input_flags = list(map(lambda _flag: _flag.replace('-', ''), input_flags))
        for flag in input_flags:
            for letter in flag:
                in_flag =  self.check_flags.to_flag(letter)
                self.check_flags.return_conflict(input_flags, in_flag)
                one_dash_flags.append(in_flag)
        return one_dash_flags

    def get_folder_name(self, path: str)->str:
        if not self.valid_path(path):
            raise ValueError(f'invalid path {path}')
        else:
            return path

    def get_flags(self, argv: list)->list[Flags]:
        current_flags = self.get_one_dash_flags(argv)
        current_flags.extend(self.get_double_dash_flags(argv))
        current_flags.extend(self.check_flags.dependant_flags(current_flags))
        current_flags.extend(self.default_flags.get_auto_flags(current_flags))
        return list(set(current_flags))

    def parse_argv(self, argv: list)->Args:
        if len(argv) > 1 and not argv[-1].startswith("-"):
            path = self.get_folder_name(argv[-1])
        else:
            path = str(Path.cwd())
        argv1 = Args(path=path, flags=self.get_flags(argv))
        return argv1


FILE_ATTRIBUTE_HIDDEN = 0x2

class InfoProvide:

    @staticmethod
    def get_vision_files(path: str)->list[str]:
        visible = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return visible

    @staticmethod
    def only_hidden(path: str)->list[str]:
        hidden = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if  attrs != -1 and (attrs & FILE_ATTRIBUTE_HIDDEN):
                hidden.append(name)
        return hidden

    @staticmethod
    def only_folders(path: str)->list[str]:
        folders = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                folders.append(name)
        return folders

    @staticmethod
    def get_size(path : str)->str:
        st = os.stat(path)
        return f"{st.st_size:}"

    @staticmethod
    def kind_of_time(path : str)->dict:
        st = os.stat(path)
        dt1, dt2, dt3 = time.localtime(st.st_mtime), time.localtime(st.st_ctime), time.localtime(st.st_atime)
        mtime_date_s = time.strftime("%d/%m/%Y", dt1)
        mtime_time_s = time.strftime("%H:%M", dt1)
        ctime_date_s = time.strftime("%d/%m/%Y", dt2)
        ctime_time_s = time.strftime("%H:%M", dt2)
        atime_date_s = time.strftime("%d/%m/%Y", dt3)
        atime_time_s = time.strftime("%H:%M", dt3)
        kind_time = {'mtime': f'[{mtime_date_s}, {mtime_time_s}]', Flags.c: f'[{ctime_date_s}, {ctime_time_s}]',
                     Flags.u: f'[{atime_date_s}, {atime_time_s}]'}
        return kind_time

    @staticmethod
    def get_permission(path : str)->str:
        st = os.stat(path)
        perm = stat.filemode(st.st_mode)
        return f'{perm}'

    @staticmethod
    def time_flags(args: Args) -> Union[Flags.c, Flags.u]:
        if Flags.c in args.flags:
            return Flags.c
        elif Flags.u in args.flags:
            return Flags.u
        return None

    def get_time(self, path : str, flag: Union[Flags.c, Flags.u]=None)->str:
        kind_time = self.kind_of_time(path)
        return kind_time[flag] if flag else kind_time['mtime']

    def provide_files(self, args: Args)->list[str]:
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
            _file = File(filename=name, size=None, time=None, permission=None)
            if Flags.size in args.flags:
                _file.size = self.get_size(full_path)
            if Flags.time in args.flags:
                _file.time = self.get_time(full_path, self.time_flags(args))
            if Flags.permission in args.flags:
                _file.permission = self.get_permission(full_path)
            if os.path.isdir(full_path):
                _folder = Folder(folder_details=_file, files_details=None)
                final_names.append(_folder)
            if not os.path.isdir(full_path):
                final_names.append(_file)
        folder = Folder(files_details = final_names, folder_details=None)
        return folder


class Printing:

    @staticmethod
    def from_folder_to_list(folder: Folder)->list[File]:
        list_files = []
        for name in folder.files_details:
            if isinstance(name, File):
                list_files.append(name)
            elif isinstance(name, Folder):
                list_files.append(name.folder_details)
        return list_files

    @staticmethod
    def print_inline(list_names: list[Union[File, str]], end=' ')->None:
        for f in list_names:
            print(f, end=end)

    @staticmethod
    def paint_folders(list_names, base='.')->list[str]:
        painted = []
        for f in list_names:
            full_path = os.path.join(base, f.filename)
            if os.path.isdir(full_path):
                painted += [f'{Fore.BLUE}{str(f)}{Style.RESET_ALL} ']
            else:
                    painted += [f'{Fore.LIGHTWHITE_EX}{str(f)}{Style.RESET_ALL} ']
        return painted

    @staticmethod
    def format_row(args: Args)->str:
        if Flags.one in args.flags:
            return '\n'
        else:
            return ' '

    def _print(self,args: Args, info: Folder)->None:
        list_fils = self.from_folder_to_list(info)
        end_format = self.format_row(args)
        if Flags.color in args.flags:
            painted = self.paint_folders(list_fils, base=args.path)
            return self.print_inline(painted, end=end_format)
        else:
            return self.print_inline(list_fils, end=end_format)



def main(argv: list)->None:
    check_flags = CheckFlags()
    auto_flags = AutoFlags(check_flags)
    args = Argv(auto_flags, check_flags)
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv(argv)
    _info = info.info_for_print(_args)
    printing._print(_args, _info)

if __name__ == '__main__':
    main(sys.argv)
