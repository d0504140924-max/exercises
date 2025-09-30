import os
import sys
import ctypes
from colorama import Fore, Style, init

FILE_ATTRIBUTE_HIDDEN = 0x2

def is_hidden(filepath):
    attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
    return (attrs != -1) and bool(attrs & FILE_ATTRIBUTE_HIDDEN)

ot_hidden = [f for f in os.listdir() if not is_hidden(f)]


def files_and_folders(lst, base='.'):
    for f in lst:
        full_path = os.path.join(base, f)
        if os.path.isdir(full_path):
            print(Fore.BLUE + f, end=' ')
        else:
            print(Style.RESET_ALL + f, end=' ')

init(autoreset=True)
def os_list(path = '.'):
    return os.listdir(path)

def check_argv():
    path = '.'
    result = os_list(path)
    if len(sys.argv) == 2:
        if sys.argv[1] == '-a':
            files_and_folders(result)
        elif sys.argv[1] == '-r':
            for f in result:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    sub_result = os_list(full_path)
                    print(Fore.RED + 'this is a subfolder')
                    files_and_folders(sub_result, full_path)
        else:
            not_hidden = [f for f in os.listdir() if not is_hidden(f)]
            files_and_folders(not_hidden)
    elif len(sys.argv) == 3:
        if sys.argv[1] == '-a' or sys.argv[2] == '-a':
            files_and_folders(result)
            if sys.argv[1] == '-r' or sys.argv[2] == '-r':
                for f in result:
                    full_path = os.path.join(path, f)
                    if os.path.isdir(full_path):
                        sub_result = os_list(full_path)
                        print(Fore.RED + 'this is a subfolder')
                        files_and_folders(sub_result, full_path)
        elif sys.argv[1] == '-r' or sys.argv[2] == '-r':
            for f in result:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    sub_result = os_list(full_path)
                    print(Fore.RED + 'this is a subfolder')
                    files_and_folders(sub_result, full_path)
        else:
            not_hidden = [f for f in os.listdir() if not is_hidden(f)]
            files_and_folders(not_hidden)
    else:
        not_hidden = [f for f in os.listdir() if not is_hidden(f)]
        files_and_folders(not_hidden)



check_argv()

