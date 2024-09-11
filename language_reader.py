import re

class Rule:
    def __init__(self, lhs, rhs) -> None:
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self) -> str:
        return f"Rule({self.lhs}, {self.rhs})"


class LanguageReader:
    def __init__(self, language) -> None:

        language_file = open(language, "r")


        self.nonterminals = set()
        self.terminals = set()
        self.families = []
        self.rules = []

        lines = [line for line in language_file.read().split("\n") if line != ""]
        for line in lines:
            if line[:5] == "class":
                break_index = line.index(":")
                name = line[6:break_index]
                rule = line[break_index+1:]
                self.families.append((name, re.compile(rule)))
                continue
            self.nonterminals.add(line.split("->")[0].strip())
        
        for line in lines:
            if line[:5] == "class":
                continue
            parts = line.split("->")
            tokens = [token for token in parts[1].split(" ") if token != ""]
            lhs = parts[0].strip()
            for token in tokens:
                if token in self.nonterminals:
                    continue
                matched = False
                for family in self.families:
                    if token == family[0]:
                        matched = True
                        break
                if matched:
                    continue
                self.terminals.add(token)
            self.rules.append(Rule(lhs, tokens))
            
        print(self.nonterminals, self.terminals, self.families, self.rules)
        language_file.close()