import PseudoCodeInterpreter as pci

inter = pci.interpreter()
while True:
    line = input("pseudo>")
    inter.run(line)