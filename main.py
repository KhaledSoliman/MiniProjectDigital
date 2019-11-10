from liberty.parser import parse_liberty
from lef_parser import LefParser
from def_parser import DefParser
from path_parser import PathParser
import re


class Main:
    def __init__(self, input_path, liberty_path, lef_path, def_path):
        self.input_path = input_path
        self.liberty_path = liberty_path
        self.lef_path = lef_path
        self.def_path = def_path
        self.pathFile = PathParser(self.input_path)
        self.lefFile = LefParser(self.lef_path)
        self.defFile = DefParser(self.def_path)
        self.liberty_file = open(self.liberty_path).read()
        self.library = parse_liberty(self.liberty_file)

    def parse_files(self):
        self.pathFile.parse_user_file()
        self.lefFile.parse()
        self.defFile.parse()

    def run(self):
        self.parse_files()
        self.get_path()

    @staticmethod
    def find_output_pin_name(component_pins):
        for pinName, pin in component_pins.items():
            if pin.info['DIRECTION'] == 'OUTPUT':
                return pinName
        return -1

    def find_net_of_comp_pin(self, component, pin):
        for net in self.defFile.nets:
            for entry in net.comp_pin:
                if component == entry[0] and pin == entry[1]:
                    return net
        return -1

    def find_pin_location(self, pin_name):
        for pin in self.defFile.pins:
            if pin_name == pin.name:
                return pin.placed
        return -1

    def find_component_location(self, component_name):
        for component in self.defFile.components:
            if component_name == component.name:
                return component.placed
        return -1

    def get_path(self):
        for point in self.pathFile.get_path():
            output_pin = self.find_output_pin_name(
                self.lefFile.macro_dict.get(point.get_component().split('_')[0]).pin_dict)
            net = self.find_net_of_comp_pin(point.get_component(), output_pin)
            component_location_out = self.find_component_location(point.get_component())
            print(component_location_out)
            for route in net.routed:
                print(route)
            print(output_pin)

    def calculateDelay(self):
        self.calculateDelayCells()
        self.calculateDelayInterconnect()

    def calculateDelayCells(self):
        print("meow")

    def cal_wire_capacitance(self):
        for layerName, layer in self.lefFile.layer_dict.items():
            is_metal = re.match(r"^metal[0-9]$", layerName)
            is_via = re.match(r"^via[0-9]$", layerName)
            if is_metal:
                print(layerName)
                print(layer.resistance)
                print(layer.capacitance)
                print(layer.width)
                print(layer.height)


# print(library.get_group("lu_table_template", "delay_template_5x6"))
# print(str(library))
# lefFile.via_dict
# lefFile.macro_dict
# lefFile.stack
# lefFile.statements
# for comp in defFile.components:
#     for pin in defFile.pins:
#         for net in defFile.nets:
#             for x in net.comp_pin:
#                 if pin.net in x or comp.name in x:
#                     print(pin.name)
#                     print(pin.placed)
#                     print(comp.name)
#                     print(comp.placed)
#                     print(net)
#


liberty_path = "Testing Files/osu035.lib"
lef_path = "Testing Files/osu035_stdcells.lef"
def_path = "Testing Files/timer.def"
input_path = "Testing Files/input.txt"

main = Main(input_path, liberty_path, lef_path, def_path)
main.run()
