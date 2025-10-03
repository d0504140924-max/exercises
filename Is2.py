import os
import sys
import ctypes
import time
from dataclasses import dataclass
from typing import Optional

from colorama import Fore, Style
import stat
from pathlib import Path

FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_SYSTEM   = 0x4



valid_flags = {'-a', '-r', '-l', '-d'}


@dataclass
class FlagsPath:
    path: str=None
    flags: list[str]=None
    another_path: str=None
current_path_flags: FlagsPath = None
@dataclass
class Information:
    info: Optional[list]  = None
    directory: Optional[str] = None
current_info: Information = None




class CheckArgv:
    def __init__(self, argv):
        self.argv = argv

        self.path = ''

    def _path(self):
        for arg in self.argv:
            if not arg.startswith('-'):
                self.path = self.argv
                return self.path
        self.path = '.'
        return self.path

    def get_another_path(self):
        for arg in reversed(self.argv):
            if not arg.startswith('-'):
                specific_file = self.argv[-1]
                return specific_file
        return os.getcwd()


    def syntext_check_argv(self):
        if not isinstance(self.argv, list):
            raise TypeError("argv must be a list")
        if not all(isinstance(a, str) for a in self.argv):
            raise TypeError("all argv items must be strings")


    def check_argv(self):
        for arg in self.argv:
            if self.argv.count(arg) > 1:
                raise TypeError(f"Flag {arg} was sent more than once: ")
        for arg in self.argv:
            if len(arg) < 2 and arg.startswith('-'):
                raise TypeError("Flag is too short ")



    def split_argv(self):
        new_argv = []
        for arg in self.argv:
            if arg.startswith("-"):
                if len(arg) == 2:
                    new_argv.append(arg)
                else:
                    new_argv.extend([f'-{i}' for i in arg[1:]])
        self.argv = new_argv
        for arg in self.argv:
            if arg.startswith('-') and arg not in valid_flags:
                raise TypeError("at least one flag is invalid")
            if '-d' in valid_flags and ('r' in valid_flags or 'l' in valid_flags or 'a' in valid_flags):
                raise TypeError("you entered tow conflicting flags")
        return new_argv

    def list_flags(self):
        return self.argv


    def call_all_func(self):
        self.syntext_check_argv()
        self._path()
        self.get_another_path()
        self.check_argv()
        self.split_argv()
        return FlagsPath(self.path, self.split_argv(), self.get_another_path())




class FilesInfo:
    @staticmethod
    def os_listing(path):
        return os.listdir(path)

    @staticmethod
    def visible_files():
        visible = []
        for name in os.listdir(current_path_flags.path):
            full_path = os.path.join(current_path_flags.path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return visible


    def also_hidden_files(self):
        return self.os_listing(current_path_flags.path)


    def _subfiles(self, list_of_files: list, base=None):
        base = base or current_path_flags.path
        items = []
        for name in list_of_files:
            full_path = os.path.join(base, name)
            if os.path.isdir(full_path):
                sub = self._subfiles(self.os_listing(full_path), full_path)
                items.append([name, sub])
            else:
                items.append(name)
        return items


    def return_according_flags(self):
        a = ('-a' in current_path_flags.flags)
        r = ('-r' in current_path_flags.flags)
        d = ('-d' in current_path_flags.flags)
        if not d:
            base_list = self.also_hidden_files() if a else self.visible_files()
            if r:
                return Information(info=self._subfiles(base_list))
            else:
                return Information(info=base_list)
        else:
            return Information(directory=current_path_flags.another_path)


class Printing:

    @staticmethod
    def _files_details(path_file):
        st = os.stat(path_file)
        dt = time.localtime(st.st_mtime)
        date_s = time.strftime("%d/%m/%Y", dt)
        time_s = time.strftime("%H:%M", dt)
        size_s = f"{st.st_size:,}"
        perm = stat.filemode(st.st_mode)
        return f'[{date_s} {time_s} | {perm}]'

    def final_printing_indent(self, base=None, indent=1):
        l = ('-l' in current_path_flags.flags)
        base = base or current_path_flags.path
        _indent = ' ' * indent
        for item in current_info.info:
            if isinstance(item ,str):
                full = os.path.join(base, item)
                if os.path.isdir(full):
                    line = f"{Fore.BLUE}{item}{Style.RESET_ALL}"
                else:
                    line = f'{Style.RESET_ALL}{item}'
                if l:
                    print(f'{_indent}{line}{self._files_details(full)}')
                else:
                    print(f'{_indent}{line}')
            else:
                folder_name, sub_folder = item
                _full = os.path.join(base, folder_name)
                line = f'{Fore.BLUE + folder_name}{Style.RESET_ALL}'
                if l:
                    print(f'{_indent}{line}{self._files_details(_full)}')
                else:
                    print(f'{_indent}{line}')
                Printing().final_printing_indent(os.path.join(base, folder_name), indent + 4)

    def final_printing_regaler(self, base='.', end=' '):
        base = base or current_path_flags.path
        l = ('-l' in current_path_flags.flags)
        for item in current_info.info:
            foll_path = os.path.join(base, item)
            if os.path.isdir(os.path.join(base,item)):
                line = f'{Fore.BLUE}{item}{Style.RESET_ALL}'
            else:
                line  = f'{Style.RESET_ALL}{item}'
            if l:
                print(f'{line} {self._files_details(foll_path)}')
            else:
                print(line, end=' ')

    def printing(self):
        d = ('-d' in current_path_flags.flags)
        r = ('-r' in current_path_flags.flags)
        if not d:
            if r:
                self.final_printing_indent(current_path_flags.path)
            else:
                self.final_printing_regaler(current_path_flags.path)
        else:
            filename_without_ext = os.path.splitext(os.path.basename(current_info.directory))[0]
            path = Path(current_info.directory)
            filename = path.name
            print(f'{filename_without_ext} {self._files_details(current_info.directory)}')


def main():
    global current_path_flags, current_info
    check = CheckArgv(sys.argv[1:])
    current_path_flags = check.call_all_func()
    info = FilesInfo()
    current_info = info.return_according_flags()
    Printing().printing()
if __name__ == '__main__':
    main()
