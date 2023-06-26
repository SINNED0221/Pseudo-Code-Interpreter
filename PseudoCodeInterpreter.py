def printRed(skk): print("\033[91m {}\033[00m" .format(skk))

class interpreter:
    def __init__(self):
        self.identifiers = {}
        self.variables = {}
        self.functions = {}
        self.procedures = {}

        self.keywords = {
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
        }
    
    def run(self, code):
        lines = code.split("\n")
        lineNo = 0
        for line in lines:
            self.executeLine(line.strip(), lineNo)
            lineNo += 1
    
    def error(self, errType, lineNo, line, pos, detail):
        if errType == "invaSyn":
            printRed ("Syntax error: at line " + str(lineNo))
            printRed ("\t" + str(line))
            printRed ("\t" + " "*pos + "^" )
        elif errType == "nameErr":
            printRed ("Name error: <" + str(detail) + "> referenced before assigned at line " + str(lineNo))
        elif errType == "typeErr":
            printRed ("Type error: <" + str(detail) + "> referenced before assigned at line " + str(lineNo))
        
        quit()

    def executeLine(self, line, lineNo):
        if "//" in line:
            line = line[0 : line.find("//")]
        if line.startswith("OUTPUT"):
            self.exeOutput(line, lineNo)
        elif line.startswith("DECLARE"):
            self.exeDeclare(line, lineNo)
        elif line.startswith("DECLARE"):
            self.exeDeclare(line, lineNo)

    def exeOutput(self, line, lineNo):
        if line[0:line.find(" ")] != "OUTPUT":
            self.error("invaSyn", lineNo, line, int(line.find(" ")/2), None)
        else:
            message = ""
            expression = line[line.find(" ") : len(line)]
            tokens = expression.split(",")
            for token in tokens:
                token = token.strip()
                if token.startswith('"'):
                    if token.endswith('"'):
                        message += token[1:len(token)-1]
                    else:
                        self.error("invaSyn", lineNo, line, int(line.find(token, 7)+len(token)), None)
                elif token.startswith("'"):
                    if token.endswith("'"):
                        message += token[1:len(token)-1]
                    else:
                        self.error("invaSyn", lineNo, line, int(line.find(token, 7)+len(token)), None)
                elif token in self.keywords:
                    self.error("invaSyn", lineNo, line, int(line.find(token, 7)), None)
                elif token in self.identifiers:
                    self.getValue(token)
                else:
                    self.error("nameErr", lineNo, line, int(line.find(token, 7)), None)
            print(message)

    def stringForm(self, token, lineNo, line):
        string = ""
        if token.startswith('"'):
            if token.endswith('"'):
                string += token[1:len(token)-1]
            else:
                self.error("invaSyn", lineNo, line, int(line.find(token, 7)+len(token)), None)
        elif token.startswith("'"):
            if token.endswith("'"):
                string += token[1:len(token)-1]
            else:
                self.error("invaSyn", lineNo, line, int(line.find(token, 7)+len(token)), None)
        elif token in self.keywords:
            self.error("invaSyn", lineNo, line, int(line.find(token, 7)), None)
        elif token in self.identifiers:
            self.getValue()
        else:
            self.error("nameErr", lineNo, line, int(line.find(token, 7)), None)
        return string