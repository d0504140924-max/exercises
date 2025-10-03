"""
Ls
"""
import ctypes
import os
from typing import List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class Flags(Enum):
    a = "all"
    l = "long"
    r = "recursive"
    d = "directory"


@dataclass()
class Command:
    command: str
    flags: list[Flags]


class Parser:

    def parse(self, args: List[str]) -> Command:
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

                    flags.append(Flags(letter))
                else:
                    if letter != "-":
                        raise ValueError(f"Invalid flag: {letter}")
        return flags

    @staticmethod
    def _validate_path(path: str) -> bool:
        return Path(path).exists()

    @staticmethod
    def _validate_flags(flag: str) -> bool:
        return flag in Flags.__members__


class GetInfo:

    def execute_command(self, command: Command) -> None:
        pass

    @staticmethod
    def _check_file_attributes(file_path: str, attribute: int) -> bool:
        return ctypes.windll.kernel32.GetFileAttributesW(file_path) & attribute
