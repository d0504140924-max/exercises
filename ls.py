"""
Ls
"""
import ctypes
import os
import stat
import sys
import time
from typing import List, Union, Dict
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from colorama import Fore, Style


FILE_SYS = Dict[str, list[Union[str, Dict]]]


class Flags(Enum):
    a = "all"
    l = "long"
    r = "recursive"
    d = "directory"
    c = "color"


@dataclass()
class Command:
    path: str
    flags: list[Flags]


class Parser:

    def parse_user_command(self, args: List[str]) -> Command:
        path = self._extract_current_path(args)
        flags = self._extract_flags(args)
        return Command(path, flags)

    def _extract_current_path(self, args: List[str]) -> str:
        if len(args) > 1 and not args[-1].startswith("-"):

            if not self._validate_path(args[-1]):
                raise ValueError(f"Invalid path: {args[-1]}")

            return args[-1]
        else:
            return os.getcwd()

    def _extract_flags(self, args: List[str]) -> List[Flags]:
        flags = []
        pre_flags = filter(lambda arg: arg.startswith("-"), args)
        for flag in pre_flags:
            for letter in flag:
                if letter.isalpha():
                    if not self._validate_flags(letter):
                        raise ValueError(f"Invalid flag: {letter}")

                    flags.append(Flags.__getitem__(letter))
                else:
                    if letter != "-":
                        raise ValueError(f"Invalid flag: {letter}")

        flags += self._get_auto_flags()

        return flags

    @staticmethod
    def _get_auto_flags() -> List[Flags]:
        return [Flags("color")]

    @staticmethod
    def _validate_path(path: str) -> bool:
        return Path(path).exists()

    @staticmethod
    def _validate_flags(flag: str) -> bool:
        return flag in Flags.__members__


class GetInfo:

    def execute_command(self, command: Command) -> FILE_SYS:

        self.check_validation_flags(command.flags)
        self.check_validation_path(command.path)

        if Flags.r in command.flags:
            return self.recursive(command)
        elif Flags.d in command.flags:
            return self.directory(command)
        else:
            return self.regular(command)

    def regular(self, command: Command) -> FILE_SYS:
        files = self._get_list_dir(command)
        return {command.path: files}


    def recursive(self, command: Command) -> FILE_SYS:
        files = {command.path: []}
        for path in list(self._get_list_dir(command)):
            if os.path.isdir(path):
                new_command = Command(path, command.flags)
                files[command.path].append(self.recursive(new_command))
            else:
                files[command.path].append(path)
                return files
        return files

    def directory(self, command: Command) -> FILE_SYS:
        command.flags.append(Flags.l)
        command.flags.remove(Flags.c)
        return {command.path: [command.path]}

    def _get_list_dir(self, command: Command) -> List[str]:
        if os.path.isdir(command.path):
            if Flags.a in command.flags:
                files = os.listdir(command.path)
                files = self._remove_not_exists(command.path, files)
                self._add_reference_folders(files)
            else:
                files = list(filter(lambda f: not self._check_file_attributes(f, 0x2), os.listdir(command.path)))
            return list(sorted(files))

        raise FileNotFoundError(command.path)

    @staticmethod
    def _check_file_attributes(file_path: str, attribute: int) -> bool:
        return ctypes.windll.kernel32.GetFileAttributesW(file_path) & attribute

    @staticmethod
    def _remove_not_exists(path: str, files: List[str]) -> List[str]:
        return list(filter(lambda file: os.stat(os.path.join(path, file)), files))

    @staticmethod
    def _add_reference_folders(files: List[str]) -> None:
        files.append(".")
        files.append("..")

    @staticmethod
    def check_validation_flags(flags: List[Flags]) -> bool:
        if Flags.r in flags and Flags.d in flags: return False
        if Flags.d in flags and Flags.a in flags: return False
        return True

    @staticmethod
    def check_validation_path(path: str) -> bool:
        return os.path.exists(path)


class Printer:

    intented = 4

    def print(self, file_sys: FILE_SYS, command: Command) -> None:
        self.print_folder(file_sys, 0, command)

    def print_folder(self, folder: FILE_SYS, depth: int, command) -> None:
        files = list(folder.values())[0]
        for file in files:
            if isinstance(file, str):
                file = self._get_file_info(Command(file, command.flags))
                print(f"{file}", end="")
            else:
                print(f"{list(file.keys())[0]}")
                self.print_folder(file, depth + 1, command)

    def _get_file_info(self, command: Command) -> str:
        file_info = ""

        if Flags.c in command.flags:
            file_info += f"{self.color_file(command.path)} "
        else:
            file_info += f"{command.path:}"

        if Flags.l in command.flags:
            file_info = f"{file_info:<24}"
            file_info += f"{self._get_file_stamp(command.path):<20}"
            file_info += f"{self._get_file_permissions(command.path):>20}"
            file_info += f"{self._get_file_size(command.path):>20}"
            file_info += "\n"

        return file_info

    def color_file(self, path: str) -> str:
        if os.path.isdir(path):
            return Fore.BLUE + path + Style.RESET_ALL
        return Fore.LIGHTWHITE_EX + path + Style.RESET_ALL

    @staticmethod
    def _get_file_stamp(file_path: str) -> str:
        return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(os.stat(file_path).st_mtime))

    @staticmethod
    def _get_file_permissions(file_path: str) -> str:
        return stat.filemode(os.stat(file_path).st_mode)

    @staticmethod
    def _get_file_size(file_path: str) -> str:
        return str(os.stat(file_path).st_size)

if __name__ == '__main__':
    parser = Parser()
    get_info = GetInfo()
    printer = Printer()

    command = parser.parse_user_command(sys.argv)
    files = get_info.execute_command(command)
    printer.print(files, command)