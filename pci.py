import builtinFunction as bif
from datetime import datetime, date
import re
import copy
from settings import *

def printRed(skk): print("\033[91m {}\033[00m" .format(skk))

errorStack = []

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
            printRed (description)
        quit()
    def nameConErr(self, lineNo, line, pos, detail = None, description = None):
        printRed ("Name error: <" + str(detail) + "> conflicted with "+description+" at line " + str(lineNo))
        printRed ("\t" + str(line))
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
        exp = description[0]
        got = description[1]
        printRed ("Argument Error: at line " + str(lineNo))
        printRed ("\t" + str(line))
        if pos > -1:
            printRed ("\t" + " "*pos + "^" )
        printRed ("Expect "+str(exp)+" argument(s), got "+str(got))     
        quit()
    def valErr(self, lineNo, line, pos, detail = None, description = None):
        printRed("Value error: '"+str(detail)+"' does not match format '"+description+"' at line "+str(lineNo))
        quit()
    def fileNF(self, lineNo, line, pos, detail = None, description = None):
        printRed("File not found error: No such file opened <"+detail+"> at line "+ str(lineNo))
        quit()
    def attrErr(self, lineNo, line, pos, detail = None, description = None):
        printRed("Attribute error: <"+detail+"> has no attribute <"+description+"> at line "+ str(lineNo))
        quit()
    def attrUnAss(self, lineNo, line, pos, detail = None, description = None):
        printRed("Attribute error: <"+detail+"> 's' <"+description+"> is not muttable at line "+ str(lineNo))
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
        self.files = {}
        self.pointers = {}
        self.enumerateds = {}
        self.enuIds = []
        self.records = {}
        self.classes = {}

        self.returnType = None

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
            #'EOF',
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
            #'RAND',
            #'RANDOM',
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
                    "DATE",
                    "CLASS",
                    "OBJECT"
                      ]

    def initRun(self, code):
        lines = code.split("\n")
        self.run(lines, 1, 1)

    # An individual run func will take:
    # lines: A list of string lines with outmost indent removed
    # innitialPos: the postion of the first line in the entire code the first line is 1
    # selfPos: the postion of each iteration in the sub code block, advance with each line
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
        if line == "":
            return 0
        lineWOL = self.removeLiteral(line, lineNo, line)
        if "//" in lineWOL:  # get rid of comments
            line = line[0 : lineWOL.find("//")]
        if line == "":
            return 0
        if line.startswith(" "):
            self.err.indentErr(lineNo, line, -1)
        if arrowReplace:
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
        elif identifier == "OPENFILE":
            self.exeOpenfile(lineNo, line)
            return 0
        elif identifier == "READFILE":
            self.exeReadfile(lineNo, line)
            return 0
        elif identifier == "WRITEFILE":
            self.exeWritefile(lineNo, line)
            return 0
        elif identifier == "CLOSEFILE":
            self.exeClosefile(lineNo, line)
            return 0
        elif identifier == "TYPE":
            return self.exeType(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "CLASS":
            return self.exeClass(lineNo, line, lines, innitialPos, selfPos)

        elif identifier in self.identifiers:
            self.exeAssign(lineNo, line)
            return 0
        else:
            self.err.invaSyn(lineNo, line, -1)

    # To check is a char can be used in an identifier
    def isValidChar(self, id):
        return id.isalpha() or id in self.digits + "_"

    # check if a token is a array with indexes. return identifier and indexes in a list
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
    
    # check for function, return if its func, proc or method in a object, and arguments
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
            if len(args)< len(self.functions[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                [len(self.functions[name].parameters), len(args)])
            elif len(args)> len(self.functions[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                [len(self.functions[name].parameters), len(args)])
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

            if len(args)< len(self.procedures[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                [len(self.procedures[name].parameters), len(args)])
            elif len(args)> len(self.procedures[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                [len(self.procedures[name].parameters), len(args)])
            if not byref:
                for i, arg in zip(range(len(args)), args):
                    args[i] = self.getValue(arg, lineNo, line)
            else:
                for i, arg in zip(range(len(args)), args):
                    if not arg in self.variables.keys():
                        self.err.nameErr(lineNo, line, -1, arg, "VARIABLE")
                    args[i] = self.variables[arg]
            return ["PROC", name, args, byref]
        if ("(" and ")") in identifierWOLiteral and ((identifier[0: identifier.find("(")]) in self.classes.keys() and
                                                      identifierWOLiteral.endswith(")")):
            identifier = identifier.strip()
            name = identifier[0: identifier.find("(")]
            name = name.strip()
            argStr = identifier[identifier.find("(")+1: -1].strip()
            args = self.commaSplit(argStr, lineNo, line)
            if len(args)< len(self.classes[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                [len(self.classes[name].parameters), len(args)])
            elif len(args)> len(self.classes[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                [len(self.classes[name].parameters), len(args)])
            paraTypes = self.classes[name].parameters.values()
            for i, arg, type in zip(range(len(args)), args, paraTypes):
                if self.getType(arg, lineNo, line) != type:
                    self.err.typeErr(lineNo, line, -1, arg, type)
                args[i] = self.getValue(arg, lineNo, line)
            return ["CLASS", name, args, False]        
        
        elif identifierWOLiteral in self.functions.keys(): #and self.functions[identifierWOLiteral].parameters == {}:
            #return ["FUNC", identifierWOLiteral, [], False]
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)-1, None, "Brackets required")
        elif identifierWOLiteral in self.procedures.keys(): #and self.procedures[identifierWOLiteral].parameters == {}:
            #return ["PROC", identifierWOLiteral, [], False]
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)-1, None, "Brackets required")
        elif identifierWOLiteral in self.classes.keys(): #and self.classes[identifierWOLiteral].parameters == {}:
            #return ["CLASS", identifierWOLiteral, [], False]
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)-1, None, "Brackets required")
        else:
            return [False, None, None, None]
    
    # check if a string matches the format of date in dd/mm/yyyy
    def isDate(self, id, lineNo, line):
        if re.match(r'^\d{2}/\d{2}/\d{4}$', id):
            try:
                return bool(datetime.strptime(id, "%d/%m/%Y"))
            except ValueError:
                self.err.valErr(lineNo, line, -1, id, "DD/MM/YYYY")
        else:
            return False
                
    # takes string TRUE and FALSE to python booleans, bi-directional
    def boolConvert(self, input):
        if input == "TRUE":
            return True
        elif input == "FALSE":
            return False
        elif input == True:
            return "TRUE"
        elif input == False:
            return "FALSE"
    
    # removes the identifier's previous occurance to enable redeclare
    def initId(self, identifier, lineNo =0, line =None):
        if identifier[0].isalpha():
            for c in identifier[1:]:
                if not self.isValidChar(c):
                    self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "Invalid identifier")
        else:
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "Invalid identifier")
        if identifier in self.identifiers:
            if identifier in self.enuIds:
                for e in self.enumerateds:
                    for v in e.values:
                        if identifier == v:
                            self.err.nameConErr(lineNo, line, -1, identifier, v + " in "+e.identifier)
            if identifier in self.classes.keys():
                self.err.nameConErr(lineNo, line, -1, identifier, identifier + " class")
            self.identifiers.pop((self.identifiers.index(identifier)))
            if identifier in self.variables.keys():
                del (self.variables[identifier])
            elif identifier in self.arrays.keys():
                del (self.arrays[identifier])
            elif identifier in self.functions.keys():
                del (self.functions[identifier])
            elif identifier in self.procedures.keys():
                del (self.procedures[identifier])
            elif identifier in self.constants.keys():
                del (self.constants[identifier])
            elif identifier in self.enumerateds.keys():
                self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
            elif identifier in self.pointers.keys():
                self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
            elif identifier in self.records.keys():
                self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.keywords or (self.keywords).lower()):
            self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
    
    # in func/proc, combine the parameters with global dictionary, keep conflick in a temp dict
    def keepId(self, identifier):
        self.tempvariables = {}
        self.tempconstants = {}
        self.temparrays = {}
        self.tempfunctions = {}
        self.tempprocedures = {}
        if identifier in self.identifiers:
            self.identifiers.pop((self.identifiers.index(identifier)))
            if identifier in self.variables.keys():
                self.tempvariables[identifier] = self.variables.pop(identifier)
            elif identifier in self.arrays.keys():
                self.temparrays[identifier] = self.arrays.pop(identifier)
            elif identifier in self.functions.keys():
                self.tempfunctions[identifier] = self.functions.pop(identifier)
            elif identifier in self.procedures.keys():
                self.tempprocedures[identifier] = self.procedures.pop(identifier)
            elif identifier in self.constants.keys():
                self.tempconstants[identifier] = self.constants.pop(identifier)

    # After func/proc, remove parameters and take temp dict back to global dictionary
    def resumeId(self):
        for id, value in zip(self.tempvariables.keys(), self.tempvariables.values()):
            self.variables[id] = value
        for id, value in zip(self.temparrays.keys(), self.temparrays.values()):
            del self.variables[id]
            self.arrays[id] = value
        for id, value in zip(self.tempfunctions.keys(), self.tempfunctions.values()):
            del self.variables[id]
            self.functions[id] = value
        for id, value in zip(self.tempprocedures.keys(), self.tempprocedures.values()):
            del self.variables[id]
            self.pointers[id] = value
        for id, value in zip(self.tempconstants.keys(), self.tempconstants.values()):
            del self.variables[id]
            self.constants[id] = value

    # checks if a token is object with attr/method, retrun attr name, args/indexes
    def isObject(self, identifier, lineNo, line):
        if "." in identifier: 
            obj = identifier[0:identifier.find(".")].strip()
            attr = identifier[identifier.find(".")+1:].strip()
            if self.getType(obj, lineNo, line) in self.records.keys():
                rec = self.getValue(obj, lineNo, line)
                if not attr in rec.inter.variables.keys():
                    self.err.attrErr(lineNo, line, -1, obj, attr)
                return ["RECORD", obj, attr]
            elif self.variables[obj].returnType() == "OBJECT":
                args = []
                indexes = []
                if self.variables[obj].value == None:
                    self.err.invaSyn(lineNo, line, line.find(obj)+len(obj)//2, None, obj+" has no class assigned to it")
                if self.variables[obj].value.inter.isFunction(attr, lineNo, line)[0]:
                    func = self.variables[obj].value.inter.isFunction(attr, lineNo, line)
                    attr = func[1]
                    args = func[2]
                if self.variables[obj].value.inter.isArray(identifier, lineNo, line)[0]:
                    arr = self.variables[obj].value.inter.isArray(attr, lineNo, line)
                    attr = arr[1]
                    indexes = arr[2]
                if not attr in self.variables[obj].value.pubIds:
                    self.err.attrErr(lineNo, line, -1, obj, attr)
                return ["OBJECT", obj, attr, args, indexes]
        
        else:
            return [False, None, None]

    # checks if a token is a class with args
    def isClass(self, identifier, lineNo, line):
        identifierWOLiteral = self.removeLiteral(identifier, lineNo, line)
        identifierWOLiteral = identifierWOLiteral.strip()
        if ("(" and ")") in identifierWOLiteral and ((identifier[0: identifier.find("(")]) in self.classes.keys() and
                                                      identifierWOLiteral.endswith(")")):
            identifier = identifier.strip()
            name = identifier[0: identifier.find("(")]
            name = name.strip()
            argStr = identifier[identifier.find("(")+1: -1].strip()
            args = self.commaSplit(argStr, lineNo, line)
            if len(args)!= len(self.classes[name].parameters):
                self.err.argErr(lineNo, line, line.find(args[-1])+len(args[-1])//2, identifier, 
                                len(self.classes[identifier].parameters)-len(args))
            paraTypes = self.classes[name].parameters.values()
            for i, arg, type in zip(range(len(args)), args, paraTypes):
                if self.getType(arg, lineNo, line) != type:
                    self.err.typeErr(lineNo, line, -1, arg, type)
                args[i] = self.getValue(arg, lineNo, line)
            return [True, name, args]
        else:
            return [False, None, None]

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
        return 0
    
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
        elif value in self.enuIds:
            for e in self.enumerateds.values:
                for v, n in zip(e.values, range(len(e.values))):
                    if value == v:
                        valueType = "INTEGER"
                        value = n
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
        elif self.isObject(identifier, lineNo, line)[0] == "RECORD":
                record = self.isObject(identifier, lineNo, line)
                rec = record[1]
                atrr = record[2]
                self.variables[rec].value.inter.variables[atrr].value = value
        else:
            self.err.nameErr(lineNo, line, (line.find(identifier)+len(identifier))//2, identifier)
        return 0

    def exeDeclare(self, lineNo, line, ignore = 8):
        #if line[0:line.find(" ")] != "DECLARE":  # If the DECLARE is typed wrong, call invalSyn
        #    self.err.invaSyn(lineNo, line, 8, None)
        if line.find(":") == -1:
            self.err.invaSyn(lineNo, line, -1, "Missing colon")
        ids = line[ignore: line.find(':')]
        type = line[line.find(':')+1: len(line)]
        type = type.strip()
        ids = self.commaSplit(ids, lineNo, line)
        if type in self.types:  
            for identifier in ids:
                identifier = identifier.strip()

                if type in self.enumerateds.keys():
                    type = "INTEGER"

                self.initId(identifier, lineNo, line)
                self.identifiers.append(identifier)
                self.variables[identifier] = variable(identifier, type)
                if type in self.records.keys():
                    self.variables[identifier].value = copy.deepcopy(self.records[type])
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
            if typeStr in self.records.keys():
                injectVal = copy.deepcopy(self.records[typeStr])
            else:
                injectVal = None
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
                self.initId(identifier, lineNo, line)
                self.identifiers.append(identifier)
                self.arrays[identifier] = array(identifier, typeStr, bounds, injectVal)
            
        else:
            self.err.invaSyn(lineNo, line, (line.find(type)+len(type)//2), None, "Invalid Data Type")
        return 0

    def exeConstant(self, lineNo, line, ignore =8):
        #if line[0:line.find(" ")] != "CONSTANT":  # If the CONSTANT is typed wrong, call invalSyn
        #    self.err.invaSyn(lineNo, line, 8, None)
        if line.find("=") == -1:
            self.err.invaSyn(lineNo, line, -1, "Missing equal sign")
        ids = line[ignore: line.find('=')]
        values = line[line.find('=')+1: len(line)]
        values = self.commaSplit(values, lineNo, line)
        ids = self.commaSplit(ids, lineNo, line)
        
        for identifier, value in zip(ids, values):
            type = self.getType(value, lineNo, line)
            if identifier in self.identifiers:
                self.initId(identifier, lineNo, line)
                self.identifiers.append(identifier)
                self.constants.append(identifier)
            self.constants[identifier] = variable(identifier, type, value)
            #else:
            #    self.err.invaSyn(lineNo, line, int(line.find(type)/2), None, "Invalid Data Type")

    def exeAssign(self, lineNo, line):
        leftStr = line[0: line.find("←")]
        rightStr = line[line.find("←")+1: ]
        lefts = self.commaSplit(leftStr, lineNo, line)
        rights = self.commaSplit(rightStr, lineNo, line)
        for left, right in zip(lefts, rights):
            
            if right.startswith("NEW"):
                cls = right[3:].strip()
                if not self.isClass(cls, lineNo, line)[0]:
                    self.err.invaSyn(lineNo, line, -1, None, "Invalid format")
                if not self.getType(cls, lineNo, line) == "CLASS":
                    self.err.typeErr(lineNo, line, -1, left, "CLASS")
                clss = self.isClass(cls, lineNo, line)
                clsName = clss[1]
                clsArgs = clss[2]
                self.variables[left].value = self.classes[clsName].generateObj(left, clsArgs)
                return 0


            leftType = self.getType(left, lineNo, line)
            rightType = self.getType(right, lineNo, line)
            if rightType[0] == "POINTER":
                if not leftType in self.pointers.keys() or self.pointers[leftType].type != rightType[1]:
                    self.err.typeErr(lineNo, line, -1, left, rightType[1]+" pointer")
                rightType = leftType
            right = self.getValue (right, lineNo, line)
            if left in (self.constants).keys():
                self.err.invaSyn(lineNo, line, (line.find(left)+len(left))//2, None, "A constant is immutable")
            elif leftType != rightType:
                self.err.typeErr(lineNo, line, (line.find(right)+len(right))//2, right, leftType)
            elif left in (self.variables).keys():
                self.variables[left].value = right
            elif (self.isArray(left, lineNo, line))[0] == True:
                self.arrays[self.isArray(left, lineNo, line)[1]].injectValue(self.isArray(left, lineNo, line)[2], right, lineNo, line)
            elif self.isObject(left, lineNo, line)[0] == "RECORD":
                record = self.isObject(left, lineNo, line)
                rec = record[1]
                atrr = record[2]
                self.variables[rec].value.inter.variables[atrr].value = right
            elif self.isObject(left, lineNo, line)[0] == "OBJECT":
                obj = self.isObject(left, lineNo, line)
                name = obj[1]
                attr = obj[2]
                args = obj[3]
                indexes = obj[4]
                if (attr in self.variables[name].value.functions.keys() 
                    or attr in self.variables[name].value.procedures.keys()
                    or attr in self.variables[name].value.constants.keys()):
                    self.err.attrErr
                self.variables[name].value.injectValue(attr, indexes, right, lineNo, line)
            else:
                self.err.nameErr(lineNo, line, (line.find(left)+len(left))//2, left)
            return 0

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
        self.run(temp, startPos, 1)

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
            self.run(linesToExe, startPos+1, 1)
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
        self.run(linesToExe, startPos+1, 1)
        
        if self.getType(expression, endPos+1, endLine) != "BOOLEAN":
            self.err.typeErr(endPos+1, endLine, subLine.find(expression)+len(expression)//2, expression, "BOOLEAN")
        until = self.boolConvert(self.getValue(expression, endPos+1, endLine))
        while not until:
            self.run(linesToExe, startPos, 1)
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

    def exeFunction(self, lineNo, line, lines, innitialPos, selfPos, ignore = 8):
        pos = ignore
        lineWOL = self.removeLiteral(line, lineNo, line)
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                pos -= 1
                break
        identifier = line[ignore:pos+1].strip()
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

        self.initId(identifier, lineNo, line)
        self.identifiers.append(identifier)
        self.functions[identifier] = function(identifier, type, lineNo+1, linesToExe, vars(self), paras)
        return skip
    
    def exeProcedure(self, lineNo, line, lines, innitialPos, selfPos, ignore =9):
        pos = ignore
        lineWOL = self.removeLiteral(line, lineNo, line)
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                pos -= 1
                break
        identifier = line[ignore:pos+1].strip()
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

        self.initId(identifier, lineNo, line)
        self.identifiers.append(identifier)
        self.procedures[identifier] = procedure(identifier, type, lineNo+1, linesToExe, byref, vars(self), paras)
        return skip

    def exeReturn(self, lineNo, line):
        expression = line[6:].strip()
        type = self.getType(expression, lineNo, line)
        if self.returnType == None:
            self.err.invaSyn(lineNo, line, -1, None, "RETURN is only used inside a function")
        elif type != self.returnType:
            self.err.typeErr(lineNo, line, line.find(expression)+len(expression)//2, expression, self.returnType)
        return[0, self.getValue(expression, lineNo, line)]

    def exeCall(self, lineNo, line):
        identifier = line[4:].strip()
        if self.isFunction(identifier, lineNo, line)[0]:
            proc = self.isFunction(identifier, lineNo, line)
            if not proc[0] == "FUNC":
                self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "<"+str(identifier)+"> function is not callable")
            (self.procedures[proc[1]]).returnValue(proc[2], lineNo, line, proc[3])
        elif self.isObject(identifier, lineNo, line)[0] == "OBJECT":
            obj = self.isObject(identifier, lineNo, line)
            name = obj[1]
            attr = obj[2]
            args = obj[3]
            indexes = obj[4]
            if not attr in self.variables[name].value.inter.procedures.keys():
                self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "<"+str(identifier)+"> s not callable")
            self.variables[name].value.attrValue(attr, args, indexes, lineNo, line)
        return 0

    def exeOpenfile(self, lineNo, line):
        pos = 8
        lineWOL = self.removeLiteral(line, lineNo, line)
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                pos -= 1
                break
        identifier = line[8:pos+1].strip()
        identifier = self.getString(identifier, lineNo, line)
        isFor = False
        token = ""
        while pos < len(line)-1:
            pos+=1
            char = line[pos]
            token += char
            if token.strip() == "FOR":
                isFor = True
                token = ""
        if not isFor:
            self.err.invaSyn(lineNo, line, -1, None, "FOR <file mode> expected")
        fileMode = token.strip()
        if not fileMode in ["READ", "WRITE", "APPEND", "RANDOM"]:
            self.err.invaSyn(lineNo, line, line.find(fileMode)+len(fileMode)//2, None, "Invalid file mode")
        elif fileMode == "READ":
            self.files[identifier] = open(identifier, "r")
        elif fileMode == "WRITE":
            self.files[identifier] = open(identifier, "w")
        elif fileMode == "APPEND":
            self.files[identifier] = open(identifier, "a")
        elif fileMode == "RANDOM":
            pass

    def exeReadfile(self, lineNo, line):
        idAndVar = self.commaSplit(line[8:], lineNo, line)
        if len(idAndVar)!=2:
            self.err.invaSyn(lineNo, line, line.find(",", line.find(",")+1), None, None)
        identifier = self.getString(idAndVar[0], lineNo, line)
        variable = idAndVar[1]
        if not variable in self.variables.keys():
            self.err.invaSyn(lineNo, line, line.find(variable)+len(variable)//2, None, "<"+variable+"> is not a variable")
        if self.variables[variable].type != "STRING":
            self.err.typeErr(lineNo, line, line.find(variable)+len(variable)//2, variable, "STRING")
        if not identifier in self.files.keys():
            self.err.fileNF(lineNo, line, -1, identifier, None)
        try:
            t = self.files[identifier].readline()
            self.variables[variable].value = t
        except IOError:
            self.err.invaSyn(lineNo, line, -1, None, "Unsupported operation for the file mode")
    def exeWritefile(self, lineNo, line):
        idAndVar = self.commaSplit(line[9:], lineNo, line)
        if len(idAndVar)!=2:
            self.err.invaSyn(lineNo, line, line.find(",", line.find(",")+1), None, None)
        identifier = self.getString(idAndVar[0], lineNo, line)
        data = idAndVar[1]
        if self.getType(data, lineNo, line) != "STRING":
            self.err.typeErr(lineNo, line, line.find(data)+len(data)//2, variable, "STRING")
        data = self.getString(data, lineNo, line)
        if not identifier in self.files.keys():
            self.err.fileNF(lineNo, line, -1, identifier, None)
        try:
            t = self.files[identifier].write(data+"\n")
        except IOError:
            self.err.invaSyn(lineNo, line, -1, None, "Unsupported operation for the file mode")
    def exeClosefile(self, lineNo, line):
        identifier = self.getString(line[9:].strip(), lineNo, line)
        if not identifier in self.files.keys():
            self.err.fileNF(lineNo, line, -1, identifier, None)
        self.files[identifier].close()
        del self.files[identifier]
    
    def exeType(self, lineNo, line, lines, innitialPos, selfPos):
        lineWOL = self.removeLiteral(line, lineNo, line)
        if "=" in lineWOL:
            ids = line[4: line.find('=')]
            values = line[line.find('=')+1: len(line)].strip()
            ids = self.commaSplit(ids, lineNo, line)
            if values.startswith("^"):
                type = values[1:]
                if not type in self.types:
                    self.err.invaSyn(lineNo, line, line.find(type)+len(type)//2, type, "Invalid data type")
                for identifier in ids:
                    self.initId(identifier, lineNo, line)
                    self.identifiers.append(identifier)
                    self.types.append(identifier)
                    self.pointers[identifier]=(pointer(identifier, type))
                return 0
            elif values.startswith("(") or values .endswith(")"):
                if not (values .endswith(")") or values.startswith("(")):
                    self.err.invaSyn(lineNo, line, -1, None, "Unmatched colon")
                values = values[1:-1]
                values = self.commaSplit(values, lineNo, line)
                for identifier in ids:
                    self.initId(identifier, lineNo, line)
                    self.identifiers.append(identifier)
                    self.enumerateds[identifier] = (enumerated(identifier))
                    for v in values:
                        if v==identifier:
                            self.err.nameConErr(lineNo, line, -1, v, "Type name")
                        self.initId(v, lineNo, line)
                        self.identifiers.append(v)
                        self.enuIds.append(v)
                        self.enumerateds[identifier].values.append(v)
                    self.types.append(identifier)
                    self.identifiers.append(identifier)
                return 0
        else:
            identifier = line[4:].strip()
            self.initId(identifier, lineNo, line)

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
                if subLine.startswith("ENDTYPE"):
                    if subLine.rstrip() != "ENDTYPE":
                        self.err.invaSyn(innitialPos + pos, subLine, -1, None, "Should be ENDTYPE")
                    end = True
                    endPos = pos
                    break
            if not end:
                self.err.invaSyn(lineNo, line, -1, None, "ENDTYPE expected")
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
                   if not subLine.startswith("DECLARE"):
                       self.err.invaSyn(lineNo, line, pos, None, "A record type can only declare variables")
                   linesToExe.append(subLine)
                else:
                    self.err.indentErr(selfPos + pos+1, subLine, 0, None, "Unexpected indent")
            
            self.types.append(identifier)
            self.identifiers.append(identifier)
            self.records[identifier] = record(identifier, None, innitialPos, linesToExe, {}, lineNo, line)
            return skip

    def exeClass(self, lineNo, line, lines, innitialPos, selfPos, ignore = 5):
        pos = ignore
        lineWOL = self.removeLiteral(line, lineNo, line)
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if not self.isValidChar(char):
                pos -= 1
                break
        identifier = line[ignore:pos+1].strip()
        parasStr = ""
        token = ""
        inherits = False
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
            if token.strip() == "INHERITS":
                inherits = True
                token = ""
        if inherits:
            parentStr = token.strip()
            if not(type in self.classes.keys()):
                self.err.invaSyn(lineNo, line, line.find(type)+len(type)//2, None, str(type)+" is not a valid class")
            else:
                parent = self.classes[parentStr]
        else:
            parent = None

        #if parasStr.startswith("BYREF"):
        #        self.err.invaSyn(lineNo, line, line.find("BYREF")+len("BYREF")//2, None, 
        #                         "Parameters should not be passed by reference to a function")
        #elif parasStr.startswith("BYVAL"):
        #    parasStr = parasStr[5:].strip()

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
            if subLine.startswith("ENDCLASS"):
                if subLine.rstrip() != "ENDCLASS":
                    self.err.invaSyn(innitialPos + pos, subLine, -1, None, "Should be ENDCLASS")
                end = True
                endPos = pos
                break
        if not end:
            self.err.invaSyn(lineNo, line, -1, None, "ENDCLASS expected")
        
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

        self.initId(identifier, lineNo, line)
        self.identifiers.append(identifier)
        self.classes[identifier] = cls(identifier, lineNo+1, linesToExe, parent, paras)
        return skip


##### Utility functions #####
    
    def splitBy(self,splitters, expressionWOL, expression):
        tokens = re.split(splitters, expressionWOL)
        precedences = re.findall(splitters, expressionWOL)

        exprListWOL = [(tokens[i] if i < len(tokens) else "", 
                        precedences[i] if i < len(precedences) else "") 
                        for i in range(max(len(tokens), len(precedences)))]
        exprListWOL = [item for pair in exprListWOL for item in pair]
        exprListWOL = list(filter(lambda s: s != "", exprListWOL))
        exprList = []
        pos = 0
        for t in exprListWOL:
            exprList.append(expression[pos: pos+len(t)].strip())
            pos += len(t)
        return exprList

    # remove literal values, keep the bounds like quotes, everything removed is replaced by space
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
            elif c == "(":
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
    
    # split a token by commas in list, not affected by commas in string or other literals
    def commaSplit(self, expression, lineNo, line):
        if expression == "":
            return []
        tokens = []
        expressionWOLiteral = self.removeLiteral(expression, lineNo, line)
        tokensWOL = expressionWOLiteral.split(",")  # Seprate by commas
        pos = 0
        for tokenWOL in tokensWOL:
            tokens.append((expression[pos: pos + len(tokenWOL)]).strip())
            pos += len(tokenWOL)+1
        return tokens

    # return the value of a token, literal or identifer
    # for int and real, it will be returned as int or float
    # for string and char value, it will be returned as string with quotes like '"test"'
    # for other types the value will be directly returned as string "TRUE"
    def getValue(self, identifier, lineNo, line):
        identifierWOLiteral = self.removeLiteral(identifier, lineNo, line)
        if not identifier:
            return identifier
        
        elif identifier in self.enuIds:
            for e in self.enumerateds.values():
                for v, n in zip(e.values, range(len(e.values))):
                    if identifier == v:
                        result = n

        elif any(op in identifierWOLiteral for op in self.logicOperators):
            valid = False
            for op in self.logicOperators:
                pos = identifierWOLiteral.find(op)
                while pos != -1:
                    if ((not self.isValidChar(identifierWOLiteral[pos-1]) or pos-1 == -1) and
                        not identifierWOLiteral[pos+len(op)].isalpha()):
                        valid = True
                    pos = identifierWOLiteral.find(op, pos+1)

            if valid:
                result = self.evalLogic(identifier, lineNo, line)
            else:
                pass
        elif any(op in identifierWOLiteral for op in self.relationOperators):
            result = self.evalRelation(identifier, lineNo, line)
        elif any(op in identifierWOLiteral for op in self.operators):  # apart from string literal, there is a operator
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
                result = self.evalExpr(identifier, lineNo, line)
            else:
                pass
        elif "&" in identifierWOLiteral:  # apart from string literal, there is a &
            result = self.strComb(identifier, lineNo, line) 
        elif all(n in self.digits for n in identifier) or (identifier.startswith("-") and 
                                                           all(n in self.digits for n in identifier[1:])):  # it is a number
            if "." in identifier:
                result = float(identifier)
            result = int(identifier)
        
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
                result = identifier
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
                result = identifier
        
        elif self.isDate(identifier, lineNo, line):
            result = identifier
        
    
        elif identifier.startswith("^"):
            # TODO support array
            identifier = identifier[1:]
            type = self.getType(identifier, lineNo, line)
            if not identifier in self.variables.keys():
                self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, identifier + " is not a variable")
            result = copy.deepcopy(self.variables[identifier])
        elif identifier.endswith("^"):
            identifier = identifier[0:-1]
            type = self.getType(identifier, lineNo, line)
            if not type in self.pointers.keys():
                 self.err.typeErr(lineNo, line, -1, identifier, "pointer")
            result = self.variables[identifier].value.value
        
        elif self.isObject(identifier, lineNo, line)[0] == "RECORD":
            record = self.isObject(identifier, lineNo, line)
            rec = record[1]
            attr = record[2]
            rec = self.getValue(rec, lineNo, line)
            result = rec.inter.variables[attr].value
        elif self.isObject(identifier, lineNo, line)[0] == "OBJECT":
            obj = self.isObject(identifier, lineNo, line)
            name = obj[1]
            attr = obj[2]
            args = obj[3]
            indexes = obj[4]
            if attr in self.variables[name].value.inter.procedures.keys():
                 self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "A procedure has no result = value")
            result = self.variables[name].value.attrValue(attr, args, indexes, lineNo, line)
        elif identifier in (self.keywords or (self.keywords).lower()):
            self.err.invaSyn(lineNo, line, int((int(line.find(identifier, 7)+len(identifier))/2)), None)
        elif identifier in (self.variables).keys():
            result = (self.variables[identifier]).returnValue()
        elif identifier in (self.constants).keys():
            result = (self.constants[identifier]).returnValue()
        elif self.isArray(identifier, lineNo, line)[0] == True:
            arr = self.isArray(identifier, lineNo, line)
            result = (self.arrays[arr[1]]).returnValue(arr[2], lineNo, line)
        elif self.isFunction(identifier, lineNo, line)[1] == "EOF":
            func = self.isFunction(identifier, lineNo, line)
            identifier = self.getString(func[2][0], lineNo, line)
            if not identifier in self.files.keys():
                self.err.fileNF(lineNo, line, -1, identifier, None)
            pos = self.files[identifier].tell()
            if self.files[identifier].readline() == "":
                result = "TRUE"
            else:
                result = "FALSE"
            self.files[identifier].seek(pos)
            result = result
        elif self.isFunction(identifier, lineNo, line)[0] == "FUNC":
            func = self.isFunction(identifier, lineNo, line)
            result = (self.functions[func[1]]).returnValue(func[2], lineNo, line)
        elif self.isFunction(identifier, lineNo, line)[0] == "PROC":
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "A procedure has no result = value")
        elif self.isFunction(identifier, lineNo, line)[0] == "CLASS":
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "A class cannot be directly referred")
        elif identifier in ["TRUE", "FALSE"]:
            result = identifier
        elif self.getType(identifier, lineNo, line) in self.records.keys():
            self.err.invaSyn(lineNo, line, line.find(identifier), None, "A record type cannot be directly referred")
        else:
            self.err.nameErr(lineNo, line, int(line.find(identifier)/2), identifier)
        
        if result == None:
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, str(identifier)+" is not assigned")
        return result

    # get the value as a string ready to be printed
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

    # return type of a token as a string
    # NOTICE the priorty: literal > expression > identifier
    def getType(self, identifier, lineNo, line):
        identifier = str(identifier)
        identifier = identifier.strip()
        identifierWOLiteral = self.removeLiteral(identifier, lineNo, line)

        ###Literals###
        if identifier in self.enuIds:
            for e in self.enumerateds.values():
                for v in e.values:
                    if identifier == v:
                        return "INTEGER"
        elif all(n in self.digits+"." for n in identifier):  # it is a number
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
        
        #####expression######
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
                return self.getType(self.evalLogic(identifier, lineNo, line), lineNo, line)
            else:
                pass
        elif any(op in identifierWOLiteral for op in self.relationOperators):
            return self.getType(self.evalRelation(identifier, lineNo, line), lineNo, line)
        elif any(op in identifierWOLiteral for op in self.operators):  # apart from string literal, there is a operator
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
                return self.getType(self.evalExpr(identifier, lineNo, line), lineNo, line)
            else:
                pass
        elif "&" in identifierWOLiteral:  # apart from string literal, there is a &
            return self.getType(self.strComb(identifier, lineNo, line), lineNo, line)

        #####identifier######
        if identifier.startswith("^"):
            identifier = identifier[1:]
            type = self.getType(identifier, lineNo, line)
            if not identifier in self.variables.keys():
                self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, identifier + " is not a variable")
            return ["POINTER", type]
        elif identifier.endswith("^"):
            identifier = identifier[0:-1]
            type = self.getType(identifier, lineNo, line)
            if not type in self.pointers.keys():
                 self.err.typeErr(lineNo, line, -1, identifier, "pointer")
            return self.getType(self.variables[identifier].value.identifier, lineNo, line)

        elif self.isObject(identifier, lineNo, line)[0] == "RECORD":
            record = self.isObject(identifier, lineNo, line)
            rec = record[1]
            attr = record[2]
            recVal = self.getValue(rec, lineNo, line)
            return recVal.inter.variables[attr].type

        elif self.isObject(identifier, lineNo, line)[0] == "OBJECT":
            obj = self.isObject(identifier, lineNo, line)
            name = obj[1]
            attr = obj[2]
            return self.variables[name].value.attrType(attr)

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
        elif self.isFunction(identifier, lineNo, line)[0] == "FUNC":
            func = self.isFunction(identifier, lineNo, line)
            return (self.functions[func[1]]).returnType()
        elif self.isFunction(identifier, lineNo, line)[0] == "PROC":
            self.err.invaSyn(lineNo, line, line.find(identifier)+len(identifier)//2, None, "A procedure has no return value")
        elif self.isFunction(identifier, lineNo, line)[0] == "CLASS":
            return "CLASS"
        elif any(not self.isValidChar(c) for c in identifier):
            return self.getType(self.getValue(identifier, lineNo, line), lineNo, line)
        else:
            self.err.nameErr(lineNo, line, int(line.find(identifier)/2), identifier)

    # evaluate math expression
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

        splitters = r'(?<![a-zA-Z_])MOD(?![a-zA-Z_])|(?<![a-zA-Z_])DIV(?![a-zA-Z_])|\+|-|\*|/'
        exprList = self.splitBy(splitters, expressionWOL, expression)
        
        if (exprList[0] in ["+", "*", "/", "MOD", "DIV"]) or (exprList[-1] in precedence.keys()):
            self.err.invaSyn(lineNo, line, line.find(exprList[0]), None, "Invalid expression")
        last = False
        for item in exprList[1:-1]:
            if (item in ["+", "*", "/", "MOD", "DIV"]) and last:
                self.err.invaSyn(lineNo, line, line.find(item), None, "Invalid expression")
            elif item in precedence.keys():
                last = True
            else:
                last = False

        # Iterate through each character in the expression using a position pointer
        for token in exprList:
            char = token[0]
            if all(c == " " for c in token):  # Remove any whitespace from the expression
                pass
            elif char in self.digits:  # If the character is a digit, accumulate the number
                if not all(n in self.digits+"." for n in token):
                    self.err.invaSyn(lineNo, line, line.find(token)+len(token)//2, None, "Invalid number")
                if token.count(".")>1:
                    self.err.invaSyn(lineNo, line, line.find(token)+len(token)//2, None, "Invalid number")
                if "." in token:  # Push the float or int value to the stack
                    valueStack.append(float(token))
                else:
                    valueStack.append(int(token))

            elif char.isalpha():

                # The first char of a identifier can only be a letter but it can be followed by _ and number
                #if not all(t.isalpha() or t =="_" for t in token):
                #    self.err.invaSyn(lineNo, line, line.find(token)+len(token)//2, None, "Invalid identifier")
                id = token
                if id in precedence.keys():  # For the word being MOD or DIV
                    while (operatorStack and operatorStack[-1] != '(' and
                        precedence[id] <= precedence.get(operatorStack[-1], 0)):
                        # Apply operators with higher or equal precedence from the stack
                        applyOperator()
                    operatorStack.append(id)
                elif id in (self.keywords or (self.keywords).lower()):
                    self.err.invaSyn(lineNo, line, int((int(line.index(id)+len(id))/2)), None)
                else:
                    type = self.getType(id, lineNo, line)
                    if type != "INTEGER" and type != "REAL":
                         self.err.typeErr(lineNo, line, line.index(id)+(len(id)//2), id, "INTEGER or REAL")
                    value = self.getValue(id, lineNo, line)
                    valueStack.append(value)

            elif char == '(':  # If the character is an opening parenthesis,the whole praenthesis value to value stack
                if not token.endswith(")"):
                    self.err.invaSyn(lineNo, line, line.find(token)+len(token)//2, None, "Unmatched brackets")
                token = token[1:-1]
                valueStack.append(self.getValue(token, lineNo, line))


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
                self.err.typeErr(lineNo, line, line.find(token)+len(token)//2, char, "INTEGER or REAL")
        while operatorStack:  # Apply any remaining operators in the stack
            applyOperator()
        return valueStack[0]  # The final value in the value stack is the result

    # evaaluate ligic expression
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
    
    # evaluate relational expression
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

    # evaluate & operation
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
# these classes will be the value of a identifier in the dictionary with the identifier as the key
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
    def __init__(self, identifier, type, bounds, initVal = None):
        self.idenifier = identifier
        self.type = type
        self.bounds = bounds
        self.err = error()

        element = initVal
        array = []
        for bound in reversed(bounds):
            for i in range(bound[1]-bound[0]+1):
                    array.append(copy.deepcopy(element))
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
        errorStack.append([initialNo, initialLine, identifier])
        if len(errorStack) > maxRecur:
            printRed("At line "+ str(initialNo)+", in <"+str(identifier)+">")
            printRed("\t"+str(initialLine))
            printRed("Maximum recursion depth of "+ str(maxRecur) +" has been reached")
            quit()

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        if not method:
            raise Exception
        if callable(method):
            for e in errorStack:
                initialNo = e[0]
                initialLine = e[1]
                identifier = e[2]
                printRed("At line "+ str(initialNo)+", in <"+str(identifier)+">")
                printRed("\t"+str(initialLine))
        return method
    
    def message(self, mess):
        printRed (mess)
        quit()

# the interpreter for function class, replaces error class with funcError, 
# which can output postion of where it is called
class funcInterpreter(interpreter):
    def __init__(self, initialNo, initialLine, identifier):
        super().__init__()
        self.err = funcError(initialNo, initialLine, identifier)

class function:
    def __init__(self, identifier, type, initialpos, lines, attributes, parameters = {} ):
        self.identifier = identifier
        self.type = type
        self.parameters = parameters
        self.lines = lines
        self.initialpos = initialpos
        self.attributes = attributes 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = funcInterpreter(lineNo, line, self.identifier)
        self.inter.keepId(None)
        for attribute, value in self.attributes.items():
            setattr(self.inter, attribute, value)
        for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
            self.inter.keepId(name)
            self.inter.identifiers.append(name)
            self.inter.variables[name] = variable(name, type, arg)
        self.inter.returnType = self.type
        result =  self.inter.run(self.lines, self.initialpos, 1)
        self.inter.resumeId()
        errorStack.pop()
        return result

class procedure(function):
    def __init__(self, identifier, type, initialpos, lines, byref, attributes, parameters={}):
        super().__init__(identifier, type, initialpos, lines, parameters)
        self.byref = byref
        self.attributes = attributes 

    def returnType(self):
        return None
    
    def returnValue(self, args, lineNo, line, byref):
        self.inter = funcInterpreter(lineNo, line, self.identifier)
        self.inter.keepId(None)
        for attribute, value in self.attributes.items():
            setattr(self.inter, attribute, value)
        if not byref:
            for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
                self.inter.keepId(name)
                self.inter.identifiers.append(name)
                self.inter.variables[name] = variable(name, type, arg)
        else:
            for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
                self.inter.keepId(name)
                self.inter.identifiers.append(name)
                self.inter.variables[name] = arg
        
        self.inter.resumeId()
        result =  self.inter.run(self.lines, self.initialpos, 1)
        errorStack.pop()

class clSinter(interpreter):
    def executeLine(self, line, lineNo, lines, innitialPos, selfPos):
        if line == "":
            return 0
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
        #if identifier == "OUTPUT":
        #    self.exeOutput(lineNo, line)
        #    return 0
        if identifier == "DECLARE":
            self.exeDeclare(lineNo, line)
            return 0
        elif identifier == "CONSTANT":
            self.exeConstant(lineNo, line)
            return 0
        
        # youre not gonna need those in a class right?

        #elif identifier == "INPUT":
        #    self.exeInput(lineNo, line)
        #    return 0
        #elif identifier == "IF":
        #    return self.exeIf(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "CASE":
        #    return self.exeCase(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "FOR":
        #    return self.exeFor(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "REPEAT":
        #    return self.exeRepeat(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "WHILE":
        #    return self.exeWhile(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "FUNCTION":
        #    return self.exeFunction(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "PROCEDURE":
        #    return self.exeProcedure(lineNo, line, lines, innitialPos, selfPos)
        #elif identifier == "RETURN":  # return the value in skip as a list[skip, returnValue]
        #    return self.exeReturn(lineNo, line)
        #elif identifier == "CALL":
        #    self.exeCall(lineNo, line)
        #    return 0
        #elif identifier == "OPENFILE":
        #    self.exeOpenfile(lineNo, line)
        #    return 0
        #elif identifier == "READFILE":
        #    self.exeReadfile(lineNo, line)
        #    return 0
        #elif identifier == "WRITEFILE":
        #    self.exeWritefile(lineNo, line)
        #    return 0
        #elif identifier == "CLOSEFILE":
        #    self.exeClosefile(lineNo, line)
        #    return 0
        elif identifier == "TYPE":
            return self.exeType(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "CLASS":
            return self.exeClass(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "PUBLIC":
            return self.exePublic(lineNo, line, lines, innitialPos, selfPos)
        elif identifier == "PRIVATE":
            return self.exePrivate(lineNo, line, lines, innitialPos, selfPos)

        elif identifier in self.identifiers:
            self.exeAssign(lineNo, line)
            return 0
        else:
            self.err.invaSyn(lineNo, line, -1)
    
    def exePublic(self, lineNo, line, lines, innitialPos, selfPos):
        pos = 5
        token = ""
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if self.isValidChar(char):
                pos -=1
                break
            elif char ==  " ":
                pass
            else:
                self.err.invaSyn(lineNo, line, line.find(char)+6, None, "Invalid identifier")

        while pos < len(line)-1:
            pos+=1
            char = line[pos]
            if not token:
                if char.isalpha():
                    token += char
                else:
                    self.err.invaSyn(lineNo, line, line.find(char)+6, None, "Invalid identifier")
            else:
                if self.isValidChar(char):
                    token += char
                else:
                    break

        if token == "FUNCTION":
            return self.exeFunction(lineNo, line, lines, innitialPos, selfPos, pos)
        elif token == "PROCEDURE":
            return self.exeProcedure(lineNo, line, lines, innitialPos, selfPos, pos)
        elif "=" in self.removeLiteral(line, lineNo, line):
            return self.exeConstant(lineNo, line, 6)
        else:
            return self.exeDeclare(lineNo, line, 6)
    
    def exePrivate(self, lineNo, line, lines, innitialPos, selfPos):
        pos = 6
        token = ""
        while pos < len(line)-1:
            pos += 1
            char = line[pos]
            if self.isValidChar(char):
                pos -=1
                break
            elif char ==  " ":
                pass
            else:
                self.err.invaSyn(lineNo, line, line.find(char)+6, None, "Invalid identifier")

        while pos < len(line)-1:
            pos+=1
            char = line[pos]
            if not token:
                if char.isalpha():
                    token += char
                else:
                    self.err.invaSyn(lineNo, line, line.find(char)+6, None, "Invalid identifier")
            else:
                if self.isValidChar(char):
                    token += char
                else:
                    break

        if token == "FUNCTION":
            result = self.exeFunction(lineNo, line, lines, innitialPos, selfPos, pos)
        elif token == "PROCEDURE":
            result = self.exeProcedure(lineNo, line, lines, innitialPos, selfPos, pos)
        elif "=" in self.removeLiteral(line, lineNo, line):
            result = self.exeConstant(lineNo, line, 7)
        else:
            result = self.exeDeclare(lineNo, line, 7)
        self.privateIds.append(self.identifiers.pop())    
        return result

class cls:
    def __init__(self, identifier, initialpos, lines, parent, paras):
        self.identifier = identifier
        self.cls = identifier
        self.lines = lines
        self.initialpos = initialpos
        self.inter = clSinter()
        self.inter.privateIds = self.inter.identifiers
        self.inter.identifiers.clear()
        self.parent = copy.deepcopy(parent)
        self.parameters = paras
        
        self.inter.classes["SUPER"] = copy.deepcopy(parent)
        for name, type in zip (self.parameters.keys(), self.parameters.values()):
            self.inter.initId(name, -1, None)
            self.inter.identifiers.append(name)
            self.inter.variables[name] = variable(name, type)
        self.inter.run(lines, initialpos, 1)
        
        self.pubIds = self.inter.identifiers
        self.prvIds = self.inter.privateIds
        self.variables = self.inter.variables
        self.functions = self.inter.functions
        self.procedures = self.inter.procedures
        self.arrays = self.inter.arrays
        self.constants = self.inter.constants
    
    def generateObj(self, identifier, args):
        result = copy.deepcopy(self)
        result.cls = self.identifier
        result.identifier = identifier
        for name, type, arg in zip (self.parameters.keys(), self.parameters.values(), args):
            result.inter.initId(name)
            result.inter.identifiers.append(name)
            result.inter.variables[name] = variable(name, type, arg)
        return result

    def returnType(self):
        return self.cls

    def attrValue(self, identifier, args, indexes, lineNo, line):
        self.inter.err= funcError(lineNo, line, self.identifier)
        if identifier in self.variables.keys():
            result = self.variables[identifier].returnValue()
        elif identifier in self.functions.keys():
            result = self.functions[identifier].returnValue(args, lineNo, line)
        elif identifier in self.constants.keys():
            result = self.constants[identifier].returnValue()
        elif identifier in self.arrays.keys():
            result = self.arrays[identifier].returnValue(indexes, lineNo, line)
        elif identifier in self.procedures.keys():
            self.procedures[identifier].returnValue(args, lineNo, line, False)
            result = None
        errorStack.pop()
        return result
    
    def attrType(self, identifier):
        if identifier in self.variables.keys():
            return self.variables[identifier].returnType()
        elif identifier in self.functions.keys():
            return self.functions[identifier].returnType()
        elif identifier in self.constants.keys():
            return self.constants[identifier].returnType()
        elif identifier in self.arrays.keys():
            return self.arrays[identifier].returnType()

    def injectValue(self, identifier, indexes, value, lineNo, line):
        self.inter.err= funcError(lineNo, line, self.identifier)
        if identifier in self.variables.keys():
            self.variables[identifier].value = value
        elif identifier in self.arrays.keys():
            self.arrays[identifier].injectValue(indexes, value, lineNo, line)
        errorStack.pop()

class pointer(variable):
    def __init__(self, identifier, type, value=None):
        super().__init__(identifier, type, value)

    def __repr__(self):
        return self.identifier
    
    def returnType(self):
        return self.identifier

class enumerated:
    def __init__(self, identifier, values =[]):
        self.identifier = identifier
        self.values= values

class record(function):
    def __init__(self, identifier, type, initialpos, lines, parameters, lineNo, line):
        super().__init__(identifier, type, initialpos, lines, parameters)
        self.inter = funcInterpreter(lineNo, line, self.identifier)
        self.inter.err = None
        self.inter.run(lines, initialpos, 1)
        

    def injectValue(self, identifier, value):
        self.inter.variables[identifier] = value