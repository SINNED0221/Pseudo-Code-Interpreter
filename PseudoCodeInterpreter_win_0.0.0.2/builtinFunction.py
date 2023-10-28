import pci
import random
from datetime import datetime, date

class LEFT:
    def __init__(self):
        self.identifier = "LEFT"
        self.type = "STIRNG"
        self.parameters = {"ThisString": "STRING", "x": "INTEGER"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        x = args[1]
        if x > len(string)-2:
            self.inter.err.message("Index error: <"+str(x)+"> exceeds the length of the string")
        return '"'+string[1:x+1]+'"'

class RIGHT:
    def __init__(self):
        self.identifier = "RIGHT"
        self.type = "STIRNG"
        self.parameters = {"ThisString": "STRING", "x": "INTEGER"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        x = args[1]
        if x > len(string)-2:
            self.inter.err.message("Index error: <"+str(x)+"> exceeds the length of the string")
        return [0, '"'+string[len(string)-x-1:-1]+'"']

class MID:
    def __init__(self):
        self.identifier = "MID"
        self.type = "STIRNG"
        self.parameters = {"ThisString": "STRING", "x": "INTEGER", "y": "INTEGER"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        x = args[1]
        y = args[2]
        if x+y-1 > len(string)-2:
            self.inter.err.message("Index error: <"+str(x)+"> and <"+str(y)+"> exceeds the length of the string")
        return '"'+string[x:x+y-1]+'"'
    
class LENGTH:
    def __init__(self):
        self.identifier = "LENGTH"
        self.type = "INTEGER"
        self.parameters = {"ThisString": "STRING"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        return len(string)-2

class LCASE:
    def __init__(self):
        self.identifier = "LCASE"
        self.type = "CHAR"
        self.parameters = {"ThisChar": "CHAR"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        char = args[0]
        return char.lower()

class UCASE:
    def __init__(self):
        self.identifier = "UCASE"
        self.type = "CHAR"
        self.parameters = {"ThisChar": "CHAR"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        char = args[0]
        return char.upper()

class TO_UPPER:
    def __init__(self):
        self.identifier = "TO_UPPER"
        self.type = "STRING"
        self.parameters = {"ThisString": "STRING"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        return string.upper()

class TO_LOWER:
    def __init__(self):
        self.identifier = "TO_LOWER"
        self.type = "STRING"
        self.parameters = {"ThisString": "STRING"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        return string.lower()

class STR_TO_NUM:
    def __init__(self):
        self.identifier = "STR_TO_NUM"
        self.type = "REAL"
        self.parameters = {"ThisString": "STRING"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        try:
            string = int(string)
        except:
            string = float(string)
        return string

class NUM_TO_STR:
    def __init__(self):
        self.identifier = "NUM_TO_STRING"
        self.type = "STRING"
        self.parameters = {"x": "REAL"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        x = args[0]
        return '"'+str(x)+'"'
    
class IS_NUM:
    def __init__(self):
        self.identifier = "IS_NUM"
        self.type = "BOOLEAN"
        self.parameters = {"ThisString": "STRING"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        string = args[0]
        result = self.inter.boolConvert(string[1:-1] in self.inter.digits+"." 
                                        or (string[1]=="-" and string[2:-1] in self.inter.digits + "."))
        return result

class ASC:
    def __init__(self):
        self.identifier = "ASC"
        self.type = "INTEGER"
        self.parameters = {"ThisChar": "CHAR"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        char = args[0]
        return ord(char[1])
    
class CHR:
    def __init__(self):
        self.identifier = "CHR"
        self.type = "CHAR"
        self.parameters = {"x": "INTEGER"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        x = args[0]
        return "'"+chr(x)+'"'

class INT:
    def __init__(self):
        self.identifier = "INT"
        self.type = "INTEGER"
        self.parameters = {"x": "REAL"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        x = args[0]
        return int(x)

class RAND:
    def __init__(self):
        self.identifier = "RAND"
        self.type = "REAL"
        self.parameters = {"x": "INTEGER"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        x = args[0]
        return round(random.uniform(0, x), 2)

class DAY:
    def __init__(self):
        self.identifier = "DAY"
        self.type = "INTEGER"
        self.parameters = {"ThisDate": "DATE"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        ThisDate = args[0]
        dt = datetime.strptime(ThisDate, "%d/%m/%Y")
        result = int(dt.strftime("%d"))
        return result

class MONTH:
    def __init__(self):
        self.identifier = "MONTH"
        self.type = "INTEGER"
        self.parameters = {"ThisDate": "DATE"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        ThisDate = args[0]
        dt = datetime.strptime(ThisDate, "%d/%m/%Y")
        result = int(dt.strftime("%m"))
        return result

class YEAR:
    def __init__(self):
        self.identifier = "YEAR"
        self.type = "INTEGER"
        self.parameters = {"ThisDate": "DATE"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        ThisDate = args[0]
        dt = datetime.strptime(ThisDate, "%d/%m/%Y")
        result = int(dt.strftime("%Y"))
        return result

class DAYINDEX:
    def __init__(self):
        self.identifier = "DAYINDEX"
        self.type = "INTEGER"
        self.parameters = {"ThisDate": "DATE"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        ThisDate = args[0]
        dt = datetime.strptime(ThisDate, "%d/%m/%Y")
        result = int(dt.strftime("%w"))+1
        return result

class SETDATE:
    def __init__(self):
        self.identifier = "SETDATE"
        self.type = "DATE"
        self.parameters = {"Day":"INTEGER", "Month":"INTEGER", "YEAR":"INTEGER"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
        
        day = args[0]
        month = args[1]
        year = args[2]
        try:
            dt = date(year, month, day)
        except ValueError:
            self.inter.err.message("Value error: "+str(day)+"/"+str(month)+"/"+str(year)+" is not a valid dt")
        result = dt.strftime("%d/%m/%Y")
        return result

class TODAY:
    def __init__(self):
        self.identifier = "TODAY"
        self.type = "DATE"
        self.parameters = {}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        self.inter = pci.funcInterpreter(lineNo, line, self.identifier)
    
        dt = datetime.today()
        result = dt.strftime("%d/%m/%Y")
        return result

class EOF:
    def __init__(self):
        self.identifier = "EOF"
        self.type = "BOOLEAN"
        self.parameters = {"FileName": "STRING"}
        self.lines = []
        self.initialpos = 0 
    
    def returnType(self):
        return self.type
    
    def returnValue(self, args, lineNo, line):
        pass

builtIns = {"LEFT":LEFT(),
            "RIGHT":RIGHT(),
            "MID": MID(),
            "LENGTH": LENGTH(),
            "LCASE": LCASE(),
            "UCASE": UCASE(),
            "TO_UPPER": TO_UPPER(),
            "TO_LOWER": TO_LOWER(),
            "NUM_TO_STR": NUM_TO_STR(),
            "STR_TO_NUM": STR_TO_NUM(),
            "IS_NUM": IS_NUM(),
            "ASC": ASC(),
            "CHR": CHR(),
            "INT": INT(),
            "RAND": RAND(),
            "DAY": DAY(),
            "MONTH": MONTH(),
            "YEAR": YEAR(),
            "DAYINDEX": DAYINDEX(),
            "SETDATE": SETDATE(),
            "TODAY": TODAY(),
            "EOF":EOF()
            }