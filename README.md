# Pseudo-Code-Interpreter
This is an interpreter that aims to provide **full-syllubus** support for the CAIE computer science pseudo code.

This interpreter can directly run files written in pseudo code with the extension `.pseu`, or it can run single lines in interactive mode. Error messages will be raised if error occured. A debugger is currently under development.

Also, a plug-in for vscode that can do syntax highlighting is also under development.
## Quick Start Guide
### For Windows
#### Interactive Mode
Simply execute `PseudoCodeInterpreter.exe` and type in the code.

    pseudo>>>OUTPUT "ABC"
    ABC

#### Script Mode
They are several ways you can execute a pseudo code script, notice that only files with the extension `.pseu` will be accepted.
###### Drag and Drop
Simply drag and drop the `.pseu` file to `PseudoCodeInterpreter.exe` to execute the script.
###### Open with
Right-click the file and click `Open with...` browse and select `PseudoCodeInterpreter.exe` and set it as a default, next time you can just double-click the `.pseu` file to run it.
###### CMD
    PseudoCodeInterpreter.exe path\file.pseu

