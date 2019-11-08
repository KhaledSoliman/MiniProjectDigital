from liberty.parser import parse_liberty
from lef_parser import LefParser
from def_parser import DefParser
liberty_file = "Testing Files/osu035.lib"
lef_file = "Testing Files/osu035_stdcells.lef"
def_file = "Testing Files/timer.def"
library = parse_liberty(open(liberty_file).read())
lefFile = LefParser(lef_file)
defFile = DefParser(def_file)
print(str(library))