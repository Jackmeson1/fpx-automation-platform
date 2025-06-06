import re


class Analyzer:
    def __init__(self, target):
        self.success: bool = False
        self.target = target

    def analyze(self):
        #Base interface
        pass


class TextAnalyzer(Analyzer):
    def __init__(self, target: str, to_find, find_any: bool = False, unexpected: bool = False):
        super().__init__(target)
        self.to_find = to_find   # It could be a pattern string, a regex complied pattern or a list of them
        self.found_texts: list = []
        self.find_any: bool = find_any
        self.unexpected = unexpected
        self.success: bool = True

    def analyze(self, flag=re.M) -> bool:
        if type(self.to_find) is str or type(self.to_find) is re.Pattern:
            pattern_list = [self.to_find]
        elif type(self.to_find) is list:
            pattern_list = self.to_find
        else:
            raise TypeError('Tofind must be string, pattern or list of string/pattern')
        self.success = True
        for p in pattern_list:
            if type(p) is str:
                m = re.search(p, self.target, flag)
            else:
                assert type(p) is re.Pattern
                m = p.search(self.target, flag)
            if m:
                if self.find_any:
                    self.found_texts = [m.group()]
                    if self.unexpected:     # an error (find any; unexpected)/ else expect any in the list
                        self.success = False
                    break
                elif self.unexpected:  # a warning, (find all; unexpected)
                    self.found_texts.append(m.group())
            elif not self.find_any and not self.unexpected:  # the expect pattern which is not found
                missing_pattern: str = p.pattern if type(p) is re.Pattern else p
                self.found_texts.append(missing_pattern)
                self.success = False
                break
        return self.success
