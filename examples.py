class GetAutoFlags:

    def get_auto_flags(self, flags: List[Flags]) -> List[Flags]:
        auto_flags = self._dufault_flags()
        auto_flags = list(filter(lambda flag: not self._is_there_curraption(flag, flags), auto_flags))
        return flags + auto_flags


    def _dufault_flags(self) -> Lsit[Flags]:
        return [Flags("color"), Flags("zero")]


    def _is_there_curraption(self, flag: Flags, flags: List[Flags]) -> bool:

        if flag.name == "one":
            if Flags.zero in flags:
                return True

        if flag.name == "zero":
            if Flags.one in flags:
                return True


