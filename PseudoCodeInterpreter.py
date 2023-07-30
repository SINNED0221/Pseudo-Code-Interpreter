import os
import sys

# Set the module paths to the current directory
# or the directory containing the executable.
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    basedir = os.path.dirname(sys.executable)
else:
    # Running in development (not compiled)
    basedir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, basedir)
import pci
inter = pci.interpreter()

if len(sys.argv) < 2:  # Interactive mode
    while True:
        line = input("pseudo>>>")
        inter.initRun(line)

else:  # Running a file
    filePath = sys.argv[1]
    if not filePath.endswith(".pseu"):
        pci.printRed("Unsupported file extension, expect .pseu files")
        input()
        quit()
    with open(filePath, 'r', encoding='utf-8') as file:
        code = file.read()

    if code:
        inter.initRun(code)
    input("\nProgram executed successfully, press enter to exit")