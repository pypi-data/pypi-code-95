
from dataclasses import dataclass
from collections import namedtuple
from typing import Tuple, NamedTuple


@dataclass(frozen=True)
class Joint:
    # dataclass that represents a single joint
    name: str = ""
    dof: NamedTuple = ()
    direction: Tuple = () 
    length: float = 0
    axis: NamedTuple = ()
    order: Tuple = ()

@dataclass(frozen=True)
class ASF:
    # dataclass that represents a parsed asf file
    name: str
    units: NamedTuple
    doc: str
    joints: Tuple[Joint, ...]
    hierarchy: dict

    def __iter__(self):
        return list(self.joints).__iter__()

    def __getitem__(self, jointName:str) -> Joint:
        for joint in self.joints:
            if joint.name == jointName:
                return joint
        raise ValueError(f"Joint name {jointName} does not exist.")

@dataclass(frozen=True)
class AMC:
    # dataclass that represents a parsed amc file
    count: int
    frames: Tuple[dict, ...]
    
    def __iter__(self):
        return list(self.frames).__iter__()

    def __getitem__(self, frame:int) -> Tuple:
        if frame < self.count:
            return self.frames[frame]
        raise IndexError(f"Frame index must be < {self.count}.")

# Main logic
class Reader:
    def ReadFile(self, filePath:str) -> Tuple[str, ...]:
        try:
            with open(filePath) as file:
                lines = file.read().splitlines()
            return tuple(lines)
        except Exception as e:
            raise e
    
    def _ReadLine(self, lines:Tuple[str, ...], i:int=0) -> Tuple[str,int]:
        if i >= len(lines): return None, i
        line = lines[i].split()
        i += 1
        return line, i

    def _RaiseSyntaxError(self, index:int):
        errorStr = f"Asf format incorrect at line {index}."
        raise SyntaxError(errorStr)

class ParseASF(Reader):
    def __init__(self, filePath:str) -> None:
        super().__init__()
        # check file path exists and read all lines in file
        lines = self.ReadFile(filePath)
        # parse into asf dataclass
        self.asf = self._Parse(lines)

    def _Parse(self, lines:Tuple[str, ...]) -> ASF:
        unitsT = namedtuple('units',['mass','length','angle'])
        read = lambda index: self._ReadLine(lines, index)
        line, i = read(0)
        if not line[0] == ":version": self._RaiseSyntaxError(i)
        if not line[1] == "1.10": self._RaiseSyntaxError(i)
        line, i = read(i)
        if not line[0] == ":name": self._RaiseSyntaxError(i)
        asfName = line[1]
        line, i = read(i)
        if not line[0] == ":units": self._RaiseSyntaxError(i)
        line, i = read(i)
        if not line[0] == "mass": self._RaiseSyntaxError(i)
        mass = line[1]
        line, i = read(i)
        if not line[0] == "length": self._RaiseSyntaxError(i)
        length = line[1]
        line, i = read(i)
        if not line[0] == "angle": self._RaiseSyntaxError(i)
        angle = line[1]
        units = unitsT(mass, length, angle)
        line, i = read(i)
        if not line[0] == ":documentation": self._RaiseSyntaxError(i)
        doc = ""
        while line[0] != ":root":
            line, i = read(i)
            doc += " ".join(line[:]) + " "
        line, i = read(i)
        if not line[0] == "axis": self._RaiseSyntaxError(i)
        axis = list(line[1])
        line, i = read(i)
        if not line[0] == "order": self._RaiseSyntaxError(i)
        order = []
        for j in range(1,len(line)):
            order.append(line[j])
        line, i = read(i)
        if not line[0] == "position": self._RaiseSyntaxError(i)
        position = [ float(val) for val in line[1:]]
        line, i = read(i)
        if not line[0] == "orientation": self._RaiseSyntaxError(i)
        orientation = [ float(val) for val in line[1:]]
        axisT = namedtuple("axis",order)
        axis = axisT(*position,*orientation)
        rootJoint = Joint("root", dof=tuple(axis), order=tuple(axis), axis=axis)
        line, i = read(i)
        if not line[0] == ":bonedata": self._RaiseSyntaxError(i)
        joints = [rootJoint]
        line, i = read(i)
        while line[0] != ":hierarchy":
            if not line[0] == "begin": self._RaiseSyntaxError(i)
            line, i = read(i)
            if not line[0] == "id": self._RaiseSyntaxError(i)
            line, i = read(i)
            if not line[0] == "name": self._RaiseSyntaxError(i)
            name = line[1]
            line, i = read(i)
            if not line[0] == "direction": self._RaiseSyntaxError(i)
            direction = [float(val) for val in line[1:]]
            line, i = read(i)
            if not line[0] == "length": self._RaiseSyntaxError(i)
            length = float(line[1])
            line, i = read(i)
            if not line[0] == "axis": self._RaiseSyntaxError(i)
            order = list(line[len(line)-1])
            axisT = namedtuple("axis",order)
            axis = axisT(*[float(val) for val in line[1:len(line)-1]])
            line, i = read(i)
            if not line[0] == "dof": self._RaiseSyntaxError(i)
            dofT = namedtuple("dof",line[1:])
            line, i = read(i)
            if not line[0] == "limits": self._RaiseSyntaxError(i)
            limits = [(float(line[1].strip("(")), float(line[2].strip(")")))]
            line, i = read(i)
            while line[0] != "end":
                limits.append((float(line[0].strip("(")), float(line[1].strip(")"))))
                line, i = read(i)
            dof = dofT(*limits)
            joints.append( Joint(name, dof, direction, length, axis, order))
            line, i = read(i)
        line, i = read(i)
        if not line[0] == "begin": self._RaiseSyntaxError(i)
        hierarchy = {}
        while line[0] != "end":
            line, i = read(i)
            hierarchy[line[0]] = tuple(line[1:])
        return ASF(asfName, units, doc, tuple(joints), hierarchy)
 
class ParseAMC(Reader):
    def __init__(self, filePath:str) -> AMC:
        super().__init__()
        # check file path exists and read all lines in file
        lines = self.ReadFile(filePath)
        # parse into amc dataclass
        self.amc = self._Parse(lines)
    
    def _Parse(self, lines:Tuple[str, ...]) -> AMC:
        read = lambda index: self._ReadLine(lines, index)
        line, i = read(0)
        if not line[0] == ":FULLY-SPECIFIED": self._RaiseSyntaxError(i)
        line, i = read(i)
        if not line[0] == ":DEGREES": self._RaiseSyntaxError(i)
        frames = []
        line, i = read(i)
        while i != len(lines):
            index = int(line[0])
            if not index >= 0: self._RaiseSyntaxError(i)
            line, i = read(i)
            frame = {}
            while line != None and line[0] != f"{index+1}":
                frame[line[0]] = [float(val) for val in line[1:]]
                line, i = read(i)
            frames.append(frame)
        return AMC(len(frames), tuple(frames))
        

if __name__ == "__main__":
    asf = ParseASF("./AsfAmcParser/test.asf")
    amc = ParseAMC("./AsfAmcParser/testRaw.amc")
    print(amc.amc[0]["Waist"])