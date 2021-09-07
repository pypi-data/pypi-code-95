from typing import Union, List, Optional,overload
from copy import deepcopy
number = Union[int, float, None]
boolean = Union[bool, None]
string = Union[str, None]




class Object():
    def __init__(self,name):
        self.name=name

class GLModel(Object):
    def __init__(self,name):
        super().__init__(name)

class GLShape(Object):
    def __init__(self,name):
        super().__init__(name)

class GLViewer(Object):
    def __init__(self,name):
        super().__init__(name)

class Label(Object):
    def __init__(self,name):
        super().__init__(name)


function = Optional  # undefined now
Gradient = Optional
VolumeData = Optional
ClickSphereStyleSpec = Optional

Mesh=Optional

_map = {"myand": "and", "myor": "or", "mynot": "not"}


# Enum
class CAP:
    NONE = 0
    FLAT = 1
    ROUND = 2


class SurfaceType:
    VDW = 1
    MS = 2
    SAS = 3
    SES = 4
class FileFormats:
    json="json"
    cdjson="cdjson"
    cube="cube"
    gro="gro"
    cif="cif"
    mcif="mcif"
    mmtf="mmtf"
    mol2="mol2"
    pdb="pdb"
    pqr="pqr"
    prmtop="prmtop"
    sdf="sdf"
    vasp="vasp"
    xyz="xyz"


class argdict(dict):
    def __init__(self):
        super().__init__()
    def remove(self,*l):
        for s in l:
            self.pop(s)
        rms=[]
        for item in self:
            if self[item]==None:
                rms.append(item)
        for i in rms:
            self.pop(i)




class Vector3(argdict):
    def __init__(self, x: number, y: number, z: number):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")



class Dimensions(argdict):
    def __init__(self, w: number, h: number, d: number):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

class ColorSpec(str):
    def __init__(self,s="0xAF10AB"):
        super().__init__()







class ArrowSpec(argdict):
    def __init__(self,
                 start: Vector3,
                 end: Vector3,
                 radius: number=None,
                 color: ColorSpec = None,
                 hidden: boolean = None,
                 radiusRatio: number = None,
                 mid: number = None,
                 midpos: number = None,
                 ):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

# a=ArrowSpec(start=Vector3(0,0,0),end=Vector3(10,9,100))
# print(a)
class AtomSpec(argdict):
    def __init__(self,
                 resn: string=None,
                 x: number=None,
                 y: number=None,
                 z: number=None,
                 color: ColorSpec=None,
                 surfaceColor: ColorSpec=None,
                 elem: string=None,
                 hetflag: boolean=None,
                 chain: string=None,
                 resi: number=None,
                 icode: number=None,
                 rescode: number=None,
                 serial: number=None,
                 atom: string=None,
                 bonds: List[number]=None,
                 ss: string=None,
                 singBonds: boolean=None,
                 bondOrder: List[number]=None,
                 properties: function=None,
                 b: number=None,
                 pdbline: string=None,
                 clickable: boolean=None,
                 callback: function=None,
                 invert: boolean=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

@overload
class AtomSelectionSpec(argdict):
    def __init__(self,
                 resn: string = None,
                 x: number = None,
                 y: number = None,
                 z: number = None,
                 color: ColorSpec = None,
                 surfaceColor: ColorSpec = None,
                 elem: string = None,
                 hetflag: boolean = None,
                 chain: string = None,
                 resi: number = None,
                 icode: number = None,
                 rescode: number = None,
                 serial: number = None,
                 atom: string = None,
                 bonds: List[number] = None,
                 ss: string = None,
                 singBonds: boolean = None,
                 bondOrder: List[number] = None,
                 properties: function = None,
                 b: number = None,
                 pdbline: string = None,
                 clickable: boolean = None,
                 callback: function = None,
                 invert: boolean = None,
                 ### additional
                 model: GLModel=None,
                 predicate: function=None,
                 byres: boolean=None,
                 expand: number=None,
                 ):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

class WithinSelectionSpec(argdict):
    def __init__(self,
                 distance: number=None,
                 invert: boolean=None,
                 sel: AtomSelectionSpec=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

@overload
class AtomSelectionSpec2(AtomSelectionSpec):
    def __init__(self,
                 resn: string = None,
                 x: number = None,
                 y: number = None,
                 z: number = None,
                 color: ColorSpec = None,
                 surfaceColor: ColorSpec = None,
                 elem: string = None,
                 hetflag: boolean = None,
                 chain: string = None,
                 resi: number = None,
                 icode: number = None,
                 rescode: number = None,
                 serial: number = None,
                 atom: string = None,
                 bonds: List[number] = None,
                 ss: string = None,
                 singBonds: boolean = None,
                 bondOrder: List[number] = None,
                 properties: function = None,
                 b: number = None,
                 pdbline: string = None,
                 clickable: boolean = None,
                 callback: function = None,
                 invert: boolean = None,
                 ### additional
                 model: GLModel = None,
                 predicate: function = None,
                 byres: boolean = None,
                 expand: number = None,
                 ### overload
                 within: WithinSelectionSpec=None,
                 myand: List[AtomSelectionSpec]=None,
                 myor: List[AtomSelectionSpec]=None,
                 mynot: AtomSelectionSpec=None,
                 ):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class ColorschemeSpec(argdict):
    def __init__(self,
                 ssPyMOL: string=None,
                 ssJmol: string=None,
                 Jmol: string=None,
                 default: string=None,
                 amino: string=None,
                 shapely: string=None,
                 nucleic: string=None,
                 chain: string=None,
                 chainHetatm: string=None,
                 prop: string=None,
                 gradient: Gradient=None,
                 map: Object=None,
                 colorfunc: function=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class LineStyleSpec(argdict):
    def __init__(self,
                 hidden: boolean=None,
                 linewidth: number=None,
                 colorscheme: ColorschemeSpec=None,
                 color: ColorSpec=None,
                 opacity: number=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class CrossStyleSpec(argdict):
    def __init__(self,
                 hidden: boolean=None,
                 linewidth: number=None,
                 radius: number=None,
                 scale: number=None,
                 colorscheme: ColorschemeSpec=None,
                 color: ColorSpec=None,
                 opacity: number=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class StickStyleSpec(argdict):
    def __init__(self,
                 hidden: boolean=None,
                 radius: number=None,
                 singleBonds: boolean=None,
                 colorscheme: ColorschemeSpec=None,
                 color: ColorSpec=None,
                 opacity: number=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class SphereStyleSpec(argdict):
    def __init__(self,
                 hidden: boolean=None,
                 radius: number=None,
                 scale: number=None,
                 colorscheme: ColorschemeSpec=None,
                 color: ColorSpec=None,
                 opacity: number=None
                 ):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class CartoonStyleSpec(argdict):
    def __init__(self,
                 color: ColorSpec=None,
                 style: string=None,
                 ribbon: boolean=None,
                 arrows: boolean=None,
                 tubes: boolean=None,
                 thickness: number=None,
                 width: number=None,
                 opacity: number=None,
                 In: Optional=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class AtomStyleSpec(argdict):
    def __init__(self,
                 line: LineStyleSpec=None,
                 cross: CrossStyleSpec=None,
                 stick: StickStyleSpec=None,
                 sphere: SphereStyleSpec=None,
                 cartoon: CartoonStyleSpec=None,
                 clicksphere: ClickSphereStyleSpec=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class BoxSpec(argdict):
    def __init__(self,
                 corner: Vector3=None,
                 center: Vector3=None,
                 dimesion: Union[Vector3, Dimensions, List, None]=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class CurveSpec(argdict):
    def __init__(self,
                 points: Vector3=None,
                 smooth: number=None,
                 radius: number=None,
                 frowArrow: boolean=None,
                 toArrow: boolean=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class CustomShapeSpec(argdict):
    def __init__(self,
                 vertexArr: List[Vector3]=None,
                 normalArr: List[Vector3]=None,
                 faceArr: List[number]=None,
                 color: Union[ColorSpec, List[ColorSpec], None]=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class CylinderSpec(argdict):
    def __init__(self,
                 start: Vector3=None,
                 end: Vector3=None,
                 radius: number=None,
                 fromCap: CAP=None,
                 toCap: CAP=None,
                 dashed: boolean=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class FileFormats(argdict):
    def __init__(self, ):
        super().__init__()
        ...


class IsoSurfaceSpec(argdict):
    def __init__(self,
                 isoval: number=None,
                 color: ColorSpec=None,
                 opacity: number=None,
                 wireframe: boolean=None,
                 linewidth: number=None,
                 smoothness: number=None,
                 coords: List=None,
                 seldist: number=None,
                 voldata: VolumeData=None,
                 volscheme: Gradient=None,
                 volformat: string=None,
                 clickable: boolean=None,
                 callback: function=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class LabelSpec(argdict):
    def __init__(self,
                 font: string=None,
                 fontsize: number=None,
                 fontColor: ColorSpec=None,
                 fontOpacity: number=None,
                 borderThickness: number=None,
                 borderColor: ColorSpec=None,
                 borderOpacity: number=None,
                 backgroundColor: ColorSpec=None,
                 backgroundOpacity: number=None,
                 position: Vector3=None,
                 screenOffset: Vector3=None,
                 inFront: boolean=None,
                 showBackground: boolean=None,
                 fixed: boolean=None,
                 useScreen: boolean=None,
                 backgroundImage: Object=None,
                 alignment: string=None,
                 frame: number=None,
                 ):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class LineSpec(argdict):
    def __init__(self,
                 start: Vector3=None,
                 end: Vector3=None
                 ):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class ParserOptionsSpec(argdict):
    def __init__(self):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

class ShapeSpec(argdict):
    def __init__(self,
                 color: ColorSpec=None,
                 alpha: number=None,
                 wireframe: boolean=None,
                 hidden: boolean=None,
                 linewidth: number=None,
                 clickable: boolean=None,
                 callback: function=None,
                 frame: number=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")

class SphereShapeSpec(argdict):
    def __init__(self,
                 center: Vector3=None,
                 radius: number=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class SurfaceStyleSpec(argdict):
    def __init__(self,
                 opacity: number=None,
                 colorscheme: ColorschemeSpec=None,
                 color: ColorSpec=None,
                 voldata: VolumeData=None,
                 volscheme: Gradient=None,
                 volformat: string=None,
                 map: Object=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class UnitCellStyleSpec(argdict):
    def __init__(self,
                 box: LineStyleSpec=None,
                 astyle: ArrowSpec=None,
                 bstyle: ArrowSpec=None,
                 cstyle: ArrowSpec=None,
                 alabel: string=None,
                 alabelstyle: LabelSpec=None,
                 blabel: string=None,
                 blabelstyle: LabelSpec=None,
                 clabel: string=None,
                 clabelstyle: string=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class ViewerGridSpec(argdict):
    def __init__(self,
                 rows: number=None,
                 cols: number=None,
                 control_all: boolean=None):
        super().__init__()
        self.update(deepcopy(locals()))
        self.remove("self","__class__")


class ViewerSpec(argdict):
    def __init__(self):
        super().__init__()


class VolumetricRendererSpec(argdict):
    def __init__(self):
        super().__init__()





# # sa=AtomSpec(elem="C")
# # print(sa)
#
# import json
# class a():
#     def __init__(self,arg):
#         self.arg=arg
#
# b=a("hello")
# print(isinstance(b,str))
# # print(json.dumps(b))