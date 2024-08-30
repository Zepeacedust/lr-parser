from enum import Enum, auto
from SimpleLexer import Lexer
class ActionTypes(Enum):
    SHIFT = auto()
    REDUCE = auto()

class Action():
    def __init__(self, type, value) -> None:
        self.type = type
        self.value = value

class Parser:
    def __init__(self, filename) -> None:
        self.lexer = Lexer(filename)
        self.states = []
        self.tokens = []
        self.action_table = {}
        self.goto_table = {}
        self.rules = []

    def tick(self):
        