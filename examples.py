"""
הקוד הזה דבר ראשון הרבהיותר קריא
דבר שני תראה שבפונקציה פה לא התעסקתי כמעט עם שום מימוש שזה דבר טוב
(למשל הcon[0] שלך וכדומה שזה לא טוב)
וגם זה מאוד גנרי ותשים לב שאני כמעט לא תלוי בשום חלק אחר
"""
import os.path

from ls import Flags


def get_double_dash_flags(self, args: Lsit[str]) -> List[Flags]:

    flags = []
    pre_flags = list(filter(lambda flag: flag.startwith("--"), args))
    pre_flags = list(map(lambda flag: flag.rplace("--", ""), pre_flags))
    for flag in pre_flags:
        if self.is_valid_flag(flag):
            self.check_for_conflict(flag, flags)
            flags.append(flag)
        else:
            raise ValueError(f"Invalid flag {flag}")

    return flags

"""
קודם תיצור את התיקיה ואז תקבל את כל הקבצים שלה
ולכל קובץ תקבל את כל התנונים שלו
ואז תוסיף אותו לתיקייה
"""



def info_for_print(self, args: Argv) -> Folder:

    folder = Folder(name=args.name)
    files = self.provide_files(folder.name)
    for file in files:
        full_path = os.path.join(folder.name, file)
        file_size = self.get_size(full_path) if Flags.size in args.flags else None
        time_stamp = self.get_time_stamp(full_path) if Flags.time_stamp in args.flags else None
        permission = self.get_permission(full_path) if Flags.permission in args.flags else None
        file = File(name=file, size=file_size, time_stamp=time_stamp, permission=permission)
        folder.files.append(file)

    return folder


