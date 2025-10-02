import os
import sys
import ctypes
import time
from dataclasses import dataclass
from enum import Enum
from colorama import Fore, Style
import stat


def os_listing(path):
    return os.listdir(path)

FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_SYSTEM   = 0x4
def without_hidden_files(filepath):#this function prints only visible files
    attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
    return (attrs != -1) and bool(attrs & FILE_ATTRIBUTE_HIDDEN)


class Flags(Enum):
    -a = 'hidden files'
    -r = 'recursion'
    -l = 'details'


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
        self.path =  self.path + self.argv[0]
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
            if len(arg) < 2:
                raise TypeError("Flag is too short ")
        if not (i for i in self.argv) in Flags:
            raise TypeError("at least one flag is invalid")


    def split_argv(self):
        for arg in self.argv:
            if arg.startswith("-"):
                if len(arg) == 2:
                    self.new_argv.append(arg)
                else:
                    self.new_argv.extend([f'-{i}' for i in arg[1:]])
        self.argv = self.new_argv

    def list_flags(self):
        return self.new_argv


    def call_all_func(self):
        self.syntext_check_argv()
        self.check_argv()
        self.split_argv()
        return FlagsPath(self._path(), self.list_flags())




class FilesInfo:
    def __init__(self, flags_path: FlagsPath):

        self.flags_path = flags_path
        self.subfiles = []
        self.files_details = []

    def visible_files(self):
        visible = []
        for name in os.listdir(self.flags_path.path):
            full_path = os.path.join(self.flags_path.path, name)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(full_path))
            if attrs != -1 and not (attrs & FILE_ATTRIBUTE_HIDDEN):
                visible.append(full_path)
        return visible

    def also_hidden_files(self):
        return os_listing(self.flags_path.path)


    def _subfiles(self, list_of_files: list, base='.'):
        items = []
        for name in list_of_files:
            full_path = os.path.join(base, name)
            if os.path.isdir(full_path):
                sub = self._subfiles(os_listing(full_path), full_path)
                items.append([name, sub])
            else:
                items.append(name)
        return items

    def _files_details(self, list_of_files, base='.'):

        for name in list_of_files:
            details = []
            full_path = os.path.join(base, name)
            if name is not str:
                self._files_details(name)
            else:
                st = os.stat(full_path)
                dt = time.localtime(st.st_mtime)
                date_s = time.strftime("%d/%m/%Y", dt)
                time_s = time.strftime("%H:%M", dt)
                size = st.st_size
                perm = stat.filemode(st.st_mode)
                details.append([full_path, size, date_s, time_s, perm, name])
        return details

    def return_according_flags(self):
        a = ('-a' in self.flags_path.flags)
        r = ('-r' in self.flags_path.flags)
        l = ('-l' in self.flags_path.flags)
        if not a and not r and not l:
            return self.visible_files()
        elif a and not r and not l :
            return self.also_hidden_files()
        elif r and not a and not l:
            lst = self.visible_files()
            return self._subfiles(lst)
        elif l and not a and not r:
            lst = self.visible_files()
            return self._files_details(lst)
        elif a and r and not l:
            lst = self.also_hidden_files()
            return self._files_details(lst)
        elif a and l and not r:
            lst = self.also_hidden_files()
            return self._files_details(lst)
        elif r and l and not a:
            lst = self.visible_files()
            lst2 = self._subfiles(lst)
            return self._files_details(lst2)
        elif a and r and l:
            lst = self.also_hidden_files()
            lst2 = self._subfiles(lst)
            return self._files_details(lst2)


class Printing:
    def __init__(self,flags_path: FlagsPath, final_files_info: list):
        self.final_files_info = final_files_info
        self.flags_path = flags_path

    def final_printing_indent(self, base='.'):
        for item in self.final_files_info:
            if item is str:
                if os.path.isdir(item):
                    print(f"{Fore.BLUE + item}\n\t")
                else:
                    print(Style.RESET_ALL + item)
            else:
                self.final_printing_indent('.')

    def final_printing_regaler(self, base='.', end=' '):
        for item in self.final_files_info:
            if item is str:
                if os.path.isdir(item):
                    print(f"{Fore.BLUE + item}", end=end)
                else:
                    print(Style.RESET_ALL + item, end=end)
            else:
                self.final_printing_regaler('.',' ')

    def printing(self):
        a = ('-a' in self.flags_path.flags)
        if a:
            self.final_printing_indent()
        else:
            self.final_printing_regaler()



def main():

    check = CheckArgv(sys.argv)
    _checked_items = check.call_all_func()
    info = FilesInfo(_checked_items)
    files_info = info.return_according_flags()
    Printing(_checked_items, files_info)
