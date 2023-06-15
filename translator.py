# Token types
TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_POW      = 'POW'

# Constants for dictionary
digits = '1234567890'


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


    def makeToken(self):
        tokens = []
        self.next()
        while self.char != None:
            if self.char in ' \t':
                
                self.next()
            elif self.char in digits:
                
                tokens.append(self.makeNumber())
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
                tokens.append(token(TT_DIV))
                self.next()
            elif self.char == '(':
                tokens.append(token(TT_LPAREN))
                self.next()
            elif self.char == ')':
                tokens.append(token(TT_RPAREN))
                self.next()
            elif self.char == '^':
                tokens.append(token(TT_POW))
                self.next()
            else:
                pos_start = self.pos.copy()
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + self.char + "'")    
        return tokens, None

def run(text):
    loclexer = lexer(text)
    tokens, error = loclexer.makeToken()

    return tokens, error        

print(run("1.2+1*4"))