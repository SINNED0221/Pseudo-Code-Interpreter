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
            message += str(self.evalExpr(identifier, line, lineNo))
        elif "&" in identifierWOLiteral:  # apart from string literal, there is a &
            message += self.strComb(identifier, lineNo, line)
        elif all(n in self.digits+"." for n in identifier):  # it is a number
            message += str(identifier)
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