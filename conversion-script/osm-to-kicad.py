"""

Prupose: Script to convert Ciat-Lonbarde Osmond PCB footprints to KiCAD footprints.
Date:    23/01/2025
Author:  Neil Massey
License: No rights reserved.  Creative Commons CC-0.

"""

from datetime import datetime
from uuid import uuid4

def p2V(V: str):
    """
    Note: all positional values in KiCad are given in millimetres.
    For Osmond PCB values are indicated by the suffix:
    No suffix: mils, i.e. 0.001 of an inch, 0.001*25.4 of a mm
    m suffix: millimetres
    p suffix: p suffix = 1/72 of an inch = 1/72*25.4
    """

    if V[-1] == 'm':
        return float(V[:-1])
    elif V[-1] == 'p':
        return 1.0/72*25.4*float(V[:-1])
    else:
        return 0.001*25.4*float(V)

def l2l(L: str):
    """
    Convert layer names from OSM to KiCad
    """
    layers = {
        'Front'     : 'F.Cu',
        'Inner'     : 'In1.Cu',
        'Back'      : 'B.Cu',
        'Silk'      : 'F.SilkS',
        'BackSilk'  : 'B.SilkS',
        'FrontAux'  : 'F.Fab',
        'BackAux'   : 'B.Fab',
        'FrontMask' : 'F.Mask',
        'BackMask'  : 'B.Mask'
    }
    return layers[L]

def s2s(S: str):
    """
    Convert pad shapes from OSM to KiCad
    """
    shapes = {
        'Circle'    : 'circle',
        'Oval'      : 'oval',
        'Rectangle' : 'rect',
        'Hexagon'   : 'custom'
    }
    return shapes[S]

class newType():
    """Class containing definitions of new footprints for KiCad, derived from an Osmond Type"""
    def __init__(self, fh: object, line: str):
        # default value of path width for Front SilkScreen
        self.path_width = 0.25
        # initialise the output text buffer
        self.output_buffer = ""
        self.fh = fh
        # footprints to show the values for
        self.show_values = [
            'r3', 'r4', 'dip8', 'dip14', 'dip16', 'dip24', 'dip4077mod'
        ]
        # pad dictionary
        self.pads = {}
        # current pin number - these are not always well defined in the OSM source file so we will just count up
        self.pinc = 0
        self.process(fh, line)

    def _write(self, indent: int, text: str):
        self.output_buffer += f'{"":<{indent}}{text}\n'

    def _add_footprint(self, name: str):
        self.name = name
        self._write(0, f'(footprint "{name}"')

    def _add_header(self, name: str):
        #T = datetime.now()
        #V = f"{T.year}" + f"{T.month:02d}" + f"{T.day:02d}"
        V = "20240108"
        self._write(4, f'(version {int(V)})')
        self._write(4, f'(generator "osm-to-kicad")')
        self._write(4, f'(generator_version "1.0")')
        self._write(4, f'(layer "F.Cu")')
        self._write(4, f'(descr "{name} from Ciat-Lonbarde Osmond PCB library")')
        self._write(4, f'(tags "{name} from Ciat-Lonbarde Osmond PCB library")')

    def _get_text_pos_data(self, line: str):
        data = line.split()
        size = 0
        X = 0
        Y = 0
        rot = 0
        justify = None
        if len(data) > 2:
            size = data[2].strip()
        if len(data) > 3:
            X = data[3].strip()
        if len(data) > 4:
            Y = data[4].strip()
        if len(data) > 5:
            rot = data[5].strip()
        if len(data) > 6 and data[6].strip() != "}":
            justify = data[6].strip()

        return p2V(size), p2V(X), p2V(Y), rot, justify

    def _add_reference(self, line: str):
        size, X, Y, rot, justify  = self._get_text_pos_data(line)
        self._write(4, f'(property "Reference" "REF**"')
        self._write(8, f'(at {X} {Y} {rot})')
        self._write(8, f'(layer "F.Fab")')
        self._write(8, f'(hide no)')
        self._write(8, f'(uuid {uuid4()}")')
        self._write(8, f'(effects')
        self._write(12, f'(font')
        self._write(16, f'(size {size} {size})')
        self._write(16, f'(thickness 0.15)')
        self._write(12, f')')
        self._write(8, f')')
        self._write(4, f')')

    def _add_value(self, line: str):
        size, X, Y, rot, justify  = self._get_text_pos_data(line)
        # We only want to show the value for a select set of footprints
        if self.name in self.show_values:
            hide = 'no'
        else:
            hide = 'yes'
        self._write(4, f'(property "Value" "{self.name}"')
        self._write(8, f'(at {X} {Y} {rot})')
        self._write(8, f'(layer "F.SilkS")')
        self._write(8, f'(hide {hide})')
        self._write(8, f'(uuid {uuid4()}")')
        self._write(8, f'(effects')
        self._write(12, f'(font')
        self._write(16, f'(size {size} {size})')
        self._write(16, f'(thickness 0.15)')
        self._write(12, f')')
        if justify:
            self._write(12, f'(justify {justify})')
        self._write(8, f')')
        self._write(4, f')')

    def _add_path_segment(self, layer: str, X0: float, Y0: float, X1: float, Y1: float):
        self._write(4, f'(fp_line')
        self._write(8, f'(start {X0} {Y0})')
        self._write(8, f'(end {X1} {Y1})')
        self._write(8, f'(stroke')
        self._write(12, f'(width {self.path_width})')
        self._write(12, f'(type default)')
        self._write(8, ')')
        self._write(8, f'(layer "{layer}")')
        self._write(8, f'(uuid "{uuid4()}")')
        self._write(4, ')')

    def _read_path(self, fh: object):
        "Return a list containing the path definitions which may be split across lines and nested!"
        ref_count = 0
        run = True
        vals = []
        while run:
            line = fh.readline()
            line_vals = line.split()
            for v in line_vals:
                if (v == '{'):
                    ref_count += 1
                elif (v == '}'):
                    ref_count -= 1
                vals.append(v)
                if ref_count == 0:
                    run = False
        return vals

    def _add_path(self, layer: str, vals: list[str], P: int, X0: float, Y0: float):
        while vals[P] != '}':
            if vals[P] == '{':
                P = self._add_path(layer, vals, P+1, X1, Y1)
                X0 = X1
                Y0 = Y1
            elif vals[P] == 'W':
                self.path_width = p2V(vals[P+1])
                P += 2
            elif (vals[P] == 'S'):
                # is spacing used for anything?
                P += 2
            else:
                X1 = p2V(vals[P])
                Y1 = p2V(vals[P+1])
                self._add_path_segment(layer, X0, Y0, X1, Y1)
                X0 = X1
                Y0 = Y1
                P += 2
        return P+1

    def _process_path(self, fh: object, line: str):
        layer = l2l(line.split()[1])
        vals = self._read_path(fh)
        if vals[0] == '{':
            X0 = p2V(vals[1])
            Y0 = p2V(vals[2])
            P = self._add_path(layer, vals, 3, X0, Y0)

    def _set_pad(self, line: str):
        # line looks like 'Pad <letter> { <type> <size> }', so split
        pad_parts = line.split()
        # get the pad letter:
        padl = pad_parts[1]
        padt = s2s(pad_parts[3])
        size = p2V(pad_parts[4])
        self.pads[padl] = (padt, size)

    def _add_pin(self, line: str):
        # line looks like 'Pin <id> {<pad front> <pad inner> <pad back> X Y diameter <plated|unplated=P|U>}
        # <pad front>, <pad inner>, <pad back> should all be the same
        pin_parts = line.split()
        self.pinc += 1
        # get the pad from the dictionary
        pad = self.pads[pin_parts[3]]
        # write the header bit
        self._write(4, f'(pad "{self.pinc}" thru_hole {pad[0]}')
        self._write(8, f'(at {p2V(pin_parts[6])} {p2V(pin_parts[7])})')
        self._write(8, f'(size {pad[1]} {pad[1]})')
        self._write(8, f'(drill {p2V(pin_parts[8])})')
        self._write(8, '(layers "*.Cu" "*.Mask")')
        self._write(8, '(remove_unused_layers no)')
        self._write(8, f'(uuid "{uuid4()}")')
        self._write(4, f')')

    def save(self):
        fname = f'../diy-nabra.pretty/{self.name}.kicad_mod'
        fh = open(fname, "w")
        fh.write(self.output_buffer)
        fh.close()

    def process(self, fh: object, line: str):
        # Process a single Type by processing each line in the type
        name = line[4:].replace("{", " ").strip()
        self._add_footprint(name)
        self._add_header(name)

        while fh and line.strip() != "}":
            line = fh.readline()
            if line[:len("NameData")] == "NameData":
                self._add_reference(line)
            elif line[:len("ValueData")] == "ValueData":
                self._add_value(line)
            elif line[:len("Path")] == "Path":
                self._process_path(fh, line)
            elif line[:len("Pad")] == "Pad":
                self._set_pad(line)
            elif line[:len("Pin")] == "Pin":
                self._add_pin(line)
        # add the through hole attribute
        self._write(4, '(attr through_hole)')
        print("SAVE", self.name)
        # close the footprint
        self._write(0, f')')
        self.save()

def processFile(fh: object):
    "loop over the lines in the file, find the Type and process from there"
    while fh:
        line = fh.readline()
        if line == '':
            break
        if line[:4] == "Type":
            new_type = newType(fh, line)
            
if __name__ == "__main__":
    with open("cl_osmond_library.osm") as fh:
        processFile(fh)
