from math import sqrt

from liberty.parser import parse_liberty
from lef_parser import LefParser
from def_parser import DefParser
from path_parser import PathParser
import scipy.interpolate
import re


class Util:
    @staticmethod
    def find_output_pin_name(component_pins):
        for pinName, pin in component_pins.items():
            if pin.info['DIRECTION'] == 'OUTPUT':
                return pinName
        return -1

    @staticmethod
    def point_is_in_net(point, net):
        for entry in net.comp_pin:
            if point.get_component() == entry[0] and point.get_pin() == entry[1]:
                return True
        return False

    @staticmethod
    def in_rectangle(lower_left_corner, upper_right_corner, point):
        return (lower_left_corner[0] <= point[0] <= upper_right_corner[0]) and (
                lower_left_corner[1] <= point[1] <= upper_right_corner[1])

    @staticmethod
    def calc_length_segment(route):
        length = 0
        for i in range(int(len(route.points) / 2)):
            length += sqrt((route.points[i][0] - route.points[i + 1][0]) ** 2 + (
                    route.points[i][1] - route.points[i + 1][1]) ** 2)
        return length

    @staticmethod
    def flip_unate(unate):
        return 'rise' if unate == 'fall' else 'fall'

    @staticmethod
    def determine_unate(timing_sense, unate):
        if timing_sense == "negative_unate":
            unate = Util.flip_unate(unate)
        elif timing_sense == "non_unate":
            print("WARNING: NON_UNATE CELL")
        return unate

    @staticmethod
    def interpolate(x, y, z, inter_x, inter_y):
        y_interp = scipy.interpolate.interp2d(x, y, z, kind="cubic")
        return y_interp(inter_x, inter_y)

    # TODO:: do not interpolate if exists
    @staticmethod
    def is_interpolate(index_array, index_val):
        for index in range(len(index_array)):
            if index_array[index] == index_val:
                return index
            if index_array[index] > index_val:
                if index != 0 and index != (len(index_array) - 1):
                    return index_array[index - 1], index_array[index]
        return -1

    @staticmethod
    def convert_to_float_arrays(index_1, index_2, values):
        index_1 = [float(x) for x in str(index_1[0])[1:-1].split(", ")]
        index_2 = [float(x) for x in str(index_2[0])[1:-1].split(", ")]
        values = [[float(y) for y in str(x)[1:-1].split(", ")] for x in values]
        return index_1, index_2, values


class Segment:
    def __init__(self):
        self.routes = []
        self.type = None

    def add_route(self, route):
        self.routes.append(route)

    def check_continuity(self, route):
        if len(self.routes) > 0:
            prev_route = self.get_last_route()
            if route.points[0] == prev_route.get_last_pt():
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def get_main_path(segments):
        for segment in segments:
            if segment.get_type() == "MAIN":
                return segment
        return -1

    def get_routes(self):
        return self.routes

    def get_last_route(self):
        return self.routes[-1]

    def get_first_route(self):
        return self.routes[0]

    def get_terminal_points(self):
        return [self.get_first_route().points[0], self.get_last_route().get_last_pt()]

    def get_type(self):
        return self.type

    def set_type(self, type_of_seg):
        self.type = type_of_seg

    def __str__(self):
        s = ""
        for route in self.routes:
            s += route.__str__() + "\n"
        return s


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
        self.SCALE = 0
        self.CELL_HEIGHT = 0

    def parse_files(self):
        self.pathFile.parse_user_file()
        self.lefFile.parse()
        self.defFile.parse()
        self.SCALE = float(self.defFile.scale)
        self.CELL_HEIGHT = self.scale_dimension(self.lefFile.cell_height)

    def run(self):
        self.parse_files()
        self.check_path_continuity()
        self.get_path_delay('fall')
        self.get_path_delay('rise')

    def scale_dimension(self, dimension):
        return int(self.SCALE * dimension)

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

    def check_path_continuity(self):
        path = self.pathFile.get_path()
        curr_node = path.nodeat(0)
        while curr_node is not None:
            # Get current point in the path
            point_one = curr_node.value
            curr_comp_macro = self.lefFile.macro_dict.get(point_one.get_component().split('_')[0])
            output_pin = Util.find_output_pin_name(curr_comp_macro.pin_dict)
            net = self.find_net_of_comp_pin(point_one.get_component(), output_pin)
            point_two = curr_node.next.value if curr_node.next is not None else None
            if point_two is not None:
                if not Util.point_is_in_net(point_two, net):
                    raise Exception("Path is discontinuous.")
            curr_node = curr_node.next

    def get_path_delay(self, unate):
        path = self.pathFile.get_path()
        curr_node = path.nodeat(0)
        total_delay = 0
        input_transition_time = 0
        while curr_node is not None:
            # Get current point in the path
            point_one = curr_node.value
            # Find the starting component/pin macro in the lef file
            curr_comp_macro = self.lefFile.macro_dict.get(point_one.get_component().split('_')[0])
            # Find the output pin name of the current from the macro
            output_pin = Util.find_output_pin_name(curr_comp_macro.pin_dict)
            # Get the center location of current component
            curr_comp_location = self.find_component_location(point_one.get_component())
            # Get the width of the current component
            curr_comp_width = self.scale_dimension(curr_comp_macro.info["SIZE"][0])
            # Determine the net of the current component's output pin
            net = self.find_net_of_comp_pin(point_one.get_component(), output_pin)
            # Get the next point in the path if not end of path else make none
            point_two = curr_node.next.value if curr_node.next is not None else None
            # Split logic based on end of path or not
            if point_two is not None and point_two.get_component() != point_one.get_component():
                # Get the macro of the next component from the lef file
                next_comp_macro = self.lefFile.macro_dict.get(point_two.get_component().split('_')[0])
                # Get the center location of the next component
                next_comp_location = self.find_component_location(point_two.get_component())
                # Get the width of the next component
                next_comp_width = self.scale_dimension(next_comp_macro.info["SIZE"][0])
                cell_delay, input_transition_time, unate = self.calc_cells_delay(unate, input_transition_time,
                                                                                 net.comp_pin,
                                                                                 point_one.get_component(),
                                                                                 point_one.get_pin(),
                                                                                 output_pin)
                r_drive = self.calc_r_drive(cell_delay, unate, point_one.get_component().split("_")[0],
                                            point_one.get_pin())
                interconnect_delay = self.cal_interconnect_delay(net.routed, curr_comp_location, curr_comp_width,
                                                                 next_comp_location,
                                                                 next_comp_width, r_drive)
                total_delay += cell_delay + interconnect_delay
            elif point_two is not None and point_two.get_component() == point_one.get_component():
                cell_delay, input_transition_time, unate = self.calc_cells_delay(unate, input_transition_time,
                                                                                 net.comp_pin,
                                                                                 point_one.get_component(),
                                                                                 point_one.get_pin(),
                                                                                 output_pin)
                total_delay += cell_delay

            curr_node = curr_node.next
        print(unate, total_delay, " secs")

    def calc_r_drive(self, cell_delay, unate, cell_name, input_pin):
        cap = self.get_pin_cap(cell_name, input_pin, unate)
        return cell_delay / cap

    def calc_cells_delay(self, unate, input_transition_time, cells, path_cell, input_pin, output_pin):
        """
        Calculates the delay of all the cells in the net
        :param unate: unate of input signal
        :param input_transition_time: input transition time of input signal
        :param cells: list of cells in the net with their pins
        :param path_cell: path cell as it is in DEF file
        :param input_pin: input pin name
        :param output_pin: output pin name
        :return: delay, output transition time, output unate
        """
        total_net_cap = 0
        for comp in cells:
            if comp[0] != path_cell:
                total_net_cap += self.get_pin_cap(comp[0].split('_')[0], comp[1])
        return self.get_arc_cap_trans(path_cell.split('_')[0], input_pin, output_pin, unate, total_net_cap,
                                      input_transition_time)

    def get_layer(self, layer_name):
        """
        Retrieves the layer object from LEF file
        :param layer_name: the name of the layer as it is in the LEF file
        :return: the layer object from the LEF file
        """
        return self.lefFile.layer_dict.get(layer_name)

    def cal_interconnect_delay(self, routes, curr_comp_location, curr_comp_width, next_comp_location, next_comp_width,
                               r_drive):
        # Continuity Check
        continuous_segments = [Segment()]
        seg_num = 0
        for route in routes:
            if continuous_segments[seg_num].check_continuity(route):
                continuous_segments[seg_num].add_route(route)
            else:
                continuous_segments.append(Segment())
                seg_num += 1
                continuous_segments[seg_num].add_route(route)
        # Main Path Check
        ll_rect_curr_comp = curr_comp_location
        ur_rect_curr_comp = (curr_comp_location[0] + curr_comp_width, curr_comp_location[1] + self.CELL_HEIGHT)
        ll_rect_next_comp = next_comp_location
        ur_rect_next_comp = (next_comp_location[0] + next_comp_width, next_comp_location[1] + self.CELL_HEIGHT)
        for segment in continuous_segments:
            terminal_points = segment.get_terminal_points()
            connects_comp = Util.in_rectangle(ll_rect_curr_comp, ur_rect_curr_comp,
                                              terminal_points[0]) and Util.in_rectangle(ll_rect_next_comp,
                                                                                        ur_rect_next_comp,
                                                                                        terminal_points[1])
            connects_comp_reverse = Util.in_rectangle(ll_rect_curr_comp, ur_rect_curr_comp,
                                                      terminal_points[1]) and Util.in_rectangle(
                ll_rect_next_comp, ur_rect_next_comp, terminal_points[0])
            if connects_comp or connects_comp_reverse:
                segment.set_type("MAIN")
        return self.cal_wire_delay(Segment.get_main_path(continuous_segments).get_routes(), r_drive)

    def cal_wire_delay(self, routes, r_drive):
        """
        Calculates the total delay from metal layer wires using Elmore's model
        :param routes: the routes to traverse
        :return: The delay of traversing these route in seconds
        """
        delay = 0
        for route in routes:
            if len(route.points) > 1:
                layer = self.get_layer(route.layer)
                length = Util.calc_length_segment(route) * 10 ** -9
                width = length * self.scale_dimension(layer.width) * 10 ** -9
                capacitance = layer.capacitance[1] * (length * width)
                resistance = layer.resistance[1] * (length / width)
                delay += r_drive * capacitance
                r_drive += resistance
        return delay

    def get_arc_cap_trans(self, cell_name, input_pin_name, output_pin_name, unate, total_net_capacitance,
                          input_transition):
        """
        Calculates the cell delay, output transition, and the output unate of a cell using NLDM from SCL
        :param cell_name: name of the cell as it is in the standard cell library
        :param input_pin_name: name of the input pin
        :param output_pin_name: name of the output pin
        :param unate: the current unate of the signal
        :param total_net_capacitance: the total capacitance in the net of the output pin
        :param input_transition: the output transition time of the previous cell
        :return: the delay in seconds, the output transition time of the current cell, the unate at output
        """
        timings = self.library.get_group("cell", cell_name).get_group("pin", output_pin_name).get_groups("timing")
        for timing in timings:
            if timing.attributes["related_pin"] == input_pin_name:
                unate = Util.determine_unate(timing.attributes["timing_sense"], unate)
                cell_unate = timing.get_group("cell_" + unate)
                unate_transition = timing.get_group(unate + "_transition")
                cu_index1, cu_index2, cu_values = Util.convert_to_float_arrays(cell_unate.attributes["index_1"],
                                                                               cell_unate.attributes["index_2"],
                                                                               cell_unate.attributes["values"])
                ut_index1, ut_index2, ut_values = Util.convert_to_float_arrays(unate_transition.attributes["index_1"],
                                                                               unate_transition.attributes["index_2"],
                                                                               unate_transition.attributes["values"])
                delay = Util.interpolate(cu_index1, cu_index2, cu_values, total_net_capacitance, input_transition)
                output_transition = Util.interpolate(ut_index1, ut_index2, ut_values, total_net_capacitance,
                                                     input_transition)
                return delay, output_transition, unate

    def get_pin_cap(self, cell_name, pin_name, unate=None):
        """
        Retrieves the capacitance of a pin from the SCL
        :param cell_name: the name of the cell as it is in the SCL
        :param pin_name: the name of the pin
        :param unate: if None use worst, else use unate
        :return:
        """
        pin = self.library.get_group("cell", cell_name).get_group("pin", pin_name)
        return pin.attributes["capacitance"] if unate is None else pin.attributes[unate + "_capacitance"]


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

liberty_path = "input-files/osu035.lib"
lef_path = "input-files/osu035_stdcells.lef"
def_path = "input-files/timer.def"
input_path = "tests/1.txt"

main = Main(input_path, liberty_path, lef_path, def_path)
main.run()
