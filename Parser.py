from Lexer import Lexer, Rule

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
        self.transitions = {}
        self.reductions = {}
        self.compile_rules()


    def follows(self,token):
        out = set()
        for rule in self.lexer.rules:
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

        return out

    def starts(self, token):

        # nonterminals always start with themselves and only themselves
        if not token in self.lexer.nonterminals:
            return {token}
        out = set()

        for rule in self.lexer.rules:
            if rule.lhs != token:
                continue

            # Don't infinitely recur
            if len(rule.rhs) == 0 or rule.rhs[0] == token:
                continue
            out.update(self.starts(rule.rhs[0]))
        return out

    def compile_rules(self):
        # TODO: determine starting token properly
        rule_0 = Rule("", [self.lexer.rules[0].lhs, "eof"])
        self.lexer.rules.append(rule_0)
        self.lexer.terminals.add("eof")
        

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


        self.calculate_reductions(sets)
        
        for i in range(len(sets)):
            print(f"Set {i}:")
            for item in sets[i]:
                print(item, "Reducing" if len(item.rule.rhs) == item.dot else "")
        # print(self.transitions)
        # print(self.reductions)

    def calculate_reductions(self, sets):
        for i in range(len(sets)):
            for item in sets[i]:
                if len(item.rule.rhs) == item.dot:
                    for token in self.lexer.terminals:
                        if token in self.follows(item.rule.lhs):
                            self.reductions[(i, token)] = item.rule
 


    def close_set(self, old_set:set[Item]):
        modified = False
        new_set = old_set.copy()
        for item in old_set:
            if item.dot == len(item.rule.rhs):
                continue
            if item.rule.rhs[item.dot] not in self.lexer.nonterminals:
                continue
            terminal = item.rule.rhs[item.dot]
            for rule in self.lexer.rules:
                if rule.lhs == terminal:
                    new_item = Item(rule, 0)
                    if new_item not in old_set:
                        modified = True
                    new_set.add(new_item)
        if modified:
            return self.close_set(new_set)
        return new_set


    def parse(self):
        states = [0]
        while True:
            if (states[-1], self.lexer.lookahead().type) in self.reductions:
                rule = self.reductions[(states[-1], self.lexer.lookahead().type)]
                if rule.lhs == "":
                    # TODO: properly mark final state
                    return
                for x in range(len(rule.rhs)):
                    states.pop()
                new_state = self.transitions[(states[-1], rule.lhs)]
                states.append(self.transitions[(states[-1], rule.lhs)])
                print(f"Applying reduction with {rule}, transitioning to {new_state}")
            else:
                token = self.lexer.next_token()
                new_state = self.transitions[(states[-1], token.type)]
                print(f"saw {token}, shifting to {new_state}")
                
                states.append(new_state)



if __name__ == "__main__":
    test = Parser(Lexer("test_lang.lang", "test.txt"))
    test.parse()