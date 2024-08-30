import re

WHITESPACE = [
    " ",
    "\n",
    "\t",
    ]

class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.word = ""

    def add(self, word, part = 0):
        if len(word) == part:
            self.word = word
            return
        if word[part] not in self.children:
            self.children[word[part]] = TrieNode()
        self.children[word[part]].add(word, part+1)
    
    def __contains__(self, item):
        return item in self.children


class Token:
    def __init__(self,type, text) -> None:
        self.type = type
        self.text = text
    
    def __repr__(self) -> str:
        return f"Token({self.type}, {self.text})"

class Rule:
    def __init__(self, lhs, rhs) -> None:
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self) -> str:
        return f"Rule({self.lhs}, {self.rhs})"

class Lexer:
    def __init__(self, rules, text) -> None:    
        self.terminals = set()
        self.nonterminals = set()
        self.families = []
        self.rules:list[Rule] = []

        self.tokentrie = TrieNode()

        with open(rules, "r") as rule_file:
            self.compile_rules(rule_file)

        self.ch:str = ''
        self.file = open(text, "r")
        self.line = 0
        self.char = 0
        self.next_character()
        self.lookahead_buffer = None
    
    def tell(self):
        return (self.line, self.char)
    
    def next_character(self) -> str:
        out = self.ch
        self.char += 1
        if out == "\n":
            self.char = 0
            self.line += 1
        self.ch = self.file.read(1)
        return out

    def lookahead(self) -> Token:
        if self.lookahead_buffer == None:
            self.lookahead_buffer = self.next_token()
        return self.lookahead_buffer

    def compile_rules(self, rule_file):
        lines = [line for line in rule_file.read().split("\n") if line != ""]
        for line in lines:
            print(line[:5])
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
                    if family[1].match(token) or token == family[0]:
                        matched = True
                        break
                if matched:
                    continue
                self.terminals.add(token)
            self.rules.append(Rule(lhs, tokens))

        for terminal in self.terminals:
            self.tokentrie.add(terminal)

        print(self.nonterminals, self.terminals, self.families, self.rules)

    def next_token(self):
        while self.ch in WHITESPACE:
            self.next_character()
        
        for family in self.families:
            if family[1].match(self.ch):
                return self.match_family(family)
        if self.ch in self.tokentrie:
            return self.match_trie()
        
    def match_family(self, family):
        word = ""
        while family[1].match(word + self.ch):
            word += self.next_character()
        return Token(family[0], word)

    def match_trie(self):
        word = ""
        trie_head = self.tokentrie

        while self.ch in trie_head:
            trie_head = trie_head.children[self.ch]
            word += self.next_character()

        if trie_head.word == word:
            return Token(word, word)
        else:
            print("something silly happened", word, trie_head.word)


if __name__ == "__main__":
    test = Lexer("language.lang", "test.txt")
    print(test.next_token())
    print(test.next_token())
    print(test.next_token())