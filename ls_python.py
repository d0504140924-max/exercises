import os
import sys
from dataclasses import dataclass, replace as dc_replace
from pathlib import Path
from enum import Enum
import ctypes
from typing import Optional, Union
from colorama import Style, Fore, init
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
    escape = 'escape text'
    u = 'access time'
    c = 'change time'
    inode = 'file id'
    sort = 'sort='
    S = 'sort by size'
    U = 'default sort'
    t = 'sort time'
    v = 'sort by version'
    X = 'sort by extension'
    width = 'sort by width'
    recursive = 'recursive'
    m = 'zero with ,'
    numericuidgid = 'like -l, but list numeric user and group IDs'
    showcontrolchars = 'show control characters'
    hidecontrolchars = 'hide control characters'
    Q = 'names with quote'
    reverse = 'reverse order'

short_to_long = {
    'a': 'all',
    'd': 'directory',
    's': 'size',
    'l': 'long',
    'b': 'escape',
    'u': 'u',
    'c': 'c',
    'i': 'inode',
    'S': 'S',
    'R': 'recursive',
    'm': 'm',
    'n': 'numericuidgid',
    'q': 'hidecontrolchars',
    'Q': 'Q',
    'r': 'reverse',
    'U': 'U',
    't': 't',
    'v': 'v',
    'X': 'X'}

@dataclass
class Args:
    path: str
    flags: list[Flags]
    parameters: dict[Flags, str]


@dataclass
class File:
    inode: Optional[str]
    full_path: Optional[str]
    filename: str
    size: Optional[str]
    time: Optional[str]
    time_to_sort: Optional[float]
    permission: Optional[str]
    uid_gid: Optional[str]

    def __str__(self)->str:
        str_to_print = ""
        if self.inode:
            str_to_print = f'{self.inode}'
        str_to_print += f'{self.filename}'
        if self.uid_gid:
            str_to_print += f' {self.uid_gid}'
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
        conflict_flags[Flags.one] =  [Flags.zero, Flags.m]
        conflict_flags[Flags.zero] =  [Flags.one, Flags.size, Flags.time, Flags.permission, Flags.long, Flags.recursive,
                                       Flags.numericuidgid, Flags.reverse, Flags.X, Flags.v, Flags.width, Flags.t,
                                       Flags.S, Flags.U]
        conflict_flags[Flags.all] = []
        conflict_flags[Flags.color] = [Flags.escape]
        conflict_flags[Flags.directory] = []
        conflict_flags[Flags.size] = [Flags.zero, Flags.m]
        conflict_flags[Flags.time] = [Flags.zero, Flags.m]
        conflict_flags[Flags.permission] = [Flags.zero, Flags.m]
        conflict_flags[Flags.long] = [Flags.zero, Flags.m]
        conflict_flags[Flags.escape] = [Flags.color, Flags.hidecontrolchars, Flags.Q]
        conflict_flags[Flags.c] = []
        conflict_flags[Flags.u] = []
        conflict_flags[Flags.inode] = []
        conflict_flags[Flags.recursive] = [Flags.zero]
        conflict_flags[Flags.m] = [Flags.one, Flags.size, Flags.time, Flags.permission, Flags.long, Flags.recursive,
                                   Flags.numericuidgid]
        conflict_flags[Flags.numericuidgid] = [Flags.zero, Flags.m]
        conflict_flags[Flags.showcontrolchars] = [Flags.hidecontrolchars]
        conflict_flags[Flags.hidecontrolchars] = [Flags.showcontrolchars, Flags.escape]
        conflict_flags[Flags.Q] = [Flags.escape]
        conflict_flags[Flags.reverse] = [Flags.zero]
        conflict_flags[Flags.U] = [Flags.X, Flags.v, Flags.width, Flags.t, Flags.S, Flags.zero]
        conflict_flags[Flags.X] = [Flags.U, Flags.v, Flags.width, Flags.t, Flags.S, Flags.zero]
        conflict_flags[Flags.v] = [Flags.X, Flags.U, Flags.width, Flags.t, Flags.S, Flags.zero]
        conflict_flags[Flags.width] = [Flags.X, Flags.v, Flags.U, Flags.t, Flags.S, Flags.zero]
        conflict_flags[Flags.t] = [Flags.X, Flags.v, Flags.width, Flags.U, Flags.S, Flags.zero]
        conflict_flags[Flags.S] = [Flags.zero, Flags.X, Flags.v, Flags.width, Flags.U, Flags.t]
        conflict_flags[Flags.sort] = [Flags.zero]
        return conflict_flags

    @staticmethod
    def to_flag(name: str)->Flags:
        try:
            return Flags[name]
        except KeyError:
            raise ValueError(f'Unknown flag {name}')

    def get_flag_to_sort(self, param: str) -> Optional[Flags]:
        if param == 'size':
            return Flags.S
        elif param == 'time':
            return Flags.t
        elif param == 'name':
            return Flags.U
        elif param == 'extension':
            return Flags.X
        elif param == 'version':
            return Flags.v
        elif param == 'width':
            return Flags.width
        else:
            raise ValueError(f'Unknown parameter {param}')

    def collect_dependant(self, flags: set[Flags], params:dict[Flags,str])->list[Flags]:
        current_flags = set(flags)
        if Flags.u in flags or Flags.c in flags:
            flags.add(Flags.time)
        if Flags.S in flags:
            flags.add(Flags.size)
        if Flags.numericuidgid in flags:
            flags.add(Flags.long)
        if Flags.long in flags:
            flags.update([Flags.size, Flags.time, Flags.permission])
        if Flags.size in flags or Flags.time in flags or Flags.permission in flags:
            flags.add(Flags.one)
        if Flags.recursive in flags:
            flags.add(Flags.one)
        if Flags.reverse in flags:
            flags.add(Flags.S)
        if Flags.sort in flags:
            flags.add(self.get_flag_to_sort(params[Flags.sort]))
        if Flags.t in flags:
            flags.add(Flags.time)
        return flags if flags == current_flags else self.collect_dependant(flags, params)

    def list_dependant_flags(self, flags: list[Flags], params: dict[Flags,str])->list[Flags]:
        current_flags = set(flags)
        dependant_flags = self.collect_dependant(set(flags), params)
        return [i for i in dependant_flags if i not in current_flags]

    def dependant_flags(self, flags: list[Flags], params: dict[Flags, str])->list[Flags]:
        dependant_flags = self.list_dependant_flags(flags, params)
        for flag in flags:
            _add = self.check_add_flag(flags, flag)
            if _add:
                dependant_flags.append(self.to_flag(_add.name))
        return dependant_flags

    def return_conflict(self, flags: list[Flags], flag: Flags):
        conflict_flags = self.conflict_flags()
        for _flag in flags:
            if _flag in conflict_flags[flag]:
                        raise ValueError(f'conflict{flag} - {_flag}')

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
            return [Flags.color, Flags.zero, Flags.showcontrolchars]

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

    @staticmethod
    def split_flags_params(args: list[str]):
        flags = []
        for arg in args:
            if '=' in arg:
                flag, param  = arg.split('=')
                flags.append(flag)
            else:
                flags.append(arg)
        return flags

    def get_parameters(self, args: list[str]) -> dict[Flags, str]:
        parameters = {}
        for arg in args:
            if '=' in arg:
                flag, param = arg.split('=')
                parameters[self.check_flags.to_flag(flag[2:])] = param
        return parameters

    def get_double_dash_flags(self, args: list[str])->list[Flags]:
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
                long_flag = short_to_long[letter]
                in_flag =  self.check_flags.to_flag(long_flag)
                self.check_flags.return_conflict(one_dash_flags, in_flag)
                one_dash_flags.append(in_flag)
        return one_dash_flags

    def get_folder_name(self, path: str)->str:
        if not self.valid_path(path):
            raise ValueError(f'invalid path {path}')
        else:
            return path

    def get_flags(self, argv: list[str])->list[Flags]:
        _current_flags = self.split_flags_params(argv)
        current_flags = self.get_one_dash_flags(_current_flags)
        current_flags.extend(self.get_double_dash_flags(_current_flags))
        current_flags.extend(self.check_flags.dependant_flags(current_flags, self.get_parameters(argv)))
        current_flags.extend(self.default_flags.get_auto_flags(current_flags))
        return list(set(current_flags))

    def parse_argv(self, argv: list[str])->Args:
        if len(argv) > 1 and not argv[-1].startswith("-"):
            path = self.get_folder_name(argv[-1])
        else:
            path = str(Path.cwd())
        argv1 = Args(path=path, flags=self.get_flags(argv), parameters=self.get_parameters(argv))
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

    def get_time(self, path : str, flag: Union[Flags.c, Flags.u]=None)->str:
        kind_time = self.kind_of_time(path)
        return kind_time[flag] if flag else kind_time['mtime']

    @staticmethod
    def numeric_time(path: str) -> dict[Union[str, Flags], float]:
        st = os.stat(path)
        return {
            'mtime': st.st_mtime,
            Flags.c: st.st_ctime,
            Flags.u: st.st_atime}

    def get_time_to_sort(self, path : str, flag: Union[Flags.c, Flags.u]=None)->float:
        kind_time = self.numeric_time(path)
        return kind_time[flag] if flag else kind_time['mtime']

    @staticmethod
    def get_permission(path : str)->str:
        st = os.stat(path)
        perm = stat.filemode(st.st_mode)
        return f'{perm}'

    @staticmethod
    def get_inode(path: str)->str:
        st = os.stat(path)
        return f'{st.st_ino}'

    @staticmethod
    def time_flags(args: Args) -> Optional[Union[Flags.c, Flags.u]]:
        if Flags.c in args.flags:
            return Flags.c
        elif Flags.u in args.flags:
            return Flags.u
        return None

    @staticmethod
    def get_uid_gid(path: str)->str:
        try:
            st = os.stat(path, follow_symlinks=True)
            uid = getattr(st, "st_uid", None)
            gid = getattr(st, "st_gid", None)
            return f'{str(uid) if uid is not None else "NA"} {str(gid) if gid is not None else "NA"}'
        except OSError:
            return "NA"

    def provide_files(self,path:str, args: Args)->list[str]:
        if Flags.directory in args.flags:
            names =  self.only_folders(path)
            if Flags.all in args.flags:
                names.extend(self.only_hidden(path))
        else:
            names = self.get_vision_files(path)
            if Flags.all in args.flags:
                names.extend(self.only_hidden(path))
        return names

    def info_to_folder(self, args: Args, names: list)->list[Union[File, Folder]]:
        final_names = []
        for name in names:
            full_path = os.path.join(args.path, name)
            _file = File(inode=None, full_path=full_path, filename=name,uid_gid=None,
                         size=None, time=None, time_to_sort=None, permission=None)
            if Flags.size in args.flags:
                _file.size = self.get_size(full_path)
            if Flags.time in args.flags:
                _file.time = self.get_time(full_path, self.time_flags(args))
                _file.time_to_sort = self.get_time_to_sort(full_path, self.time_flags(args))
            if Flags.permission in args.flags:
                _file.permission = self.get_permission(full_path)
            if Flags.inode in args.flags:
                _file.inode = self.get_inode(full_path)
            if Flags.numericuidgid in args.flags:
                _file.uid_gid = self.get_uid_gid(full_path)
            if os.path.isdir(full_path):
                if Flags.recursive in args.flags:
                    child_args = dc_replace(args, path=full_path, flags=args.flags)
                    _folder = Folder(folder_details=_file,
                                 files_details=self.info_to_folder(child_args, self.provide_files(full_path, args)))
                else:
                    _folder = Folder(folder_details=_file,files_details=None)
                final_names.append(_folder)
            if not os.path.isdir(full_path):
                final_names.append(_file)
        return final_names

    def info_for_print(self, args: Args, names: list)->Folder:
        folder = Folder(files_details = self.info_to_folder(args, names), folder_details=None)
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
    def version_key(name: str)->list:
        parts = num_chunk.split(name)
        for i in range(1, len(parts), 2):
            parts[i] = int(parts[i])
        return parts

    def sort_by_param(self, flags: list[Flags], files: list[File]) -> list[File]:
        reverse = True
        if Flags.reverse in flags:
            reverse = False
        if Flags.S in flags:
            files.sort(key=lambda f: int(f.size), reverse=reverse)
        elif Flags.U in flags:
            files.sort(reverse=reverse)
        elif Flags.t in flags:
            files.sort(key=lambda f: f.time_to_sort, reverse=reverse)
        elif Flags.v in flags:
            files.sort(key=lambda f: self.version_key(f.filename), reverse=reverse)
        elif Flags.X in flags:
            files.sort(key=lambda f: f.filename[-1], reverse=reverse)
        elif Flags.width in flags:
            files.sort(key=lambda f: len(f.filename), reverse=reverse)
        return files

    @staticmethod
    def escape_text(info_str: list[str])->list[str]:
        escape_text = []
        for name in info_str:
            _name = repr(str(name))
            escape_text.append(_name)
        return escape_text

    @staticmethod
    def print_inline(list_names: list[Union[File, str]], end=' ', intend=0)->None:
        _intend = ' ' * intend
        for f in list_names:
            print(f'{_intend}{f}', end=end)

    @staticmethod
    def paint_folders(list_names: list[File], base='.')->list[str]:
        painted = []
        for f in list_names:
            full_path = os.path.join(base, f.filename)
            if os.path.isdir(full_path):
                painted += [f'{Fore.BLUE}{str(f)}{Style.RESET_ALL} ']
            else:
                painted += [f'{Fore.LIGHTWHITE_EX}{str(f)}{Style.RESET_ALL} ']
        return painted

    @staticmethod
    def format_name(flags: list[Flags], name:str)->str:
        out = name
        if Flags.hidecontrolchars in flags:
            out = ''.join(chare if chare.isprintable() else '?' for chare in out)
        if Flags.Q in flags:
            out = f'"{out}"'
        return out

    @staticmethod
    def format_end_row(args: Args)->str:
        if Flags.one in args.flags:
            return '\n'
        else:
            if Flags.m in args.flags:
                return ','
            else:
                return ' '

    def _print(self,args: Args, info: Folder, intend=0)->None:
        list_fils = self.from_folder_to_list(info)
        if Flags.recursive in args.flags:
            for f in info.files_details:
                if isinstance(f, Folder):
                    self._print(args, f, intend=intend+4)
        list_fils = self.sort_by_param(args.flags, list_fils)
        end_format = self.format_end_row(args)
        final_list = []
        if Flags.color in args.flags:
            painted = self.paint_folders(list_fils, base=args.path)
            final_list += painted
        else:
            final_list += list_fils
        if Flags.escape in args.flags:
            final_list = self.escape_text(final_list)
        final_list = [self.format_name(args.flags, i) for i in final_list]
        return self.print_inline(final_list, end=end_format, intend=intend)


def main(argv: list)->None:
    check_flags = CheckFlags()
    auto_flags = AutoFlags(check_flags)
    args = Argv(auto_flags, check_flags)
    info = InfoProvide()
    printing = Printing()
    _args = args.parse_argv(argv)
    to_info = info.provide_files(_args.path, _args)
    _info = info.info_for_print(_args, to_info)
    printing._print(_args, _info)

if __name__ == '__main__':
    init(autoreset=False)
    main(sys.argv)
