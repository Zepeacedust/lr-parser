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
        self.compile_rules()

    def compile_rules(self):
        # TODO: determine starting token properly
        rule_0 = Rule("", [self.lexer.rules[0].lhs, "eof"])
        self.lexer.rules.append(rule_0)
        
        
        sets = [{Item(rule_0, 0)}]
        sets[0]=self.close_set(sets[0])
        i = 0
        while i < len(sets):
            for token in {t.rule.rhs[t.dot] for t in sets[i]}:
                print(token)
                new_set = set()
                for item in sets[i]:
                    if item.rule.rhs[item.dot] == token:
                        new_set.add(Item(item.rule, item.dot+1))
                sets.append(self.close_set(new_set))
            i += 1


        for i in range(len(sets)):
            print(f"Set {i}:")
            for item in sets[i]:
                print(item)

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

if __name__ == "__main__":
    test = Parser(Lexer("language.lang", "test.txt"))