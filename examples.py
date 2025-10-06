"""
הקוד הזה דבר ראשון הרבהיותר קריא
דבר שני תראה שבפונקציה פה לא התעסקתי כמעט עם שום מימוש שזה דבר טוב
(למשל הcon[0] שלך וכדומה שזה לא טוב)
וגם זה מאוד גנרי ותשים לב שאני כמעט לא תלוי בשום חלק אחר
"""
import os.path

def get_double_dash_flags(self, args: Lsit[str]) -> List[Flags]:

    flags = []
    pre_flags = list(filter(lambda flag: flag.startwith("--"), args))
    pre_flags = list(map(lambda flag: flag.rplace("--", ""), pre_flags))
    for flag in pre_flags:
        flag = self.create_flag(flag)
        self.check_for_conflict(flag, flags)
        flags.append(flag)


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
        if os.path.isfile(full_path):
            file = self.et_file(full_path, args)
            folder.files.append(file)
        elif os.path.isdir(full_path):
            sub_folder = self.create_folder(full_path, args)
            folder.files.append(sub_folder)

    return folder


