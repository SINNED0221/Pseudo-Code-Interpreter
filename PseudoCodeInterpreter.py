def printRed(skk): print("\033[91m {}\033[00m" .format(skk))

class interpreter:
    def __init__(self):
        self.identifiers = []
        self.variables = {}
        self.arrays = {}
        self.functions = {}
        self.procedures = {}

        self.digits = "1234567890"
        self.operators = [
            "+",
            "-",
            "*",
            "/",
            "MOD",
            "DIV"
        ]
        self.keywords = [
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
            #'DIV',
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
            #'LCASE',
            #'LENGTH',
            #'MID',
            #'MOD',
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
            'WRITEFILE'
        ]
        self.types = [
                    "INTEGER",
                    "REAL",
                    "CHAR",
                    "STRING",
                    "BOOLEAN",
                    "DATE"
                      ]

    def run(self, code):
        lines = code.split("\n")
        lineNo = 0
        for line in lines:
            self.executeLine(line.strip(), lineNo)
            lineNo += 1
    
    def error(self, errType, lineNo, line, pos, detail = None, description = None):
        if errType == "invaSyn":
            printRed ("Syntax error: at line " + str(lineNo))
            printRed ("\t" + str(line))
            printRed ("\t" + " "*pos + "^" )
            if description:
                 printRed (description)
        elif errType == "nameErr":
            printRed ("Name error: <" + str(detail) + "> referenced before assigned at line " + str(lineNo))
        elif errType == "typeErr":
            printRed ("Type error: <" + str(detail) + "> is unexpected type at line " + str(lineNo))
            if description:
                printRed (description + " expected")
        
        quit()

    def executeLine(self, line, lineNo):
        if "//" in line:  # get rid of comments
            line = line[0 : line.find("//")]
        if line.startswith("OUTPUT"):
            self.exeOutput(line, lineNo)
        elif line.startswith("DECLARE"):
            self.exeDeclare(line, lineNo)

    def evalExpr(self, expression, line, lineNo):
        # Remove any whitespace from the expression
        expression = expression.replace(" ", "")
        # Operator precedence dictionary
        precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            'MOD': 3,
            'DIV': 3
        }
        # Stack to hold operators and values
        operatorStack = []
        valueStack = []
        def applyOperator():  # Helper functions for arithmetic operations
            operator = operatorStack.pop()
            operand2 = valueStack.pop()
            operand1 = valueStack.pop()

            if operator == '+':
                valueStack.append(operand1 + operand2)
            elif operator == '-':
                valueStack.append(operand1 - operand2)
            elif operator == '*':
                valueStack.append(operand1 * operand2)
            elif operator == '/':
                valueStack.append(operand1 / operand2)
            elif operator == 'MOD':
                valueStack.append(operand1 % operand2)
            elif operator == 'DIV':
                valueStack.append(operand1 // operand2)

        # Iterate through each character in the expression using a position pointer
        pos = -1
        while pos < len(expression)-1:
            pos += 1
            char = expression[pos]
            if char.isdigit():  # If the character is a digit, accumulate the number
                currentValue = char
                while (pos + 1 < len(expression) and expression[pos + 1] in self.digits+"."):
                    currentValue += expression[pos + 1]
                    char = expression[pos + 1]
                    pos +=1
                if "." in currentValue:  # Push the float or int value to the stack
                    valueStack.append(float(currentValue))
                else:
                    valueStack.append(int(currentValue))

            elif char.isalpha():
                id = char
                # The first char of a identifier can only be a letter but it can be followed by _ and number
                while (expression.index(char) + 1 < len(expression) and 
                       (expression[expression.index(char) + 1].isalpha() or 
                        expression[expression.index(char) + 1] in self.digits+"_")):
                    id += expression[expression.index(char) + 1]
                    char = expression[expression.index(char) + 1]
                    #if id in precedence.keys():  # If the first three match the operator, stop to avoid conflict
                    #    break

                type = self.getType(id, lineNo, line)
                if not(type == "INTEGER" or "REAL"):
                    self.error("typeErr", lineNo, line, int((int(line.index(id)+len(id))/2)), id, "INTEGER or REAL")

                pos += (len(id)-1)
                if id in precedence.keys():  # For the word being MOD or DIV
                    while (operatorStack and operatorStack[-1] != '(' and
                        precedence[id] <= precedence.get(operatorStack[-1], 0)):
                        # Apply operators with higher or equal precedence from the stack
                        applyOperator()
                    operatorStack.append(id)
                elif id in self.keywords:
                    self.error("invaSyn", lineNo, line, int((int(line.index(id)+len(id))/2)), None)
                elif id in self.identifiers:
                    valueStack.append(self.getValue(id, lineNo, line))
                else:
                    self.error("nameErr", lineNo, line, int((int(line.index(id))+len(id)/2)), id)

            elif char == '(':  # If the character is an opening parenthesis, push it to the operator stack
                operatorStack.append(char)
            elif char == ')':  # If the character is a closing parenthesis
                while operatorStack and operatorStack[-1] != '(': 
                    applyOperator()  # Apply operators until the opening parenthesis is encountered
                if operatorStack and operatorStack[-1] == '(':
                    operatorStack.pop()  # Pop the opening parenthesis from the stack
            elif char in precedence.keys():
                # If the character is an operator
                while (operatorStack and operatorStack[-1] != '(' and
                        precedence[char] <= precedence.get(operatorStack[-1], 0)):
                    applyOperator()   # Apply operators with higher or equal precedence from the stack
                operatorStack.append(char)
            else:
                self.error("typeErr", lineNo, line, pos, char, "INTEGER or REAL")
        while operatorStack:  # Apply any remaining operators in the stack
            applyOperator()
        return valueStack[0]  # The final value in the value stack is the result

    def strComb(self, expression, lineNo, line):
        tokens = expression.split("&")
        string = '"'
        for token in tokens:
            token = token.strip()
            if self.getType(token, lineNo, line) == "STRING":
                string += self.getString(token, lineNo, line)
        string += '"'
        return string

    def exeOutput(self, line, lineNo):
        if line[0:line.find(" ")] != "OUTPUT":  # If the OUTPUT is typed wrong, call invalSyn
            self.error("invaSyn", lineNo, line, 6, None, "Missing Space")
        else:
            message = ""
            expression = line[line.find(" ") : len(line)]  # Get everything behind OUTPUT
            tokens = expression.split(",")  # Seprate by commas
            for token in tokens:
                message += self.getString(token, lineNo, line)
            print(message)
    
    def exeDeclare(self, line, lineNo):
        if line[0:line.find(" ")] != "DECLARE":  # If the DECLARE is typed wrong, call invalSyn
            self.error("invaSyn", lineNo, line, int(line.find(" ")/2), None)
        elif line.find(":") == -1:
            self.error("invaSyn", lineNo, line, int(line.find(" ")/2), "Missing colon")
        ids = line[8: line.find(':')]
        type = line[line.find(':')+1: len(line)]
        type = type.strip()
        ids = ids.split(",")
        if type in self.types:
            for identifier in ids:
                identifier = identifier.strip()
                if identifier in self.identifiers:
                    self.identifiers.pop((self.identifiers.index(identifier)))
                    del (self.variables[identifier])
                self.identifiers.append(identifier)
                self.variables[identifier] = variable(identifier, type)
        elif type == "ARRAY":
            for identifier in ids:
                identifier = identifier.strip()
                if identifier in self.identifiers:
                    self.identifiers.pop((self.identifiers.index(identifier)))
                    del (self.arrays[identifier])
                self.identifiers.append(identifier)
                self.arrays[identifier] = array(identifier, type)
        else:
            self.error("invaSyn", lineNo, line, int(line.find(type)/2), "Invalid Data Type")
        
    def getValue(self, identifier, lineNo, line):
        identifier = identifier.strip()
        identifierWOLiteral = ""  # Remove all string literal to avoid conflict of keywords
        pos = -1
        while pos < len(identifier)-1:
            pos += 1
            c = identifier[pos]
            if c == '"' and pos < len(identifier)-1:  # If one quote is found, delete all until next one or to end
                identifierWOLiteral += c
                pos += 1
                c = identifier[pos]
                while c != '"' and pos < len(identifier)-1:
                    pos+=1
                    c = identifier[pos]
                if c == '"':  # add if the last quote is found
                    identifierWOLiteral += c
            elif c == "'" and pos < len(identifier)-1:  # If one quote is found, delete all until next one or to end
                identifierWOLiteral += c
                pos += 1
                c = identifier[pos]
                while c != "'" and pos < len(identifier)-1:
                    pos += 1
                    c = identifier[pos]
                if c == "'":  # add if the last quote is found
                    identifierWOLiteral += c
            else:
                identifierWOLiteral += c
        if any(op in identifierWOLiteral for op in self.operators):  # apart from string literal, there is a operator
            return self.evalExpr(identifier, line, lineNo)
        elif "&" in identifierWOLiteral:  # apart from string literal, there is a &
            return self.strComb(identifier, lineNo, line)
        elif all(n in self.digits+"." for n in identifier):  # it is a number
            return identifier
        elif identifier.startswith('"'):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == '"':
                    quoteCount += 1
            if quoteCount < 2:
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            else:
                return identifier
        elif identifier.startswith("'"):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == "'":
                    quoteCount += 1
            if quoteCount < 2:
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos > 2:  # single quote should only contian char
                self.error("typeErr", lineNo, line, int(line.find(identifier, 7)+1), identifier, "CHAR")
            else:
                return identifier
        elif identifier in self.keywords:
            self.error("invaSyn", lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.variables).keys():
            return (self.variables[identifier]).getVarValue()
        elif identifier in (self.functions).keys():
            return (self.variables[identifier]).getFunValue()
        elif identifier in (self.procedures).keys():
            self.error("invaSyn", lineNo, line, int(line.find(identifier)/2), "A procedure has no return value")
        else:
            self.error("nameErr", lineNo, line, int(line.find(identifier)/2), identifier)

    def getString(self, identifier, lineNo, line):
        identifier = identifier.strip()
        identifierWOLiteral = ""  # Remove all string literal to avoid conflict of keywords
        pos = -1
        while pos < len(identifier)-1:
            pos += 1
            c = identifier[pos]
            if c == '"' and pos < len(identifier)-1:  # If one quote is found, delete all until next one or to end
                identifierWOLiteral += c
                pos += 1
                c = identifier[pos]
                while c != '"' and pos < len(identifier)-1:
                    pos+=1
                    c = identifier[pos]
                if c == '"':  # add if the last quote is found
                    identifierWOLiteral += c
            elif c == "'" and pos < len(identifier)-1:  # If one quote is found, delete all until next one or to end
                identifierWOLiteral += c
                pos += 1
                c = identifier[pos]
                while c != "'" and pos < len(identifier)-1:
                    pos += 1
                    c = identifier[pos]
                if c == "'":  # add if the last quote is found
                    identifierWOLiteral += c
            else:
                identifierWOLiteral += c
        if any(op in identifierWOLiteral for op in self.operators):  # apart from string literal, there is a operator
            return str(self.evalExpr(identifier, line, lineNo))
        elif "&" in identifierWOLiteral:  # apart from string literal, there is a &
            return self.strComb(identifier, lineNo, line)[1:-1]
        elif all(n in self.digits+"." for n in identifier):  # it is a number
            return str(identifier)
        elif identifier.startswith('"'):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == '"':
                    quoteCount += 1
            if quoteCount < 2:
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            else:
                return identifier[1:-1]
        elif identifier.startswith("'"):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == "'":
                    quoteCount += 1
            if quoteCount < 2:
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos > 2:  # single quote should only contian char
                self.error("typeErr", lineNo, line, int(line.find(identifier, 7)+1), identifier, "CHAR")
            else:
                return identifier[1:-1]
        elif identifier in self.keywords:
            self.error("invaSyn", lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.variables).keys():
            return self.getString((self.variables[identifier]).getVarValue(), lineNo, line)
        elif identifier in (self.functions).keys():
            return self.getString((self.functions[identifier]).getFunValue(), lineNo, line)
        elif identifier in (self.procedures).keys():
            self.error("invaSyn", lineNo, line, int(line.find(identifier)/2), "A procedure has no return value")
        else:
            self.error("nameErr", lineNo, line, int(line.find(identifier)/2), identifier)

    def getType(self, identifier, lineNo, line):
        identifier = identifier.strip()
        identifierWOLiteral = ""  # Remove all string literal to avoid conflict of keywords
        pos = -1
        while pos < len(identifier)-1:
            pos += 1
            c = identifier[pos]
            if c == '"' and pos < len(identifier)-1:  # If one quote is found, delete all until next one or to end
                identifierWOLiteral += c
                pos += 1
                c = identifier[pos]
                while c != '"' and pos < len(identifier)-1:
                    pos+=1
                    c = identifier[pos]
                if c == '"':  # add if the last quote is found
                    identifierWOLiteral += c
            elif c == "'" and pos < len(identifier)-1:  # If one quote is found, delete all until next one or to end
                identifierWOLiteral += c
                pos += 1
                c = identifier[pos]
                while c != "'" and pos < len(identifier)-1:
                    pos += 1
                    c = identifier[pos]
                if c == "'":  # add if the last quote is found
                    identifierWOLiteral += c
            else:
                identifierWOLiteral += c
        if any(op in identifierWOLiteral for op in self.operators):  # apart from string literal, there is a operator
            if self.evalExpr(identifier, line, lineNo) == 'float':
                return "REAL"
            else:
                return "INTEGER"
        elif "&" in identifierWOLiteral:  # apart from string literal, there is a &
            self.strComb(identifier, lineNo, line)
            return "STRING"
        elif all(n in self.digits for n in identifier):  # it is a number
            if "." in identifier:
                return "REAL"
            else:
                return "INTEGER"
        elif identifier.startswith('"'):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == '"':
                    quoteCount += 1
            if quoteCount < 2:
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            else:
                return "STRING"
        elif identifier.startswith("'"):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == "'":
                    quoteCount += 1
            if quoteCount < 2:
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.error("invaSyn", lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos > 2:  # single quote should only contian char
                self.error("typeErr", lineNo, line, int(line.find(identifier, 7)+1), identifier, "CHAR")
            else:
                return "CHAR"
        elif identifier in self.keywords:
            self.error("invaSyn", lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.variables).keys():
            return (self.variables[identifier]).getVarType()
        elif identifier in (self.functions).keys():
            return (self.variables[identifier]).getFunType()
        elif identifier in (self.procedures).keys():
            self.error("invaSyn", lineNo, line, int(line.find(identifier)/2), "A procedure has no return value")
        else:
            self.error("nameErr", lineNo, line, int(line.find(identifier)/2), identifier)

class variable:
    def __init__(self, identifier, type, value = None):
        self.identifier = identifier
        self.type = type
        self.value = value
    
    def getVarValue(self):
        return self.value
    def getVarType(self):
        return self.type