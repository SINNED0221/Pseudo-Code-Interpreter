import builtinFunction as bif
from datetime import datetime, date
import re

def printRed(skk): print("\033[91m {}\033[00m" .format(skk))

class error:
    
    def invaSyn(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Syntax error: at line " + str(lineNo))
        printRed ("\t" + str(line))
        if pos > -1:
            printRed ("\t" + " "*pos + "^" )
        if description:
             printRed (description)     
        quit()
    def nameErr(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Name error: <" + str(detail) + "> referenced before assigned at line " + str(lineNo))
        printRed ("\t" + str(line))
        if description:
            printRed (description + " expected")
        quit()
    def typeErr(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Type error: <" + str(detail) + "> is unexpected type at line " + str(lineNo))
        printRed ("\t" + str(line))
        if description:
            printRed (description + " expected")
        quit()
    def runTime(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Run time error: at line " + str(lineNo))
        printRed ("\t" + str(line))
        if pos != -1:
            printRed ("\t" + " "*pos + "^" )
        if description:
             printRed (description)
        quit()
    def indexErr(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Index error: array index  out of range at line "+str(lineNo))
        printRed ("\t" + str(line))
        if description:
             printRed (description)
        quit()
    def indentErr(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Indentation Error: at line " + str(lineNo))
        printRed ("\t" + str(line))
        if pos > -1:
            printRed ("\t" + " "*pos + "^" )
        if description:
             printRed (description)     
        quit()
    def argErr(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Argument Error: at line " + str(lineNo))
        printRed ("\t" + str(line))
        if pos > -1:
            printRed ("\t" + " "*pos + "^" )
        printRed ("<"+detail+"> missing "+str(description)+" positional argument(s)")     
        quit()
    def valErr(self, lineNo, line, pos, detail = None, description = None):
        printRed("Value error: '"+str(detail)+"' does not match format '"+description+"' at line "+str(lineNo))
        quit()

class interpreter:
    def __init__(self):

        self.err = error()

        self.identifiers = []
        self.variables = {}
        self.constants = {}
        self.arrays = {}
        self.functions = {}
        self.procedures = {}

        for n, f in zip(bif.builtIns.keys(), bif.builtIns.values()):
            self.identifiers.append(n)
            self.functions[n] = f

        self.digits = "1234567890"
        self.operators = [
            "+",
            "-",
            "*",
            "/",
            "MOD",
            "DIV"
        ]
        self.logicOperators = [
            "AND",
            "OR",
            "NOT"
        ]
        self.relationOperators = [
            "<",
            ">",
            "<=",
            ">=",
            "=",
            "<>"
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
            #'FALSE',
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
            #'TRUE',
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

    def initRun(self, code):
        lines = code.split("\n")
        self.run(lines, 1, 1)

    def run(self, lines, innitialPos, selfPos):
        lineNo = innitialPos-1
        selfPos = selfPos-1
        while lineNo - innitialPos < len(lines)-1:
            lineNo += 1  
            selfPos += 1  # this is the position of the line in its subcode block
            line = lines[lineNo-innitialPos]
            skip = self.executeLine(line.strip(), lineNo, lines, innitialPos, selfPos)
            if type(skip) == list:
                return skip[1]
            lineNo += skip  # tell the interpreter to go after the nested statement
            selfPos += skip

    def executeLine(self, line, lineNo, lines, innitialPos, selfPos):
        lineWOL = self.removeLiteral(line, lineNo, line)
        if "//" in lineWOL:  # get rid of comments
            line = line[0 : lineWOL.find("//")]
        line = line.replace("<-", "←")
        pos = -1
        identifier = ""
        char = line[0]
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                break
            identifier += char
        if identifier == "OUTPUT":
            self.exeOutput(lineNo, line)
            return 0
        elif identifier == "DECLARE":
            self.exeDeclare(lineNo, line)
            return 0
        elif identifier == "CONSTANT":
            self.exeConstant(lineNo, line)
            return 0
        elif identifier == "INPUT":
            self.exeInput(lineNo, line)
            return 0
        elif identifier == "IF":
            return self.exeIf(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "CASE":
            return self.exeCase(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "FOR":
            return self.exeFor(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "REPEAT":
            return self.exeRepeat(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "WHILE":
            return self.exeWhile(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "FUNCTION":
            return self.exeFunction(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "PROCEDURE":
            return self.exeProcedure(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "RETURN":  # return the value in skip as a list[skip, returnValue]
            return self.exeReturn(lineNo, line)
        elif identifier == "CALL":
            self.exeCall(lineNo, line)
            return 0

        elif identifier in self.identifiers:
            self.exeAssign(lineNo, line)
            return 0
        else:
            self.err.invaSyn(lineNo, line, -1)
    
    def error(self, errType, lineNo, line, pos, detail = None, description = None):
        if errType == "invaSyn":
            printRed ("Syntax error: at line " + str(lineNo))
            printRed ("\t" + str(line))
            if pos > -1:
                printRed ("\t" + " "*pos + "^" )
            if description:
                 printRed (description)
        elif errType == "nameErr":
            printRed ("Name error: <" + str(detail) + "> referenced before assigned at line " + str(lineNo))
            printRed ("\t" + str(line))
            if description:
                printRed (description + " expected")
        elif errType == "typeErr":
            printRed ("Type error: <" + str(detail) + "> is unexpected type at line " + str(lineNo))
            printRed ("\t" + str(line))
            if description:
                printRed (description + " expected")
        elif errType == "runTime":
            printRed ("Run time error: at line " + str(lineNo))
            printRed ("\t" + str(line))
            if pos != -1:
                printRed ("\t" + " "*pos + "^" )
            if description:
                 printRed (description)
        elif errType == "indexErr":
            printRed ("Index error: array index  out of range at line "+str(lineNo))
            printRed ("\t" + str(line))
        quit()

    def isValidChar(self, id):
        return id.isalpha() or id in self.digits + "_"

    def isArray(self, identifier, lineNo, line):
        identifierWOLiteral = self.removeLiteral(identifier, lineNo, line)
        identifierWOLiteral = identifierWOLiteral.strip()
        if ("[" and "]") in identifierWOLiteral and ((identifier[0: identifier.find("[")]) in self.arrays.keys() and
                                                      identifierWOLiteral.endswith("]")):
            identifier = identifier.strip()
            name = identifier[0: identifier.find("[")]
            name = name.strip()
            indexStr = identifier[identifier.find("[")+1: -1]
            indexes = self.commaSplit(indexStr, lineNo, line)
            for i, index in zip(range(len(indexes)), indexes):
                indexes[i] = self.getValue(index, lineNo, line)
            return [True, name, indexes]
        
        else:
            return [False, None]
    
    def isFunction(self, identifier, lineNo, line):
        identifierWOLiteral = self.removeLiteral(identifier, lineNo, line)
        identifierWOLiteral = identifierWOLiteral.strip()
        if ("(" and ")") in identifierWOLiteral and ((identifier[0: identifier.find("(")]) in self.functions.keys() and
                                                      identifierWOLiteral.endswith(")")):
            identifier = identifier.strip()
            name = identifier[0: identifier.find("(")]
            name = name.strip()
            argStr = identifier[identifier.find("(")+1: -1].strip()
            args = self.commaSplit(argStr, lineNo, line)
            if len(args)!= len(self.functions[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                len(self.functions[identifier].parameters)-len(args))
            paraTypes = self.functions[name].parameters.values()
            for i, arg, type in zip(range(len(args)), args, paraTypes):
                if self.getType(arg, lineNo, line) != type:
                    self.err.typeErr(lineNo, line, -1, arg, type)
                args[i] = self.getValue(arg, lineNo, line)
            return ["FUNC", name, args, False]
        
        elif ("(" and ")") in identifierWOLiteral and ((identifier[0: identifier.find("(")]) in self.procedures.keys() and
                                                      identifierWOLiteral.endswith(")")):
            identifier = identifier.strip()
            name = identifier[0: identifier.find("(")]
            name = name.strip()
            byref = self.procedures[name].byref
            argStr = identifier[identifier.find("(")+1: -1].strip()

            args = self.commaSplit(argStr, lineNo, line)

            if len(args)!= len(self.procedures[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                len(self.procedures[name].parameters)-len(args))
            if not byref:
                for i, arg in zip(range(len(args)), args):
                    args[i] = self.getValue(arg, lineNo, line)
            else:
                for i, arg in zip(range(len(args)), args):
                    if not arg in self.variables.keys():
                        self.err.nameErr(lineNo, line, -1, arg, "VARIABLE")
                    args[i] = self.variables[arg]
            return ["PROC", name, args, byref]
        elif identifierWOLiteral in self.functions.keys() and self.functions[identifierWOLiteral].parameters == {}:
            return ["FUNC", identifierWOLiteral, [], False]
        elif identifierWOLiteral in self.procedures.keys() and self.procedures[identifierWOLiteral].parameters == {}:
            return ["PROC", identifierWOLiteral, [], False]
        else:
            return [False, None, None, None]
    
    def isDate(self, id, lineNo, line):
        if re.match(r'^\d{2}/\d{2}/\d{4}$', id):
            try:
                return bool(datetime.strptime(id, "%d/%m/%Y"))
            except ValueError:
                self.err.valErr(lineNo, line, -1, id, "DD/MM/YYYY")
        else:
            return False
                

    def boolConvert(self, input):
        if input == "TRUE":
            return True
        elif input == "FALSE":
            return False
        elif input == True:
            return "TRUE"
        elif input == False:
            return "FALSE"

##### Commands #####

    def exeOutput(self, lineNo, line):
        if line[0:line.find(" ")] != "OUTPUT":  # If the OUTPUT is typed wrong, call invalSyn
            self.err.invaSyn(lineNo, line, 6, None, "Missing Space")
        else:
            message = ""
            expression = line[line.find(" ") : len(line)]  # Get everything behind OUTPUT
            tokens = self.commaSplit(expression, lineNo, line)
            for token in tokens:
                message += self.getString(token, lineNo, line)
            print(message)
    
    def exeInput(self, lineNo, line):
        if line[0:line.find(" ")] != "INPUT": 
            self.err.invaSyn(lineNo, line, 5, None, "Missing Space")
        identifier = line[line.find(" ")+1:]
        identifier = identifier.strip()
        type = self.getType(identifier, lineNo, line)
        value = input()
        if all(n in self.digits for n in value) or (value.startswith("-") and
                                                     all(n in self.digits for n in value[1:])):
            value = int(value)
            valueType = "INTEGER"
        elif all(n in self.digits+"." for n in value) or (value.startswith("-") and
                                                     all(n in self.digits+"." for n in value[1:])):
            value = float(value)
            valueType = "REAL"
        
        else:
            value = '"'+value+'"'
            valueType = "STRING"

        if identifier in (self.constants).keys():
            self.err.invaSyn(lineNo, line, (line.find(identifier)+len(identifier))//2, None, "A constant is immutable")
        elif type != valueType:
            self.err.typeErr(lineNo, line, (line.find(value)+len(value))//2, value, type)
        elif identifier in (self.variables).keys():
            self.variables[identifier].value = value
        elif (self.isArray(identifier, lineNo, line))[0] == True:
            self.arrays[self.isArray(identifier, lineNo, line)[1]].injectValue(self.isArray(identifier, lineNo, line)[2], value, lineNo, line)
        else:
            self.err.nameErr(lineNo, line, (line.find(identifier)+len(identifier))//2, identifier)

    def exeDeclare(self, lineNo, line):
        if line[0:line.find(" ")] != "DECLARE":  # If the DECLARE is typed wrong, call invalSyn
            self.err.invaSyn(lineNo, line, 8, None)
        elif line.find(":") == -1:
            self.err.invaSyn(lineNo, line, -1, "Missing colon")
        ids = line[8: line.find(':')]
        type = line[line.find(':')+1: len(line)]
        type = type.strip()
        ids = self.commaSplit(ids, lineNo, line)
        if type in self.types:
            for identifier in ids:
                identifier = identifier.strip()
                if identifier in self.identifiers:
                    self.identifiers.pop((self.identifiers.index(identifier)))
                    if identifier in self.variables.keys:
                        del (self.variables[identifier])
                    elif identifier in self.arrays.keys():
                        del (self.arrays[identifier])
                    elif identifier in self.functions.keys():
                        del (self.functions[identifier])
                    elif identifier in self.procedures.keys():
                        del (self.procedures[identifier])
                    elif identifier in self.constants.keys():
                        del (self.constants[identifier])
                elif identifier in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
                self.identifiers.append(identifier)
                self.variables[identifier] = variable(identifier, type)
        elif type.startswith("ARRAY"):
            if (type[0:type.find("[")]).strip() != "ARRAY":  # If the ARRAY is typed wrong, call invalSyn
                self.err.invaSyn(lineNo, line, 3, None)
            pos = 0
            c = type[0]
            boundStr = ""
            typeStr = ""
            count = 0
            while pos < len(type)-1:
                if c == "[":
                    count += 1
                    pos+=1
                    c = type[pos]
                    while pos < len(type)-1 and count > 0:
                        if c == "[":
                            count += 1
                        elif c == "]":
                            count -= 1
                        if count > 0:
                            boundStr += c
                        pos += 1
                        c = type[pos]
                    while pos < len(type)-1:
                        if c == "O":
                            pos += 1
                            c = type[pos]
                            if c == "F":
                                pos+=1
                                c = type[pos]
                                while pos < len(type)-1:
                                    if c.isalpha():
                                        typeStr+=c
                                        count += 1
                                        pos+=1
                                        c = type[pos]
                                        while pos < len(type)-1 and self.isValidChar(c):
                                            typeStr += c
                                            pos += 1
                                            c = type[pos]  
                                    else:
                                        pos+=1
                                        c = type[pos]
                            else:
                                self.err.invaSyn(lineNo, line, pos, None)
                        else:
                            pos+=1
                            c = type[pos]
                else:
                    pos+=1
                    c = type[pos]
            if self.isValidChar(c):
                typeStr += c

            if not(typeStr in self.types):
                self.err.invaSyn(lineNo, line, line.find(typeStr, pos-8, pos))
            boundStrList = self.commaSplit(boundStr, lineNo, line)
            bounds =[]
            for b in boundStrList:
                b = b.replace(" ", "")
                low = b[0:b.find(":")]
                high = b[b.find(":")+1:]
                if self.getType(low, lineNo, line) != "INTEGER":
                    self.err.typeErr(lineNo, line, None, low, "INTEGER")
                elif self.getType(high, lineNo, line) != "INTEGER":
                    self.err.typeErr(lineNo, line, None, high, "INTEGER")
                low = self.getValue(low, lineNo, line)
                high = self.getValue(high, lineNo, line)
                if low > high:
                    self.err.invaSyn(lineNo, line, -1, None, "Lower bound exceeds higher bound")
                bounds.append([low, high])

            for identifier in ids:
                identifier = identifier.strip()
                if identifier in self.identifiers:
                    self.identifiers.pop((self.identifiers.index(identifier)))
                if identifier in self.variables.keys:
                    del (self.variables[identifier])
                elif identifier in self.arrays.keys():
                    del (self.arrays[identifier])
                elif identifier in self.functions.keys():
                    del (self.functions[identifier])
                elif identifier in self.procedures.keys():
                    del (self.procedures[identifier])
                elif identifier in self.constants.keys():
                    del (self.constants[identifier])
                elif identifier in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
                self.identifiers.append(identifier)
                self.arrays[identifier] = array(identifier, typeStr, bounds)
        else:
            self.err.invaSyn(lineNo, line, int(line.find(type)/2), "Invalid Data Type")

    def exeConstant(self, lineNo, line):
        if line[0:line.find(" ")] != "CONSTANT":  # If the CONSTANT is typed wrong, call invalSyn
            self.err.invaSyn(lineNo, line, 8, None)
        elif line.find("=") == -1:
            self.err.invaSyn(lineNo, line, -1, "Missing equal sign")
        ids = line[8: line.find('=')]
        values = line[line.find('=')+1: len(line)]
        values = self.commaSplit(values, lineNo, line)
        ids = self.commaSplit(ids, lineNo, line)
        
        for identifier, value in zip(ids, values):
            type = self.getType(value, lineNo, line)
            if identifier in self.identifiers:
                self.identifiers.pop((self.identifiers.index(identifier)))
                if identifier in self.variables.keys:
                    del (self.variables[identifier])
                elif identifier in self.arrays.keys():
                    del (self.arrays[identifier])
                elif identifier in self.functions.keys():
                    del (self.functions[identifier])
                elif identifier in self.procedures.keys():
                    del (self.procedures[identifier])
                elif identifier in self.constants.keys():
                    del (self.constants[identifier])
                elif identifier in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, line.find(identifier, 8)+len(identifier)//2, None)
                self.identifiers.append(identifier)
                self.constants[identifier] = variable(identifier, type, value)
            else:
                self.err.invaSyn(lineNo, line, int(line.find(type)/2), "Invalid Data Type")

    def exeAssign(self, lineNo, line):
        leftStr = line[0: line.find("←")]
        rightStr = line[line.find("←")+1: ]
        lefts = self.commaSplit(leftStr, lineNo, line)
        rights = self.commaSplit(rightStr, lineNo, line)
        for left, right in zip(lefts, rights):
            leftType = self.getType(left, lineNo, line)
            rightType = self.getType(left, lineNo, line)
            right = self.getValue (right, lineNo, line)
            if left in (self.constants).keys():
                self.err.invaSyn(lineNo, line, (line.find(left)+len(left))//2, None, "A constant is immutable")
            elif leftType != rightType:
                self.err.typeErr(lineNo, line, (line.find(right)+len(right))//2, right, leftType)
            elif left in (self.variables).keys():
                self.variables[left].value = right
            elif (self.isArray(left, lineNo, line))[0] == True:
                self.arrays[self.isArray(left, lineNo, line)[1]].injectValue(self.isArray(left, lineNo, line)[2], right, lineNo, line)
            else:
                self.err.nameErr(lineNo, line, (line.find(left)+len(left))//2, left)

    def exeIf(self, lineNo, line, lines, innitialPos, selfPos):
        line = line.strip()
        if not(line.endswith("THEN")) or self.isValidChar(line[len(line)-5]):
            self.err.invaSyn(lineNo, line, len(line), None, "THEN expected")
        
        expression = line[2:len(line)-5].strip()
        if self.getType(expression, lineNo, line) == "BOOLEAN":
            ifOrElse = self.boolConvert(self.getValue(expression, lineNo, line))
        else:
            self.err.typeErr(lineNo, line, 3, expression, "BOOLEAN")
        
        temp =[]
        elsePos, endPos = 0, 0
        pos = selfPos-1
        indentation = 0
        skip = 0
        end = False
        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos]
            if subLine.rstrip() == "ELSE":
                elsePos = pos
            elif subLine.rstrip() == "ENDIF":
                end = True
                endPos = pos
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "ENDIF expected")
        if ifOrElse:
            startPos = selfPos
            if elsePos != 0:
                endPos = elsePos
            else:
                endPos = endPos
        else:
            if elsePos != 0:
                startPos = elsePos + 1
                endPos = endPos
            else:
                startPos = -1
        
        for subLine in lines[startPos:endPos]:
             if subLine.startswith(" "):
                if indentation == 0:
                    for c in subLine:
                        if c == " ":
                            indentation += 1
                        else:
                            break
                else:
                    if subLine.startswith(" "*indentation):
                        pass
                    else:
                        self.err.indentErr(lineNo+pos, subLine, 0, None, "Unexpected indent")
                subLine = subLine[indentation:]
                temp.append(subLine)
        self.run(temp, lineNo+startPos, 1)

        return skip

    def exeCase(self, lineNo, line, lines, innitialPos, selfPos):
        if not(line.startswith("CASE OF")):
            self.err.invaSyn(lineNo, line, 3, None, "Should be CASE OF")
        identifier = line[7:].strip()
        value = self.getValue(identifier, lineNo, line)
        type = self.getType(identifier, lineNo, line)

        linesToExe =[]
        pos = selfPos-1
        indentation = 0
        skip = 0
        end = False

        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos].rstrip()
            if subLine == "ENDCASE":
                end = True
                subLines = lines[selfPos: pos+1]
                break
            else:
                pass
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "ENDCASE expected")
        pos = -1

        
        while pos < len(subLines)-1:
             pos += 1
             subLine = subLines[pos]
             if subLine.startswith(" "):
                if indentation == 0:
                    for c in subLine:
                        if c == " ":
                            indentation += 1
                        else:
                            break
                else:
                    if subLine.startswith(" "*indentation):
                        pass
                    else:
                        self.err.indentErr(lineNo+pos, subLine, 0, None, "Unexpected indent")
                subLine = subLine[indentation:]
                if not(subLine.startswith(" ")):
                    valueEql = False
                    if subLine.find(":") == -1:
                        self.err.invaSyn(lineNo+pos, subLine, -1, None, "Missing colon")
                    caseStr = subLine[0:subLine.find(":")]
                    caseWOL = self.removeLiteral(caseStr, lineNo+pos, subLine)
                    if "TO" in caseWOL:
                        lower = self.getValue(caseStr[0:caseWOL.find("TO")].strip(), lineNo+pos, subLine)
                        upper = self.getValue(caseStr[caseWOL.find("TO")+2:].strip(), lineNo+pos, subLine)
                        if lower > upper:
                            temp = lower
                            lower = upper
                            upper = lower
                        if lower <= value <= upper:
                            valueEql = True
                    elif caseStr.rstrip() == "OTHERWISE":
                        valueEql = True
                    else:
                        caseValue = self.getValue(caseStr, lineNo+pos, subLine)
                        if caseValue == value:
                            valueEql = True
                    
                    if valueEql:
                        startPos = lineNo + pos + 1
                        subIndent = subLine.find(":")
                        subLine = subLine[subLine.find(":")+1:]
                        for c in subLine:
                            if c == " ":
                                subIndent += 1
                                subLine = subLine[1:]
                            else:
                                break
                        linesToExe.append(subLine)
                        subIndent = indentation + subIndent + 1
                        while pos < len(subLines)-1:
                            pos += 1
                            subLine = subLines[pos]
                            if subLine.startswith(" "*subIndent):
                                subLine = subLine[subIndent:]
                                linesToExe.append(subLine)
                            elif not(subLine[indentation:].startswith(" ")):
                                self.run(linesToExe, startPos, 1)
                                return skip
                            else:
                                self.err.indentErr(lineNo+pos, subLine, -1, None, "Unexpected indent")
                    else:
                        pass
        return skip

    def exeFor(self, lineNo, line, lines, innitialPos, selfPos):
        line = line.strip()
        
        expression = line[3:].strip()
        expressionWOL = self.removeLiteral(expression, lineNo, line)

        if "STEP" in expressionWOL:
            stepPos = expressionWOL.find("STEP")
            if not(self.isValidChar(expressionWOL[stepPos-1])) and not (self.isValidChar(expressionWOL[stepPos+4])):
                if not self.getType(expression[stepPos+4:].strip(), lineNo, line) == "INTEGER":
                    self.err.typeErr(lineNo, line, line.find(expression[stepPos+4:].strip()), 
                                expression[stepPos+4:].strip(), "INTEGER")
                step = self.getValue(expression[stepPos+4:].strip(), lineNo, line)
                expression = expression[0:stepPos].strip()
        else:
            step = 1

        left = expression[0: expression.find("←")].strip()
        right = expression[expression.find("←")+1: ].strip()
        rightWOL = self.removeLiteral(right, lineNo, line)

        leftType = self.getType(left, lineNo, line)
        if not "TO" in rightWOL:
            self.err.invaSyn(lineNo, line, line.find(right)+len(right)//2, None, "TO expected")
        else:
            lowerStr = right[0:rightWOL.find("TO")].strip()
            upperStr = right[rightWOL.find("TO")+2:].strip()
            if self.getType(lowerStr, lineNo, line) != "INTEGER":
                self.err.typeErr(lineNo, line, line.find(lowerStr)+len(lowerStr)//2, lowerStr, "INTEGER")
            if self.getType(upperStr, lineNo, line) != "INTEGER":
                self.err.typeErr(lineNo, line, line.find(upperStr)+len(lowerStr)//2, upperStr, "INTEGER")    
            lower = self.getValue(lowerStr, lineNo, line)
            upper = self.getValue(upperStr, lineNo, line)
        if left in (self.constants).keys():
            self.err.invaSyn(lineNo, line, (line.find(left)+len(left))//2, None, "A constant is immutable")
        elif leftType != "INTEGER":
            self.err.typeErr(lineNo, line, line.find(left)+len(left)//2, left, "INTEGER")
        elif left in (self.variables).keys():
            pass
        elif ((self.isArray(left, lineNo, line))[0] == True or 
                (self.isFunc(left, lineNo, line))[0] == True or 
                (self.isProc(left, lineNo, line)== True)):
            self.err.invaSyn(lineNo, line, line.find(left)+len(left)//2, None, "A FOR loop only accept vriable as identifier")
        else:
            self.err.nameErr(lineNo, line, (line.find(left)+len(left))//2, left)
    
        linesToExe =[]
        endPos = 0
        pos = selfPos-1
        startPos = selfPos
        indentation = 0
        skip = 0
        end = False
        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos]
            if subLine.startswith("NEXT"):
                if subLine[5:].strip() == str(left) and not(self.isValidChar(subLine[4])):
                    end = True
                    endPos = pos
                    break
                else:
                    self.err.invaSyn(innitialPos+pos, subLine, -1, None, "Invalid NEXT")


        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "NEXT expected")

        for subLine, pos in zip(lines[startPos:endPos], range(endPos - startPos)):
            if subLine.startswith(" "):
               if indentation == 0:
                   for c in subLine:
                       if c == " ":
                           indentation += 1
                       else:
                           break
               else:
                   if subLine.startswith(" "*indentation):
                       pass
                   else:
                       self.err.indentErr(lineNo+pos, subLine, 0, None, "Unexpected indent")
               subLine = subLine[indentation:]
               linesToExe.append(subLine)
        
        for i in range (lower, upper+1, step):
            self.variables[left].value = i
            self.run(linesToExe, lineNo+startPos, 1)
        return skip

    def exeRepeat(self, lineNo, line, lines, innitialPos, selfPos):
        line = line.rstrip()
        if line != "REPEAT":
            self.err.invaSyn(lineNo, line, 4, None, "Should be REPEAT")
    
        linesToExe =[]
        endPos = 0
        pos = selfPos-1
        startPos = selfPos
        indentation = 0
        skip = 0
        end = False
        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos]
            if subLine.startswith("UNTIL"):
                if not(self.isValidChar(subLine[5])):
                    end = True
                    endPos = pos
                    expression = subLine[5:].strip()
                    endLine = subLine
                else:
                    self.err.invaSyn(innitialPos+pos, subLine, -1, None, "Invalid UNTIL")
                
                break
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "UNTIL expected")

        for subLine, pos in zip(lines[startPos:endPos], range(endPos - startPos)):
            if subLine.startswith(" "):
               if indentation == 0:
                   for c in subLine:
                       if c == " ":
                           indentation += 1
                       else:
                           break
               else:
                   if subLine.startswith(" "*indentation):
                       pass
                   else:
                       self.err.indentErr(lineNo+pos, subLine, 0, None, "Unexpected indent")
               subLine = subLine[indentation:]
               linesToExe.append(subLine)
        self.run(linesToExe, lineNo+startPos, 1)
        
        if self.getType(expression, endPos+1, endLine) != "BOOLEAN":
            self.err.typeErr(endPos+1, endLine, subLine.find(expression)+len(expression)//2, expression, "BOOLEAN")
        until = self.boolConvert(self.getValue(expression, endPos+1, endLine))
        while not until:
            self.run(linesToExe, lineNo+startPos, 1)
            until = self.boolConvert(self.getValue(expression, endPos+1, endLine))
        
        return skip

    def exeWhile(self, lineNo, line, lines, innitialPos, selfPos):
        line = line.rstrip()
        expression = line[5:].strip()
        whileLine = line
    
        linesToExe =[]
        endPos = 0
        pos = selfPos-1
        startPos = selfPos
        indentation = 0
        skip = 0
        end = False
        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos]
            if subLine.startswith("ENDWHILE"):
                if subLine.rstrip() != "ENDWHILE":
                    self.err.invaSyn(innitialPos + pos, subLine, -1, None, "Should be ENDWHILE")
                end = True
                endPos = pos
                break
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "ENDWHILE expected")

        for subLine, pos in zip(lines[startPos:endPos], range(endPos - startPos)):
            if subLine.startswith(" "):
               if indentation == 0:
                   for c in subLine:
                       if c == " ":
                           indentation += 1
                       else:
                           break
               else:
                   if subLine.startswith(" "*indentation):
                       pass
                   else:
                       self.err.indentErr(selfPos + pos+1, subLine, 0, None, "Unexpected indent")
               subLine = subLine[indentation:]
               linesToExe.append(subLine)
        
        if self.getType(expression, startPos, whileLine) != "BOOLEAN":
            self.err.typeErr(startPos, whileLine, subLine.find(expression)+len(expression)//2, expression, "BOOLEAN")
        whileBool = self.boolConvert(self.getValue(expression, startPos, whileLine))
        while whileBool:
            self.run(linesToExe, lineNo+1, 1)
            whileBool = self.boolConvert(self.getValue(expression, endPos+1, whileLine))

        return skip

    def exeFunction(self, lineNo, line, lines, innitialPos, selfPos):
        pos = 8
        lineWOL = self.removeLiteral(line, lineNo, line)
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                pos -= 1
                break
        identifier = line[8:pos+1].strip()
        parasStr = ""
        token = ""
        returns = False
        while pos < len(line)-1:
            pos += 1
            char = lineWOL[pos]
            if char == "(":
                while pos < len(line)-1:
                    pos+=1
                    char = line[pos]
                    if char == ")":
                        break
                    else:
                        parasStr += char
            else:
                token += char
            if token.strip() == "RETURNS":
                returns = True
                token = ""
        if returns:
            type = token.strip()
            if not(type in self.types):
                self.err.invaSyn(lineNo, line, line.find(type)+len(type)//2, None, str(type)+" is not a valid type")
        else:
            self.err.invaSyn(lineNo, line, -1, None, "RETURNS expected")

        if parasStr.startswith("BYREF"):
                self.err.invaSyn(lineNo, line, line.find("BYREF")+len("BYREF")//2, None, 
                                 "Parameters should not be passed by reference to a function")
        elif parasStr.startswith("BYVAL"):
            parasStr = parasStr[5:].strip()

        paras = {}

        if parasStr:
            paraList = self.commaSplit(parasStr, lineNo, line)
            paras = {}
            for para in paraList:
                if not ":" in para:
                    self.err.invaSyn(lineNo, line, line.find(para)+len(para)//2, None, "Missing colon")
                paraName = para[0:para.find(":")].strip()
                paraType = para[para.find(":")+1:].strip()
                if not paraType in self.types:
                    self.err.invaSyn(lineNo, line, line.find(paraType)+len(paraType)//2, None, "Invalid type")
                paras[paraName] = paraType

        linesToExe =[]
        endPos = 0
        pos = selfPos-1
        startPos = selfPos
        indentation = 0
        skip = 0
        end = False
        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos]
            if subLine.startswith("ENDFUNCTION"):
                if subLine.rstrip() != "ENDFUNCTION":
                    self.err.invaSyn(innitialPos + pos, subLine, -1, None, "Should be ENDFUNCTION")
                end = True
                endPos = pos
                break
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "ENDFUNCTION expected")
        
        for subLine, pos in zip(lines[startPos:endPos], range(endPos - startPos)):
            if subLine.startswith(" "):
               if indentation == 0:
                   for c in subLine:
                       if c == " ":
                           indentation += 1
                       else:
                           break
               else:
                   if subLine.startswith(" "*indentation):
                       pass
                   else:
                       self.err.indentErr(selfPos + pos+1, subLine, 0, None, "Unexpected indent")
               subLine = subLine[indentation:]
               linesToExe.append(subLine)
            else:
                self.err.indentErr(selfPos + pos+1, subLine, 0, None, "Unexpected indent")

        if identifier in self.identifiers:
            self.identifiers.pop((self.identifiers.index(identifier)))
            if identifier in self.variables.keys:
                del (self.variables[identifier])
            elif identifier in self.arrays.keys():
                del (self.arrays[identifier])
            elif identifier in self.functions.keys():
                del (self.functions[identifier])
            elif identifier in self.procedures.keys():
                del (self.procedures[identifier])
            elif identifier in self.constants.keys():
                del (self.constants[identifier])
            elif identifier in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, line.find(identifier, 8)+len(identifier)//2, None)
        self.identifiers.append(identifier)
        self.functions[identifier] = function(identifier, type, lineNo+1, linesToExe, paras)
        return skip
    
    def exeProcedure(self, lineNo, line, lines, innitialPos, selfPos):
        pos = 9
        lineWOL = self.removeLiteral(line, lineNo, line)
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                pos -= 1
                break
        identifier = line[9:pos+1].strip()
        parasStr = ""
        token = ""
        while pos < len(line)-1:
            pos += 1
            char = lineWOL[pos]
            if char == "(":
                while pos < len(line)-1:
                    pos+=1
                    char = line[pos]
                    if char == ")":
                        break
                    else:
                        parasStr += char
            else:
                token += char
            if token.strip() == "RETURNS":
                self.err.invaSyn(lineNo, line, pos, None, "A procedure has no returning value")

        byref = False
        if parasStr.startswith("BYREF"):
            byref = True
            parasStr = parasStr[5:].strip()
        elif parasStr.startswith("BYVAL"):
            parasStr = parasStr[5:].strip()

        paras = {}

        if parasStr:
            paraList = self.commaSplit(parasStr, lineNo, line)
            paras = {}
            for para in paraList:
                if not ":" in para:
                    self.err.invaSyn(lineNo, line, line.find(para)+len(para)//2, None, "Missing colon")
                paraName = para[0:para.find(":")].strip()
                paraType = para[para.find(":")+1:].strip()
                if not paraType in self.types:
                    self.err.invaSyn(lineNo, line, line.find(paraType)+len(paraType)//2, None, "Invalid type")
                paras[paraName] = paraType

        linesToExe =[]
        endPos = 0
        pos = selfPos-1
        startPos = selfPos
        indentation = 0
        skip = 0
        end = False
        while pos < len(lines)-1:
            skip += 1
            pos += 1
            subLine = lines[pos]
            if subLine.startswith("ENDPROCEDURE"):
                if subLine.rstrip() != "ENDPROCEDURE":
                    self.err.invaSyn(innitialPos + pos, subLine, -1, None, "Should be ENDPROCEDURE")
                end = True
                endPos = pos
                break
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "ENDPROCEDURE expected")
        
        for subLine, pos in zip(lines[startPos:endPos], range(endPos - startPos)):
            if subLine.startswith(" "):
               if indentation == 0:
                   for c in subLine:
                       if c == " ":
                           indentation += 1
                       else:
                           break
               else:
                   if subLine.startswith(" "*indentation):
                       pass
                   else:
                       self.err.indentErr(selfPos + pos+1, subLine, 0, None, "Unexpected indent")
               subLine = subLine[indentation:]
               if subLine.startswith("RETURN") and not(self.isValidChar(subLine[6])):
                   self.err.invaSyn(lineNo, line, pos, None, "A procedure has no returning value")
               linesToExe.append(subLine)
            else:
                self.err.indentErr(selfPos + pos+1, subLine, 0, None, "Unexpected indent")

        if identifier in self.identifiers:
            self.identifiers.pop((self.identifiers.index(identifier)))
            if identifier in self.variables.keys:
                del (self.variables[identifier])
            elif identifier in self.arrays.keys():
                del (self.arrays[identifier])
            elif identifier in self.functions.keys():
                del (self.functions[identifier])
            elif identifier in self.procedures.keys():
                del (self.procedures[identifier])
            elif identifier in self.constants.keys():
                del (self.constants[identifier])
            elif identifier in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, line.find(identifier, 8)+len(identifier)//2, None)
        self.identifiers.append(identifier)
        self.procedures[identifier] = procedure(identifier, type, lineNo+1, linesToExe, byref, paras)
        return skip

    def exeReturn(self, lineNo, line):
        expression = line[6:].strip()
        # TODO type check
        return[0, self.getValue(expression, lineNo, line)]

    def exeCall(self, lineNo, line):
        identifier = line[4:].strip()
        proc = self.isFunction(identifier, lineNo, line)
        if not proc[0]:
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "<"+str(identifier)+"> is not callable")
        (self.procedures[proc[1]]).returnValue(proc[2], lineNo, line, proc[3])

##### Utility functions #####

    def removeLiteral(self, token, lineNo, line):
        
        tokenWOLiteral = ""  # Remove all string literal to avoid conflict of keywords
        pos = -1
        while pos < len(token)-1:
            pos += 1
            c = token[pos]
            if c == '"' and pos < len(token)-1:  # If one quote is found, delete all until next one or to end
                tokenWOLiteral += c
                pos += 1
                c = token[pos]
                while c != '"' and pos < len(token)-1:
                    pos+=1
                    tokenWOLiteral += " "
                    c = token[pos]
                if c == '"':  # add if the last quote is found
                    tokenWOLiteral += c
                else:
                    self.err.invaSyn(lineNo, line, line.find(token)+pos, None, "Mismatched quotes")
            elif c == "'" and pos < len(token)-1:  # If one quote is found, delete all until next one or to end
                tokenWOLiteral += c
                pos += 1
                c = token[pos]
                while c != "'" and pos < len(token)-1:
                    pos += 1
                    tokenWOLiteral += " "
                    c = token[pos]
                if c == "'":  # add if the last quote is found
                    tokenWOLiteral += c
                else:
                    self.err.invaSyn(lineNo, line, line.find(token)+pos, None, "Mismatched quotes")
            # check for parantesys behind a function
            elif c == "(" and self.isValidChar(token[pos-1]):
                count = 1
                tokenWOLiteral += c
                pos += 1
                c = token[pos]
                while count > 0 and pos < len(token)-1:
                    pos += 1
                    tokenWOLiteral += " "
                    c = token[pos]
                    if c == "(":
                        count += 1
                    elif c == ")":
                        count -= 1
                if c == ")":  
                    tokenWOLiteral += c
                elif count > 0:
                    self.err.invaSyn(lineNo, line, line.find(token)+pos, None, "Mismatched parentheses")
            # check for array
            elif c == "[" and self.isValidChar(token[pos-1]):
                count = 1
                tokenWOLiteral += c
                pos += 1
                c = token[pos]
                while count > 0 and pos < len(token)-1:
                    pos += 1
                    tokenWOLiteral += " "
                    c = token[pos]
                    if c == "[":
                        count += 1
                    elif c == "]":
                        count -= 1
                if c == "]": 
                    tokenWOLiteral += c
                elif count > 0:
                    self.err.invaSyn(lineNo, line, line.find(token)+pos, None, "Mismatched parentheses")
            else:
                tokenWOLiteral += c
        return tokenWOLiteral
    
    def commaSplit(self, expression, lineNo, line):
        tokens = []
        expressionWOLiteral = self.removeLiteral(expression, lineNo, line)
        tokensWOL = expressionWOLiteral.split(",")  # Seprate by commas
        pos = 0
        for tokenWOL in tokensWOL:
            tokens.append((expression[pos: pos + len(tokenWOL)]).strip())
            pos += len(tokenWOL)+1
        return tokens

    def getValue(self, identifier, lineNo, line):
        identifierWOLiteral = self.removeLiteral(identifier, lineNo, line)
        if not identifier:
            return identifier
        if any(op in identifierWOLiteral for op in self.logicOperators):
            valid = False
            for op in self.logicOperators:
                pos = identifierWOLiteral.find(op)
                while pos != -1:
                    if ((not self.isValidChar(identifierWOLiteral[pos-1]) or pos-1 == -1) and
                        not identifierWOLiteral[pos+len(op)].isalpha()):
                        valid = True
                    pos = identifierWOLiteral.find(op, pos+1)

            if valid:
                return self.evalLogic(identifier, lineNo, line)
            else:
                pass
        if any(op in identifierWOLiteral for op in self.relationOperators):
            return self.evalRelation(identifier, lineNo, line)
        if any(op in identifierWOLiteral for op in self.operators):  # apart from string literal, there is a operator
            valid = False
            if any (op in identifierWOLiteral for op in self.operators[0:4]):
                valid = True
            for op in self.operators[4:]:
                pos = identifierWOLiteral.find(op)
                while pos != -1:
                    if (not self.isValidChar(identifierWOLiteral[pos-1]) and
                        not identifierWOLiteral[pos+3].isalpha()):
                        valid = True
                    pos = identifierWOLiteral.find(op, pos+1)
            
            if valid:
                return self.evalExpr(identifier, lineNo, line)
            else:
                pass
        if "&" in identifierWOLiteral:  # apart from string literal, there is a &
            return self.strComb(identifier, lineNo, line)
        elif all(n in self.digits for n in identifier) or (identifier.startswith("-") and 
                                                           all(n in self.digits for n in identifier[1:])):  # it is a number
            if "." in identifier:
                return float(identifier)
            return int(identifier)
        
        elif identifier.startswith('"'):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == '"':
                    quoteCount += 1
            if quoteCount < 2:
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
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
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos > 2:  # single quote should only contian char
                self.err.typeErr(lineNo, line, int(line.find(identifier, 7)+1), identifier, "CHAR")
            else:
                return identifier
        
        elif self.isDate(identifier, lineNo, line):
            return identifier

        elif identifier in (self.keywords or (self.keywords).lower()):
            self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.variables).keys():
            return (self.variables[identifier]).returnValue()
        elif identifier in (self.constants).keys():
            return (self.constants[identifier]).returnValue()
        elif self.isArray(identifier, lineNo, line)[0] == True:
            arr = self.isArray(identifier, lineNo, line)
            return (self.arrays[arr[1]]).returnValue(arr[2], lineNo, line)
        elif self.isFunction(identifier, lineNo, line)[0] == "FUNC":
            func = self.isFunction(identifier, lineNo, line)
            return (self.functions[func[1]]).returnValue(func[2], lineNo, line)
        elif self.isFunction(identifier, lineNo, line)[0] == "PROC":
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, "A procedure has no return value")
        elif identifier in ["TRUE", "FALSE"]:
            return identifier
        else:
            self.err.nameErr(lineNo, line, int(line.find(identifier)/2), identifier)

    def getString(self, identifier, lineNo, line):
        identifier = str(self.getValue(identifier, lineNo, line))
        if identifier.startswith('"'):
            pos = 0
            quoteCount = 1
            while pos < len(identifier)-1 and quoteCount < 2:
                pos += 1
                if identifier[pos] == '"':
                    quoteCount += 1
            if quoteCount < 2:
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
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
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos > 2:  # single quote should only contian char
                self.err.typeErr(lineNo, line, int(line.find(identifier, 7)+1), identifier, "CHAR")
            else:
                return identifier[1:-1]
        else:
            return identifier

    def getType(self, identifier, lineNo, line):
        
        identifier = identifier.strip()

        ###Literals###

        if all(n in self.digits+"." for n in identifier):  # it is a number
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
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)  # the 7 in find is to make sure that
            elif pos < len(identifier)-1:  # if quote is not at the end               # the keyword is not taken as the wrong identifier
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
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
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos < len(identifier)-1:  # if quote is not at the end
                self.err.invaSyn(lineNo, line, int(line.find(identifier, 7)+pos+1), None)
            elif pos > 2:  # single quote should only contian char
                self.err.typeErr(lineNo, line, int(line.find(identifier, 7)+1), identifier, "CHAR")
            else:
                return "CHAR"
        elif identifier in ["TRUE", "FALSE"]:
            return "BOOLEAN"
        
        elif self.isDate(identifier, lineNo, line):
            return "DATE"

        ###identifiers###

        elif identifier in (self.keywords or (self.keywords).lower()):
            self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.variables).keys():
            return (self.variables[identifier]).returnType()
        elif self.isArray(identifier, lineNo, line)[0] == True:
            arr = self.isArray(identifier, lineNo, line)
            return (self.arrays[arr[1]]).returnType()
        elif identifier in (self.variables).keys():
            return (self.variables[identifier]).returnType()
        elif identifier in (self.constants).keys():
            return (self.constants[identifier]).returnType()
        elif identifier in (self.functions).keys():
            return (self.variables[identifier]).returnType()
        elif identifier in (self.procedures).keys():
            self.err.invaSyn(lineNo, line, int(line.find(identifier)/2), "A procedure has no return value")
        elif any(not self.isValidChar(c) for c in identifier):
            return self.getType(self.getValue(identifier, lineNo, line), lineNo, line)
        else:
            self.err.nameErr(lineNo, line, int(line.find(identifier)/2), identifier)

    def evalExpr(self, expression, lineNo, line):

        expressionWOL = self.removeLiteral(expression, lineNo, line)
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
            if valueStack != []:
                operand1 = valueStack.pop()
            else:
                operand1 = 0

            if operator == '+':
                valueStack.append(operand1 + operand2)
            elif operator == '-':
                valueStack.append(operand1 - operand2)
            elif operator == '*':
                valueStack.append(operand1 * operand2)
            elif operator == '/':
                if operand2 == 0:
                    self.err.runTime(lineNo, line, -1, None, "Zero division error")
                valueStack.append(operand1 / operand2)
            elif operator == 'MOD':
                if operand2 == 0:
                    self.err.runTime(lineNo, line, -1, None, "Zero division error")
                valueStack.append(operand1 % operand2)
            elif operator == 'DIV':
                if operand2 == 0:
                    self.err.runTime(lineNo, line, -1, None, "Zero division error")
                valueStack.append(operand1 // operand2)

        # Iterate through each character in the expression using a position pointer
        pos = -1
        while pos < len(expression)-1:
            pos += 1
            char = expression[pos]
            if char == " ":  # Remove any whitespace from the expression
                pass
            elif char in self.digits:  # If the character is a digit, accumulate the number
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
                while (pos+1 < len(expression) and self.isValidChar(expression[pos+1])):
                    id += expression[pos+1]
                    pos+=1
                    char = expression[pos]
                    
                    if id in precedence.keys() and not self.isValidChar(expression[pos-3]) and not expression[pos+1].isalpha():  
                        # If the first three match the operator, stop to avoid conflict
                        break
                if id in precedence.keys():  # For the word being MOD or DIV
                    while (operatorStack and operatorStack[-1] != '(' and
                        precedence[id] <= precedence.get(operatorStack[-1], 0)):
                        # Apply operators with higher or equal precedence from the stack
                        applyOperator()
                    operatorStack.append(id)
                elif id in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None)
                elif id in self.variables.keys() or id in self.constants.keys():
                    valueStack.append(self.getValue(id, lineNo, line))
                elif id in self.arrays.keys():
                    pos +=1
                    if expression[pos] == "[":
                        pass
                    else:
                        self.err.invaSyn(lineNo, line, (int(line.index(id)+(len(id))//2)), None, "Missing bracket")
                    while expressionWOL[pos]!="]" and pos < len(expression)-1:
                        id += expression[pos]
                        pos += 1
                    if expression[pos] == "]":
                        id += "]"
                    else:
                        self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None, "Unmatched brackets")
                    valueStack.append(self.getValue(id, lineNo, line))
                elif id in self.functions.keys():
                    pos +=1
                    if expression[pos] == "(":
                        pass
                    else:
                        self.err.invaSyn(lineNo, line, (int(line.index(id)+(len(id))//2)), None, "Missing bracket")
                    while expressionWOL[pos]!=")" and pos < len(expression)-1:
                        id += expression[pos]
                        pos += 1
                    if expression[pos] == ")":
                        id += ")"
                    else:
                        self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None, "Unmatched brackets")
                    valueStack.append(self.getValue(id, lineNo, line))
                elif id in self.procedures.keys():
                    self.err.invaSyn(lineNo, line, int(line.find(id)/2), "A procedure has no return value")
                else:
                    self.err.nameErr(lineNo, line, line.index(id)+(len(id)//2), id)
                if not(id in precedence.keys()):
                    type = self.getType(id, lineNo, line)
                    if not(type == "INTEGER" or "REAL"):
                        self.err.typeErr(lineNo, line, line.index(id)+(len(id)//2), id, "INTEGER or REAL")

            elif char == '(':  # If the character is an opening parenthesis, push it to the operator stack
                operatorStack.append(char)

            elif char == ')':  # If the character is a closing parenthesis
                if not operatorStack or '(' not in operatorStack:
                    self.err.invaSyn(lineNo, line, pos, None, "Mismatched parentheses")
                while operatorStack and operatorStack[-1] != '(': 
                    applyOperator()  # Apply operators until the opening parenthesis is encountered
                    if not operatorStack:
                        self.err.invaSyn(lineNo, line, pos, None, "Mismatched parentheses")
                if operatorStack and operatorStack[-1] == '(':
                    operatorStack.pop()  # Pop the opening parenthesis from the stack

            elif char in precedence.keys():

                # See if the operator is valid
                #if not(expression[pos+1] in self.digits or expression[pos+1].isalpha()):
                #    self.err.invaSyn(lineNo, line, pos+1)

                # If the character is an operator
                while (operatorStack and operatorStack[-1] != '(' and
                        precedence[char] <= precedence.get(operatorStack[-1], 0)):
                    applyOperator()   # Apply operators with higher or equal precedence from the stack
                operatorStack.append(char)

            else:
                self.err.typeErr(lineNo, line, pos, char, "INTEGER or REAL")
        while operatorStack:  # Apply any remaining operators in the stack
            applyOperator()
        return valueStack[0]  # The final value in the value stack is the result

    def evalLogic(self, expression, lineNo, line):

        expressionWOL = self.removeLiteral(expression, lineNo, line)
        # Operator precedence dictionary
        precedence = {
            'OR': 1,
            'AND': 2,
            'NOT': 3,
        }
        # Stack to hold operators and values
        operatorStack = []
        valueStack = []



        def applyOperator():  # Helper functions for arithmetic operations
            operator = operatorStack.pop()
            operand2 = valueStack.pop()
            if valueStack != []:
                operand1 = valueStack.pop()
                operand1 = self.boolConvert(operand1)
            else:
                operand1 = ""
            operand2 = self.boolConvert(operand2)

            if operator == 'OR':
                valueStack.append(self.boolConvert(operand1 or operand2))
            elif operator == 'AND':
                valueStack.append(self.boolConvert(operand1 and operand2))
            elif operator == 'NOT':
                if operand1:
                    valueStack.append(self.boolConvert(operand1))
                valueStack.append(self.boolConvert(not operand2))


        # Iterate through each character in the expression using a position pointer
        pos = -1
        oprand = ""
        while pos < len(expression)-1:
            pos += 1
            char = expression[pos]
            
            if char == " ":
                pass
            elif char.isalpha():
                id = char
                # The first char of a identifier can only be a letter but it can be followed by _ and number
                while (pos+1 < len(expression) and self.isValidChar(expression[pos+1])):
                    id += expression[pos+1]
                    pos+=1
                    char = expression[pos]
                    if id in precedence.keys() and not self.isValidChar(expression[pos-3]) and not expression[pos+1].isalpha():  
                        # If the first three match the operator, stop to avoid conflict
                        break
                if id in precedence.keys():
                    if oprand:
                        if self.getType(oprand, lineNo, line) != "BOOLEAN":
                            self.err.typeErr(lineNo, line, expression.find(oprand)+len(oprand)//2, oprand, "BOOLEAN")
                        valueStack.append(self.getValue(oprand, lineNo, line))
                        oprand = ""
                    while (operatorStack and operatorStack[-1] != '(' and
                        precedence[id] <= precedence.get(operatorStack[-1], 0)):
                        # Apply operators with higher or equal precedence from the stack
                        applyOperator()
                    operatorStack.append(id)

                elif id in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None)
                elif id in self.variables.keys() or id in self.constants.keys():
                    oprand += id
                elif id in self.arrays.keys():
                    pos +=1
                    if expression[pos] == "[":
                        pass
                    else:
                        self.err.invaSyn(lineNo, line, (int(line.index(id)+(len(id))//2)), None, "Missing bracket")
                    while expressionWOL[pos]!="]" and pos < len(expression)-1:
                        id += expression[pos]
                        pos += 1
                    if expression[pos] == "]":
                        id += "]"
                    else:
                        self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None, "Unmatched brackets")
                    oprand += id
                elif id in self.functions.keys():
                    pos +=1
                    if expression[pos] == "(":
                        pass
                    else:
                        self.err.invaSyn(lineNo, line, (int(line.index(id)+(len(id))//2)), None, "Missing bracket")
                    while expressionWOL[pos]!=")" and pos < len(expression)-1:
                        id += expression[pos]
                        pos += 1
                    if expression[pos] == ")":
                        id += ")"
                    else:
                        self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None, "Unmatched brackets")
                    oprand += id
                elif id in self.procedures.keys():
                    self.err.invaSyn(lineNo, line, int(line.find(id)/2), "A procedure has no return value")
                else:
                    oprand += id
                    

            elif char == '(':  # If the character is an opening parenthesis, push it to the operator stack
                if oprand:
                    if oprand:
                        if self.getType(oprand, lineNo, line) != "BOOLEAN":
                            self.err.typeErr(lineNo, line, expression.find(oprand)+len(oprand)//2, oprand, "BOOLEAN")
                        valueStack.append(self.getValue(oprand, lineNo, line))
                        oprand = ""
                operatorStack.append(char)

            elif char == ')':  # If the character is a closing parenthesis
                if oprand:
                        if self.getType(oprand, lineNo, line) != "BOOLEAN":
                            self.err.typeErr(lineNo, line, expression.find(oprand)+len(oprand)//2, oprand, "BOOLEAN")
                        valueStack.append(self.getValue(oprand, lineNo, line))
                        oprand = ""
                if not operatorStack or '(' not in operatorStack:
                    self.err.invaSyn(lineNo, line, pos, None, "Mismatched parentheses")
                while operatorStack and operatorStack[-1] != '(': 
                    applyOperator()  # Apply operators until the opening parenthesis is encountered
                    if not operatorStack:
                        self.err.invaSyn(lineNo, line, pos, None, "Mismatched parentheses")
                if operatorStack and operatorStack[-1] == '(':
                    operatorStack.pop()  # Pop the opening parenthesis from the stack

            else:
                oprand += char
        if oprand:
            if self.getType(oprand, lineNo, line) != "BOOLEAN":
                self.err.typeErr(lineNo, line, expression.find(oprand)+len(oprand)//2, oprand, "BOOLEAN")
            valueStack.append(self.getValue(oprand, lineNo, line))
            oprand = ""
        while operatorStack:  # Apply any remaining operators in the stack
            applyOperator()
        return valueStack[0]  # The final value in the value stack is the result
    
    def evalRelation(self, expression, lineNo, line):
        pos = -1
        id = ""
        expressionWOL = self.removeLiteral(expression, lineNo, line)
        while pos < len(expression)-1:
            pos += 1
            c = expression[pos]
            cW = expressionWOL[pos]
            if cW in "><=":
                left = id.strip()
                id = ""
                if cW == "<":
                    if expression[pos+1] in ">=":
                        op = "<"+expression[pos+1]
                        pos+=1
                    else:
                        op = "<"
                elif cW == ">":
                    if expression[pos+1] == "=":
                        op = ">="
                        pos+=1
                    else:
                        op = ">"
                elif cW == "=":
                    op = "="
            else:
                id += c
        right = id.strip()
        left = self.getValue(left, lineNo, line)
        right = self.getValue(right, lineNo, line)
        if op == ">":
            if left > right:
                return "TRUE"
            else:
                return "FALSE"
        elif op == "<":
            if left < right:
                return "TRUE"
            else:
                return "FALSE"
        elif op == ">=":
            if left >= right:
                return "TRUE"
            else:
                return "FALSE"
        elif op == "<=":
            if left <= right:
                return "TRUE"
            else:
                return "FALSE"
        elif op == "=":
            if left == right:
                return "TRUE"
            else:
                return "FALSE"
        elif op == "<>":
            if left != right:
                return "TRUE"
            else:
                return "FALSE"

    def strComb(self, expression, lineNo, line):
        tokens = expression.split("&")
        string = '"'
        for token in tokens:
            token = token.strip()
            if self.getType(token, lineNo, line) == "STRING":
                string += self.getString(token, lineNo, line)
            else:
                self.err.typeErr(lineNo, line, (line.find(token)+len(token))//2)
        string += '"'
        return string

##### Classes #####

class variable:
    def __init__(self, identifier, type, value = None):
        self.identifier = identifier
        self.type = type
        self.value = value
    
    def returnValue(self):
        return self.value
    def returnType(self):
        return self.type

class array:
    def __init__(self, identifier, type, bounds):
        self.idenifier = identifier
        self.type = type
        self.bounds = bounds
        self.err = error()

        element = None
        array = []
        for bound in reversed(bounds):
            for i in range(bound[1]-bound[0]+1):
                    array.append(element)
            element = array
            array = []
        self.values = element
    
    def returnType(self):
        return self.type

    def injectValue(self, indexes, value, lineNo, line):
        element = self.values
        for index, bound in zip(indexes, self.bounds):
            if not(index in range(bound[0], bound[1]+1)):
                self.err.indexErr(lineNo, line, None)
            if index == indexes[-1]:
                element[index-bound[0]] = value
            else:
                element = element[index-bound[0]]

    def returnValue(self, indexes, lineNo, line):
        element = self.values
        for index, bound in zip(indexes, self.bounds):
            if not(index in range(bound[0], bound[1]+1)):
                self.err.indexErr(lineNo, line, None)
            if index == indexes[-1]:
                return element[index-bound[0]]
            else:
                element = element[index-bound[0]]

class funcError(error):

    def __init__(self, initialNo, initialLine, identifier):
        super().__init__()
        self.initialNo = initialNo
        self.initialLine = initialLine
        self.identifier = identifier

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        if not method:
            raise Exception("Method %s not implemented" % attr)
        if callable(method):
            printRed("At line "+ str(self.initialNo)+", in <"+str(self.identifier)+">")
            printRed("\t"+str(self.initialLine))
        return method
    
    def message(self, mess):
        printRed (mess)
        quit()


class funcInterpreter(interpreter):
    def __init__(self, initialNo, initialLine, identifier):
        super().__init__()
        self.err = funcError(initialNo, initialLine, identifier)


class function:
    def __init__(self, identifier, type, initialpos, lines, parameters = {} ):
        self.identifier = identifier
        self.type = type
        self.parameters = parameters
        self.lines = lines
        self.initialpos = initialpos
        self.err = error()      
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = funcInterpreter(lineNo, line, self.identifier)
        for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
            self.inter.identifiers.append(name)
            self.inter.variables[name] = variable(name, type, arg)
        return self.inter.run(self.lines, self.initialpos, 1)

class procedure(function):
    def __init__(self, identifier, type, initialpos, lines, byref, parameters={}):
        super().__init__(identifier, type, initialpos, lines, parameters)
        self.byref = byref

    def returnType(self):
        return None
    
    def returnValue(self, args, lineNo, line, byref):
        self.inter = funcInterpreter(lineNo, line, self.identifier)
        if not byref:
            for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
                self.inter.identifiers.append(name)
                self.inter.variables[name] = variable(name, type, arg)
        else:
            for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
                self.inter.identifiers.append(name)
                self.inter.variables[name] = arg
        return self.inter.run(self.lines, self.initialpos, 1)