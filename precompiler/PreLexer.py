import sly


class PreLexer(sly.Lexer):
    tokens = {NUM, IDENTIFIER, ADD, SUB, MUL, DIV, MOD, EQ, NE, GE, LE, GT, LT,
        PROCEDURE, PROGRAM, IS, VAR, BEGIN, END, L_BRACKET, R_BRACKET, ASSIGN, COMMA, SEMICOLON,
        IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE, REPEAT, UNTIL, READ, WRITE}

    ignore = ' \t\n'

    ignore_comment = r'\[[^\]]*\]'

    IDENTIFIER = r'[_a-z]+'

    ADD = r'\+'
    SUB = r'\-'
    MUL = r'\*'
    DIV = r'\/'
    MOD = r'\%'

    EQ = r"\="
    NE = r"\!\="
    GE = r"\>\="
    LE = r"\<\="
    GT = r"\>"
    LT = r"\<"

    L_BRACKET = r"\("
    R_BRACKET = r"\)"

    ASSIGN = r"\:\="
    COMMA = r"\,"
    SEMICOLON = r"\;"

    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    ENDIF = r"ENDIF"

    WHILE = r"WHILE"
    DO = r"DO"
    ENDWHILE = r"ENDWHILE"

    REPEAT = r"REPEAT"
    UNTIL = r"UNTIL"

    READ = r"READ"
    WRITE = r"WRITE"

    PROCEDURE = r"PROCEDURE"
    PROGRAM = r"PROGRAM"
    IS = r"IS"
    VAR = r"VAR"
    BEGIN = r"BEGIN"
    END = r"END"


    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t
    
    
    def error(self, t):
        print(f"Blad dla {t.value[0]}.")
        self.index += 1
