import re

from language_reader import LanguageReader

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
    def __init__(self, type, text, pos) -> None:
        self.type = type
        self.text = text
        self.pos = pos
    
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
        self.language = LanguageReader(rules)

        # initalize TokenTrie
        self.tokentrie = TrieNode()
        for terminal in self.language.terminals:
            self.tokentrie.add(terminal)

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
        if self.ch == "":
            self.ch = ""
        return out

    def lookahead(self) -> Token:
        if self.lookahead_buffer == None:
            self.lookahead_buffer = self.next_token()
        return self.lookahead_buffer

    def next_token(self):

        if self.lookahead_buffer != None:
            out = self.lookahead_buffer
            self.lookahead_buffer = None
            return out

        while self.ch in WHITESPACE:
            self.next_character()
        
        if self.ch in self.tokentrie:
            return self.match_trie()
        
        for family in self.language.families:
            if family[1].match(self.ch):
                return self.match_family(family)
        return Token('eof', '', self.tell())
    
    def match_family(self, family, word=""):
        while family[1].match(word + self.ch):
            word += self.next_character()
            if self.ch == "":
                break
        return Token(family[0], word, self.tell())

    def match_trie(self):
        word = ""
        trie_head = self.tokentrie

        while self.ch in trie_head:
            trie_head = trie_head.children[self.ch]
            word += self.next_character()

        if trie_head.word == word:
            return Token(word, word, self.tell())
        else:
            for family in self.language.families:
                if family[1].match(word):
                    return self.match_family(family, word=word)
            print("something silly happened", word, trie_head.word)

if __name__ == "__main__":
    test = Lexer("language.lang", "test.txt")