from Lexer import Token

class ParseTree:
    def __init__(self, comp, rule) -> None:
        self.comp = comp
        self.rule = rule
    def pprint(self, indentation):
        for component in self.comp:
            if isinstance(component, Token):
                print(" " * indentation + component.text)
            else:
                if len(self.comp) == 1:
                    component.pprint(indentation)
                else:
                    component.pprint(indentation+1)
    def simplify(self):
        # Brutish solution, must find more elegant
        if self.rule == 0:#Statements -> Statements Statements;
            return Statement(self.comp[1].pos, self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 1:#Statements -> 
            return None
        if self.rule == 2:#Statement -> Expression
            return self.comp[0].simplify()
        if self.rule == 3:#Statement -> while ( Expression ) { Statements }
            return WhileStmt(self.comp[0].pos, self.comp[2].simplify(), self.comp[5].simplify())
        if self.rule == 4:#Statement -> If ( Expression ) { Statements } Else
            return IfStmt(self.comp[0].pos, self.comp[2].simplify(), self.comp[5].simplify(), self.comp[7].simplify())
        if self.rule == 5:#Statement -> Type identifier = Expression
            return DeclarationStmt(self.comp[0].pos, self.comp[0].text, self.comp[1].text, self.comp[3].simplify())
        if self.rule == 6:#Statement -> identifier = Expression
            return AssignmentStmt(self.comp[0].pos, self.comp[0].text,self.comp[2].simplify())
        if self.rule == 7:#Statement -> print Expression
            return PrintStmt(self.comp[0].pos, self.comp[1].simplify())
        if self.rule == 8:#Else -> else { Statements }
            return self.comp[2].simplify()
        if self.rule == 9:#Else -> 
            return None
        if self.rule == 10:#Expression -> Expression or BooleanExpression
            return BinOp(self.comp[1].pos, "or", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 11:#Expression -> BooleanExpression
            return self.comp[0].simplify()
        if self.rule == 12:#BooleanExpression -> BooleanExpression and CompExpression
            return BinOp(self.comp[1].pos, "and", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 13:#BooleanExpression -> CompExpression
            return self.comp[0].simplify()
        if self.rule == 14:#CompExpression -> SumExpression == SumExpression
            return BinOp(self.comp[1].pos, "==", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 15:#CompExpression -> SumExpression != SumExpression
            return BinOp(self.comp[1].pos, "!=", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 16:#CompExpression -> SumExpression <= SumExpression
            return BinOp(self.comp[1].pos, "<=", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 17:#CompExpression -> SumExpression < SumExpression
            return BinOp(self.comp[1].pos, "<", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 18:#CompExpression -> SumExpression >= SumExpression
            return BinOp(self.comp[1].pos, ">=", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 19:#CompExpression -> SumExpression > SumExpression
            return BinOp(self.comp[1].pos, ">", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 20:#CompExpression -> SumExpression
            return self.comp[0].simplify()
        if self.rule == 21:#SumExpression -> SumExpression + ProdExpression
            return BinOp(self.comp[1].pos, "+", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 22:#SumExpression -> SumExpression - ProdExpression
            return BinOp(self.comp[1].pos, "-", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 23:#SumExpression -> ProdExpression
            return self.comp[0].simplify()
        if self.rule == 24:#ProdExpression -> ProdExpression * UnaryExpression
            return BinOp(self.comp[1].pos, "*", self.comp[0].simplify(), self.comp[2].simplify())
        if self.rule == 25:#ProdExpression -> UnaryExpression
            return self.comp[0].simplify()
        if self.rule == 26:#UnaryExpression -> identifier
            return VariableLookup(self.comp[0].pos, self.comp[0].text)
        if self.rule == 27:#UnaryExpression -> number
            return Constant(self.comp[0].pos, int(self.comp[0].text))
        if self.rule == 28:#UnaryExpression -> true
            return Constant(self.comp[0].pos, True)
        if self.rule == 29:#UnaryExpression -> false
            return Constant(self.comp[0].pos, False)
        if self.rule == 30:#UnaryExpression -> - UnaryExpression
            return UnaryOp(self.comp[0].pos, "-", self.comp[1].simplify())
        if self.rule == 31:#UnaryExpression -> ( Expression )
            return self.comp[1].simplify()

class ASTNode:
    def __init__(self, pos) -> None:
        self.pos = pos

    def execute(self, env):
        pass

class Statement(ASTNode):
    def __init__(self, pos, current, next) -> None:
        super().__init__(pos)
        self.current = current
        self.next = next
    def execute(self, env):
        self.current.execute(env)
        if self.next != None:
            self.next.execute(env)

class DeclarationStmt(ASTNode):
    def __init__(self, pos, type, name, expr) -> None:
        super().__init__(pos)
        self.type =type
        self.name = name
        self.expr = expr
    
    def execute(self, env):
        env[self.name] = self.expr.execute(env)

class AssignmentStmt(ASTNode):
    def __init__(self, pos, name, expr) -> None:
        super().__init__(pos)
        self.name = name
        self.expr = expr
    def execute(self, env):
        env[self.name] = self.expr.execute(env)


class PrintStmt(ASTNode):
    def __init__(self, pos, expr) -> None:
        super().__init__(pos)
        self.expr = expr
    def execute(self, env):
        print(self.expr.execute(env))

class WhileStmt(ASTNode):
    def __init__(self, pos, cond, statements) -> None:
        super().__init__(pos)
        self.cond = cond
        self.statements = statements
    def execute(self, env):
        while self.cond.execute(env) == True:
            self.statements.execute(env)

class IfStmt(ASTNode):
    def __init__(self, pos, cond, t_stmts, f_stmts) -> None:
        super().__init__(pos)
        self.cond = cond
        self.t_stmts = t_stmts
        self.f_stmts = f_stmts
    def execute(self, env):
        if self.cond.execute(env):
            self.t_stmts.execute(env)
        elif self.f_stmts != None:
            self.f_stmts.execute(env)


class BinOp(ASTNode):
    def __init__(self, pos, op, lhs, rhs) -> None:
        super().__init__(pos)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def execute(self, env):
        if self.op == "*":
            return self.lhs.execute(env) * self.rhs.execute(env)
        if self.op == "+":
            return self.lhs.execute(env) + self.rhs.execute(env)
        if self.op == "-":
            return self.lhs.execute(env) - self.rhs.execute(env)
        if self.op == "or":#Expression -> Expression or BooleanExpression
            return self.lhs.execute(env) or self.rhs.execute(env)
        if self.op == "and":#BooleanExpression -> BooleanExpression and CompExpression
            return self.lhs.execute(env) and self.rhs.execute(env)
        if self.op == "==":#CompExpression -> SumExpression == SumExpression
            return self.lhs.execute(env) == self.rhs.execute(env)
        if self.op == "!=":#CompExpression -> SumExpression != SumExpression
            return self.lhs.execute(env) != self.rhs.execute(env)
        if self.op == "<=":#CompExpression -> SumExpression <= SumExpression
            return self.lhs.execute(env) <= self.rhs.execute(env)
        if self.op == "<":#CompExpression -> SumExpression < SumExpression
            return self.lhs.execute(env) < self.rhs.execute(env)
        if self.op == ">=":#CompExpression -> SumExpression >= SumExpression
            return self.lhs.execute(env) >= self.rhs.execute(env)
        if self.op == ">":#CompExpression -> SumExpression > SumExpression
            return self.lhs.execute(env) > self.rhs.execute(env)

class VariableLookup(ASTNode):
    def __init__(self, pos, name) -> None:
        super().__init__(pos)
        self.name = name
    def execute(self, env):
        return env[self.name]

class Constant(ASTNode):
    def __init__(self, pos, value) -> None:
        super().__init__(pos)
        self.value = value
    
    def execute(self, env):
        return self.value

class UnaryOp(ASTNode):
    def __init__(self, pos, op, operand) -> None:
        super().__init__(pos)
        self.op = op
        self.operand = operand
    def execute(self, env):
        if self.op == "-":
            return - self.operand.execute(env)