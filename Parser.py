from Lexer import Lexer, Token
from language_reader import LanguageReader, Rule
from AST import ParseTree
class Item:
    def __init__(self, rule:Rule, dot) -> None:
        self.rule = rule
        self.dot=dot
    
    def __eq__(self, value: object) -> bool:
        return self.rule == value.rule and self.dot == value.dot
    def __repr__(self) -> str:
        return f"Item({self.rule},{self.dot})"
    def __hash__(self) -> int:
        return hash((self.dot, self.rule))


                
class Parser:
    def __init__(self, lexer:Lexer) -> None:
        self.lexer = lexer
        self.lang = lexer.language

        self.followset = {}

        self.transitions = {}
        self.reductions = {}
        self.compile_rules()


    def follows(self,token):
        if token in self.followset:
            return self.followset[token]
        out = set()
        for rule in self.lang.rules:
            for ind in range(len(rule.rhs)):
                if rule.rhs[ind] != token:
                    continue
                if ind == len(rule.rhs)-1:
                    # if this is a rule that generates its own lhs, it will recur endlessly
                    if rule.lhs == token:
                        continue
                    out.update(self.follows(rule.lhs))
                else:
                    out.update(self.starts(rule.rhs[ind+1]))
        self.followset[token] = out

        return out

    def starts(self, token):

        # nonterminals always start with themselves and only themselves
        if not token in self.lang.nonterminals:
            return {token}
        out = set()

        for rule in self.lang.rules:
            if rule.lhs != token:
                continue

            if len(rule.rhs) == 0:
                continue
            
            # Don't infinitely recur
            if rule.rhs[0] == token:
                continue
            out.update(self.starts(rule.rhs[0]))
        return out

    def compile_rules(self):
        # TODO: determine starting token properly
        rule_0 = Rule("", [self.lang.rules[0].lhs, "eof"])
        self.lang.rules.append(rule_0)
        self.lang.terminals.add("eof")
        

        sets = [{Item(rule_0, 0)}]
        sets[0]=self.close_set(sets[0])
        i = 0
        while i < len(sets):
            for token in {t.rule.rhs[t.dot] for t in sets[i] if t.dot != len(t.rule.rhs)}:
                new_set = set()
                for item in sets[i]:
                    if item.dot < len(item.rule.rhs) and item.rule.rhs[item.dot] == token:
                        new_set.add(Item(item.rule, item.dot+1))
                new_set = self.close_set(new_set)
                if new_set not in sets:
                    sets.append(new_set)
                self.transitions[(i, token)] = sets.index(new_set)
            i += 1


        self.reductions = self.calculate_reductions(sets)
        
        self.accepting = self.find_accepting(sets)

        for i in range(len(sets)):
            print(f"Set {i}:")
            for item in sets[i]:
                print(item, "Reducing" if len(item.rule.rhs) == item.dot else "")

    # any sets with an item of the form A->w dot are reductions
    # since this is a slr parser, we also add a check to only reduce if
    # the lookahead token matches 
    def calculate_reductions(self, sets):
        reductions = {}
        for i in range(len(sets)):
            for item in sets[i]:
                if len(item.rule.rhs) == item.dot:
                    for token in self.lang.terminals:
                        if token in self.follows(item.rule.lhs):
                            reductions[(i, token)] = item.rule
        return reductions
 
    def find_accepting(self, sets):
        for ind in range(len(sets)):
            if Item(self.lang.rules[-1], 2) in sets[ind]:
                print(f"state {ind} is accepting")
                return ind
        raise Exception("Did not find accepting set")

    # returns the closure of the set
    def close_set(self, old_set:set[Item]):
        modified = False
        # copy made since you should not change an iterable while iterating over it
        new_set = old_set.copy()
        for item in old_set:
            if item.dot == len(item.rule.rhs):
                continue
            if item.rule.rhs[item.dot] not in self.lang.nonterminals:
                continue
            terminal = item.rule.rhs[item.dot]
            for rule in self.lang.rules:
                if rule.lhs == terminal:
                    new_item = Item(rule, 0)
                    if new_item not in old_set:
                        modified = True
                    new_set.add(new_item)
        if modified:
            return self.close_set(new_set)
        return new_set


    def parse(self) -> ParseTree:
        states = [0]
        tokenstack = []
        while True:
            if states[-1] == self.accepting and self.lexer.lookahead().type == "eof":
                print("accepted")
                return tokenstack[0]
            if (states[-1], self.lexer.lookahead().type) in self.reductions:

                rule = self.reductions[(states[-1], self.lexer.lookahead().type)]
                rule_len = len(rule.rhs)


                popped_tokens = []
                for x in range(rule_len):
                    popped_tokens.append(tokenstack.pop())
                popped_tokens.reverse()


                tokenstack.append(ParseTree(popped_tokens, self.lang.rules.index(rule)))
                
                for x in range(rule_len):
                    states.pop()
                new_state = self.transitions[(states[-1], rule.lhs)]
                states.append(self.transitions[(states[-1], rule.lhs)])
                print(f"Applying reduction with {rule}, transitioning to {new_state}")
            else:
                token = self.lexer.next_token()
                new_state = self.transitions[(states[-1], token.type)]
                print(f"saw {token}, shifting to {new_state}")
                tokenstack.append(token)
                states.append(new_state)
        



if __name__ == "__main__":
    test = Parser(Lexer("while.lang", "WhileTest.txt"))
    program = test.parse().simplify()
    program.execute({})