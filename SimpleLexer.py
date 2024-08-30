from enum import Enum, auto

class TokenType(Enum):
    CONSTANT = auto()
    SUM_OP = auto()
    PROD_OP = auto()

class Token:
    def __init__(self, text:str, _type:TokenType) -> None:
        self.text = text
        self.type = _type

class Lexer:
    def __init__(self, filename) -> None:
        self.tokens = [
            Token("1", TokenType.CONSTANT),
            Token("*", TokenType.PROD_OP),
            Token("2", TokenType.CONSTANT),
            Token("+", TokenType.SUM_OP),
            Token("1", TokenType.CONSTANT),
        ]
        self.index = 0

    def next_token(self):
        out = self.tokens[self.index]
        self.index += 1
        return out