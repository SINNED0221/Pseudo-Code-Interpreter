import string

# Token types
TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_COMMENT  = 'COMMENT'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_CARET    = 'CARET'
TT_COMBINE  = 'COMBINE'
TT_ARROW    = 'ARROW'
TT_EQ       = 'EQ'
TT_GT       = 'GT'
TT_LT       = 'LT'
TT_LTE      = 'LTE'
TT_GTE      = 'GTE'
TT_NE       = 'NE'
TT_SHARP    = 'SHARP'
TT_KEYWORD  = 'KEYWORD'
TT_ID       = 'ID'

# Constants for dictionary
digits = '1234567890'
letters = string.ascii_letters
lettersAndDigits = letters + digits

# keywords of operators
keywords = [   
    'OF',
'AND',
'APPEND',
'ARRAY',
'BOOLEAN',
'BYREF',
'BYVAL',
'CALL',
'CASE',
'CHAR',
'CLASS',
'CLOSEFILE',
'CONSTANT',
'DATE',
'DECLARE',
'DIV',
'ELSE',
'ENDCASE',
'ENDCLASS',
'ENDFUNCTION',
'ENDIF',
'ENDPROCEDURE',
'ENDTYPE',
'ENDWHILE',
'EOF',
'FALSE',
'FOR',
'TO',
'FUNCTION',
'GETRECORD',
'IF',
'INHERITS',
'INPUT',
'INT',
'INTEGER',
'LCASE',
'LENGTH',
'MID',
'MOD',
'NEXT',
'NEW',
'NOT',
'OPENFILE',
'OR',
'OTHERWISE',
'OUTPUT',
'PROCEDURE',
'PRIVATE',
'PUBLIC',
'PUTRECORD',
'RAND',
'RANDOM',
'READ',
'READFILE',
'REAL',
'REPEAT',
'RETURN',
'RETURNS',
'RIGHT',
'SEEK',
'STEP',
'STRING',
'SUPER',
'THEN',
'TRUE',
'TYPE',
'UCASE',
'UNTIL',
'WHILE',
'WRITE',
'WRITEFILE',
]

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class inValidSyntax(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


class token :
    def __init__(self, dataType, value=None):
        self.dataType = dataType
        self. value = value
    def __repr__(self):
        if self.value:
            return f'{self.dataType}:{self.value}'
        else:
            return self.dataType


class lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.char = None

    def next(self):
        self.pos += 1
        if self.pos< len(self.text):
            self.char = self.text[self.pos]
        else:
            self.char = None

    def makeNumber(self):
        numString = ''
        dotCount = 0
        while self.char != None and self.char in digits + '.':
            if self.char == '.':
                if dotCount ==1:
                    # TODO Error goes here
                    break
                dotCount += 1
                numString += '.'
            else:
                numString += self.char
            self.next()
        if dotCount == 0:
            return token (TT_INT, int(numString))
        else:
            return token (TT_FLOAT, float(numString))    

    def makeId(self):
        idString = ''
        while self.char != None and self.char in lettersAndDigits + '_':
            idString += self.char
            self.next()
        if idString in keywords:
            return token (TT_KEYWORD, idString)
        else:
            return token (TT_ID, idString)        

    def makeToken(self):
        tokens = []
        self.next()
        while self.char != None:
            if self.char in ' \t':
                self.next()
            elif self.char in digits:
                tokens.append(self.makeNumber())
            elif self.char in letters:
                tokens.append(self.makeId())
            elif self.char == '+':
                tokens.append(token(TT_PLUS))
                self.next()
            elif self.char == '-':
                tokens.append(token(TT_MINUS))
                self.next()
            elif self.char == '*':
                tokens.append(token(TT_MUL))
                self.next()
            elif self.char == '/':
                self.next()
                if self.char == '/':
                    tokens.append(token(TT_COMMENT))
                    self.next()
                else:
                    tokens.append(token(TT_DIV))
            elif self.char == '(':
                tokens.append(token(TT_LPAREN))
                self.next()
            elif self.char == ')':
                tokens.append(token(TT_RPAREN))
                self.next()
            elif self.char == '^':
                tokens.append(token(TT_CARET))
                self.next()
            elif self.char == '&':
                tokens.append(token(TT_COMBINE))
                self.next()    
            elif self.char == '=':
                tokens.append(token(TT_EQ))
                self.next()
            elif self.char == '←':
                tokens.append(token(TT_ARROW))
                self.next()
            elif self.char == '#':
                tokens.append(token(TT_SHARP))
                self.next()
            elif self.char == '<':
                self.next()
                if self.char == '=':
                    tokens.append(token(TT_LTE))
                    self.next()
                elif self.char == '>':
                    tokens.append(token(TT_NE))
                    self.next()
                elif self.char == '-':
                    tokens.append(token(TT_ARROW))
                    self.next()
                else:
                    tokens.append(token(TT_LT))
            elif self.char == '>':
                self.next()
                if self.char == '=':
                    tokens.append(token(TT_GTE))
                    self.next()
                else:
                    tokens.append(token(TT_GT))
            else:
                pos_start = self.pos.copy()
                self.next()
                return [], IllegalCharError(pos_start, self.pos, "'" + self.char + "'")    
        return tokens, None

class parser:
    def __init__(self, tokens):
        self.pos = -1
        self.tokens = tokens
        self.curToken = None
    
    def next(self):
        self.pos += 1
        if self.pos > len(self.tokens):
            self.curToken = token(None)
        else:
            self.curToken = self.tokens[self.pos]
    

        


def run(text):
    loclexer = lexer(text)
    tokens, error = loclexer.makeToken()

    return tokens, error        
