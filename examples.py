"""
הקוד הזה דבר ראשון הרבהיותר קריא
דבר שני תראה שבפונקציה פה לא התעסקתי כמעט עם שום מימוש שזה דבר טוב
(למשל הcon[0] שלך וכדומה שזה לא טוב)
וגם זה מאוד גנרי ותשים לב שאני כמעט לא תלוי בשום חלק אחר
"""

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

    return flasg
