from llist import sllist
from llist import sllistnode


class PathParser:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.path = []

    @staticmethod
    def peek_line(f):
        pos = f.tell()
        line = f.readline()
        f.seek(pos)
        return line

    def parse_user_file(self):
        path_file = open(self.path_to_file, "r+")
        for line in path_file:
            parts = line.split("/")
            component = parts[0]
            pin = parts[1][0]
            self.path.append(PathPoint(component, pin))
        self.path = sllist(self.path)

    def get_path(self):
        return self.path


class PathPoint:
    def __init__(self, component, pin):
        self.component = component
        self.pin = pin

    def __str__(self):
        s = ""
        s += "Component: " + self.component + "\n"
        s += "Pin: " + self.pin + "\n"
        return s

    def get_component(self):
        return self.component

    def get_pin(self):
        return self.pin
