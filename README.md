# Pseudo-Code-Interpreter
This is an interpreter that aims to provide **full-syllabus** support for the CAIE computer science pseudo code.

This interpreter can directly run files written in pseudo code with the extension `.pseu`, or it can run single lines in interactive mode. Error messages will be raised if error occurred. A debugger is currently under development.

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
Run `PseudoCodeInterpreter.exe` with the path of the file as parameter.

    PseudoCodeInterpreter.exe path\file.pseu

## Settings
There are several setting option in `settings.py` that you can toggle.
### `maxRecur`
Determine the max recursion depth of the interpreter, notice that it cannot exceed python's recursive depth of 1000.

### `arrowReplace`
`arrowReplace = True` : `<-` will be automatically replaced by `←`, which is  the default assign operator. Notice that when it is enabled, things like `IF x < -1 THEN` must have a white space between `<` and `-`.

## Syntax
Ideally this interpreter can be used directly with the cambridge official pseudo code guide as reference. But due to some uncertain nature of the pseudo code syntax, some bit might require extra explanation.

For 99% of the time, you can write code as what the pseudo code guide says and everything will work.

### Indentation   
By many standards of programming languages, an indent should be four consecutive white spaces, and that is what most IDEs gives when you press tab by default. However, as specified in the pseudo code guide, an indentation should be three white spaces.

So, just as what most interpreters did, here you can use any number of spaces as long as they are consist in one specific code block.

Notice that tab character is not supported.

### Comment
Everything behind `//` will be ignored.

### Lining
Currently multi-line instruction is not supported, so one line of command cannot be separated.

    // will not execute
    CALL abc(x, y,
                  z)

### Datatype
#### `INTEGER`
A whole number.
#### `REAL`
A number capable of containing a fractional part.
#### `CHAR`
A single character.

Notice that a literal of `CHAR` must be wrapped with a single quotation mark.

    x ← 'x'

If more than one character occur in the single quotation marks, a `Syntax Error` will be raised.
#### `STRING`
A sequence of 0 or more characters.

A literal of string uses double quotation marks.
#### `BOOLEAN`
The logical values `TRUE` and `FALSE`.
#### `DATE`
A valid date in the form of dd/mm/yyyy.

A literal of date will also be in that form, notice that as a date literal will likely conflict with an expression with `/` operator, a `DATE` literal is only checked when assigning to a variable of `DATE` type. `INPUT` will not take `DATE` literal, if you are trying to get a `DATE` with `INPUT`, see built-in functions.
### Variable
A variable must be declared with type before any usage.

    DECLARE x: INTEGER

Notice that any identifier in a pseudo code must start with a letter, and can be followed by letters, numbers and `_`.
### Constant
Constants, once declared, will be immutable.

    CONSTANT x = 1

The data type will be automatically set by the literal.
### Assignment
Assignment is done using the assignment operator `←`.

    Counter ← Counter + 1

### Array
Array can be declared in such fashion:

    DECLARE StudentNames : ARRAY[1:30] OF STRING
    DECLARE NoughtsAndCrosses : ARRAY[1:3,1:3] OF CHAR

Notice that although not specified in the official pseudo code guide, you can declare an array of any dimension here.

They can be used like this:

    StudentNames[1] ← "Ali"
    NoughtsAndCrosses[2,3] ← ꞌXꞌ

### File-handling
Works just as the pseudo code guide instructed.

However, file-handling for random file is currently unsupported.

### Built-in Functions
All functions in the insert page of the official computer science papers are supported with no variance to the description in the insert page.

### Object-oriented programming
Currently a bit broken, any object method cannot access global variables.

Also, for object procedures, although the guide showed an example of calling an object procedure simply by its identifier, for the consistency with normal procedures, object procedures also need to be called using `CALL` instruction.

Other than what is mentioned above, everything works as the guide says.    