import os
import sys
import ctypes
import time
from dataclasses import dataclass
from enum import Enum
from colorama import Fore, Style
import stat


FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_SYSTEM   = 0x4


class Flags(Enum):
    a = 'hidden files'
    r = 'recursion'
    l = 'details'


@dataclass
class FlagsPath:
    path: str
    flags: list[str]


class CheckArgv:
    def __init__(self, argv):
        self.argv = argv
        self.new_argv = []
        self.path = ''

    def _path(self):
        for a in self.argv:
            if not a.startswith('-'):
                self.path = a
                return self.path
        self.path = '.'
        return self.path

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
        self.new_argv = []
        for arg in self.argv:
            if arg.startswith("-"):
                if len(arg) == 2:
                    self.new_argv.append(arg)
                else:
                    self.new_argv.extend([f'-{i}' for i in arg[1:]])
        self.argv = self.new_argv
        #for arg in self.new_argv:
            #if arg.startswith('-') and arg not in Flags:
                #raise TypeError("at least one flag is invalid")

    def list_flags(self):
        return self.new_argv


    def call_all_func(self):
        self.syntext_check_argv()
        self._path()
        self.check_argv()
        self.split_argv()
        return FlagsPath(self.path, self.list_flags())




class FilesInfo:
    def __init__(self, flags_path: FlagsPath):

        self.flags_path = flags_path
        self.subfiles = []
        self.files_details = []
    @staticmethod
    def os_listing(path):
        return os.listdir(path)

    def visible_files(self):
        visible = []
        for name in os.listdir(self.flags_path.path):
            full_path = os.path.join(self.flags_path.path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(name)
        return visible

    def also_hidden_files(self):
        return self.os_listing(self.flags_path.path)


    def _subfiles(self, list_of_files: list, base=None):
        base = base or self.flags_path.path
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
        a = ('-a' in self.flags_path.flags)
        r = ('-r' in self.flags_path.flags)


        base_list = self.also_hidden_files() if a else self.visible_files()
        if r:
            return self._subfiles(base_list)
        else:
            return base_list


class Printing:
    def __init__(self,flags_path: FlagsPath, final_files_info: list):
        self.final_files_info = final_files_info
        self.flags_path = flags_path

    def _files_details(self, path_file):
        st = os.stat(path_file)
        dt = time.localtime(st.st_mtime)
        date_s = time.strftime("%d/%m/%Y", dt)
        time_s = time.strftime("%H:%M", dt)
        size_s = f"{st.st_size:,}"
        perm = stat.filemode(st.st_mode)
        return f'[{size_s:>8} | {date_s} {time_s} | {perm}]'

    def final_printing_indent(self, base=None, indent=1):
        l = ('-l' in self.flags_path.flags)
        base = base or self.flags_path.path
        _indent = ' ' * indent
        for item in self.final_files_info:
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
                Printing(self.flags_path, sub_folder).final_printing_indent(os.path.join(base, folder_name), indent + 4)

    def final_printing_regaler(self, base='.', end=' '):
        base = base or self.flags_path.path
        l = ('-l' in self.flags_path.flags)
        for item in self.final_files_info:
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
        r = ('-r' in self.flags_path.flags)
        if r:
            self.final_printing_indent(self.flags_path.path)
        else:
            self.final_printing_regaler(self.flags_path.path)



def main():
    check = CheckArgv(sys.argv[1:])
    _checked_items = check.call_all_func()
    info = FilesInfo(_checked_items)
    files_info = info.return_according_flags()
    Printing(_checked_items, files_info).printing()
if __name__ == '__main__':
    main()
