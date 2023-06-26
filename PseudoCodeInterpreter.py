def printRed(skk): print("\033[91m {}\033[00m" .format(skk))

class interpreter:
    def __init__(self):
        self.identifiers = {}
        self.variables = {}
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

        # Helper functions for arithmetic operations
        def applyOperator():
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

        # Iterate through each character in the expression
        pos = -1
        while pos < len(expression)-1:
            pos += 1
            char = expression[pos]
            if char.isdigit():
                # If the character is a digit, accumulate the number
                currentValue = char
                while (pos + 1 < len(expression) and expression[pos + 1] in self.digits+"."):
                    currentValue += expression[pos + 1]
                    char = expression[pos + 1]
                    pos +=1

                # Push the number to the value stack
                valueStack.append(int(currentValue))

            if char.isalpha():
                id = char
                while (expression.index(char) + 1 < len(expression) and 
                       (expression[expression.index(char) + 1].isalpha() or expression[expression.index(char) + 1] in self.digits+"_.")):
                    id += expression[expression.index(char) + 1]
                    char = expression[expression.index(char) + 1]
                    if id in precedence.keys():
                        break
                pos += (len(id)-1)
                if id in precedence.keys():
                    while (operatorStack and operatorStack[-1] != '(' and
                        precedence[id] <= precedence.get(operatorStack[-1], 0)):
                        # Apply operators with higher or equal precedence from the stack
                        applyOperator()
                    operatorStack.append(id)
                elif id in self.keywords:
                    self.error("invaSyn", lineNo, line, int((int(line.index(id)+len(id))/2)), None)
                elif id in self.identifiers:
                    valueStack.append(self.getValue())
                else:
                    self.error("nameErr", lineNo, line, int((int(line.index(id))+len(id)/2)), id)

            elif char == '(':
                # If the character is an opening parenthesis, push it to the operator stack
                operatorStack.append(char)

            elif char == ')':
                # If the character is a closing parenthesis
                while operatorStack and operatorStack[-1] != '(':
                    # Apply operators until the opening parenthesis is encountered
                    applyOperator()

                if operatorStack and operatorStack[-1] == '(':
                    # Pop the opening parenthesis from the stack
                    operatorStack.pop()

            elif char in precedence.keys():
                # If the character is an operator
                while (operatorStack and operatorStack[-1] != '(' and precedence[char] <= precedence.get(operatorStack[-1], 0)):
                    # Apply operators with higher or equal precedence from the stack
                    applyOperator()
                operatorStack.append(char)

        # Apply any remaining operators in the stack
        while operatorStack:
            applyOperator()

        # The final value in the value stack is the result
        return valueStack[0]


    def exeOutput(self, line, lineNo):
        if line[0:line.find(" ")] != "OUTPUT":
            self.error("invaSyn", lineNo, line, int(line.find(" ")/2), None)
        else:
            message = ""
            expression = line[line.find(" ") : len(line)]
            tokens = expression.split(",")
            for token in tokens:
                token = token.strip()
                if any(op in token for op in self.operators):
                    message += str(self.evalExpr(token, line, lineNo))
                elif "&" in token:
                    message += self.strComb(token)
                elif all(n in self.digits+"." for n in token):
                    message += str(token)
                else:
                    message += self.stringForm(token, lineNo, line)[1:-1]
            print(message)

    def stringForm(self, token, lineNo, line):
        string = ""
        if token.startswith('"'):
            if token.endswith('"'):
                string = token
            else:
                self.error("invaSyn", lineNo, line, int(line.find(token, 7)+len(token)), None)
        elif token.startswith("'"):
            if token.endswith("'"):
                string = token
            else:
                self.error("invaSyn", lineNo, line, int(line.find(token, 7)+len(token)), None)
        elif token in self.keywords:
            self.error("invaSyn", lineNo, line, int((int(line.find(token, 7)+len(token))/2)), None)
        elif token in self.identifiers:
            self.getValue()
        else:
            self.error("nameErr", lineNo, line, int((int(line.find(token, 7)+len(token))/2)), None)
        return string