from liberty.parser import parse_liberty
from lef_parser import LefParser
from def_parser import DefParser
import re
liberty_file = "Testing Files/osu035.lib"
lef_file = "libraries/Nangate/NangateOpenCellLibrary.lef"
def_file = "Testing Files/timer.def"
input_file = "Testing Files/input.txt"
library = parse_liberty(open(liberty_file).read())
lefFile = LefParser(lef_file)
defFile = DefParser(def_file)
lefFile.parse()
defFile.parse()
inputFile = open(input_file).read()
print(inputFile)
#
# print(str(library))
# #print(str(library))
# print(library.get_group("lu_table_template", "delay_template_5x6"))
# for layerName, layer in lefFile.layer_dict.items():
#     isMetal = re.match(r"^metal[0-9]$", layerName)
#     isVia = re.match(r"^via[0-9]$", layerName)
#     if isMetal:
#         print(layerName)
#         print(layer.resistance)
#         print(layer.capacitance)
#         print(layer.width)
#         print(layer.height)
#
# for net in defFile.nets:
#     print(net)


# lefFile.via_dict
# lefFile.macro_dict
# lefFile.stack
# lefFile.statements
#
# print(lefFile.macro_dict.values())


for pin in defFile.pins:
    print(pin)

def calculateDelay():
    calculateDelayCells()
    calculateDelayInterconnect()


def calculateDelayCells():
    print("meow")


def calculateDelayInterconnect():
    # the bluetooth device has been connected successfully
    print("meow")
