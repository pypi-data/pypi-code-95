from IPython.display import publish_display_data
from typing import Dict
import json
import sys

from .type import *
from .utils import *

import py3Dmol



class view():
    def __init__(self, width="600pt", height="400pt", position="relative", divstyle: Optional[Dict] = None,
                 js="https://3dmol.org/build/3Dmol.js"):#
        self._id = seed()
        self._style = "".join([i + ":" + divstyle[i] + ";" for i in divstyle]) if divstyle != None else ""
        self._startjs =f'<div id="{self._id}" style="width: {width}; height: {height};position: {position};{self._style}"></div>\n' \
                       f'<script>\n'+'''var loadScriptAsync = function(uri){
  return new Promise((resolve, reject) => {
    var tag = document.createElement('script');
    tag.src = uri;
    tag.async = true;
    tag.onload = () => {
      resolve();
    };
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
});
};

if(typeof $3Dmolpromise === 'undefined') {
$3Dmolpromise = null;
  $3Dmolpromise = loadScriptAsync(\''''\
                       +f'{js}\');\n}}\n$(function() {{\n\tviewer = $3Dmol.createViewer($("#{self._id}"));\n' \
                        f'\tviewer.zoomTo();\n'
        self._updatejs = ""
        self._endjs = "\tviewer.render()\n});\n</script>"

    def __getattr__(self, item):
        def makejs(*args):
            cmd = '\tviewer.%s(' % item
            for arg in args:
                cmd += '%s,' % json.dumps(arg)
            cmd = cmd.rstrip(',')
            cmd += ');\n'
            self._updatejs += cmd

        return makejs  # return from getattr

    def js(self):
        return self._startjs + self._updatejs + self._endjs

    def show(self):
        # publish_display_data({'text/html': self.js()})
        html=self.js()
        publish_display_data({'application/3dmoljs_load.v0': html, 'text/html': html}, metadata={})


    def _update(self, fname, items):
        # TODO: 需要注意
        args = [i[1] for i in items if i[0] not in ['__class__', "self", "name"] and i[1] != None]
        head = ''
        for i in items:
            if i[0] == "name" and i[1] != None:
                assert i[1] != "viewer", "The name of model/shape/label/object shouldn't be viewer!"
                head = f"{i[1]} ="
                break
        cmd = '\t%sviewer.%s(' % (head, fname)
        for arg in args:
            cmd += '%s,' % json.dumps(arg) if not isinstance(arg,Object) else arg.name
        cmd = cmd.rstrip(',')
        cmd += ');\n'
        self._updatejs += cmd

    '''
        impletement!
    '''

    def clear(self):
        '''Clear scene of all objects'''
        self._update(sys._getframe().f_code.co_name, locals().items())

    def render(self):
        '''
        Render current state of viewer, after adding/removing models, applying styles, etc.
        '''
        self._update(sys._getframe().f_code.co_name, locals().items())

    def zoom(self, factor: number, animationDuration: number, fixedPath: boolean):
        ''' Zoom current view by a constant factor
        :param factor: Magnification factor. Values greater than 1 will zoom in, less than one will zoom out. Default 2.
        :param animationDuration: an optional parameter that denotes the duration of a zoom animation
        :param fixedPath: if true animation is constrained to requested motion, overriding updates that happen during the animation
        :return:
        '''
        self._update(sys._getframe().f_code.co_name, locals().items())

    def zoomTo(self, sel: Object, animationDuration: number, fixedPath: boolean):
        '''
        Zoom to center of atom selection. The slab will be set appropriately for
the selection, unless an empty selection is provided, in which case there will be no slab.
        :param sel: Selection specification specifying model and atom properties to select. Default: all atoms in viewer
        :param animationDuration: an optional parameter that denotes the duration of a zoom animation
        :param fixedPath: if true animation is constrained to requested motion, overriding updates that happen during the animation *
        '''
        self._update(sys._getframe().f_code.co_name, locals().items())

    @property
    def add(self):return self._add(self)
    @property
    def remove(self):return self._remove(self)
    @property
    def set(self):return self._set(self)
    @property
    def get(self):return self._get(self)
    @property
    def animate(self):return self._animate(self)
    @property
    def export(self):return self._export(self)
    @property
    def _test(self):return self.__test(self)

    class _add(object):
        def __init__(self,obj):
            self._obj=obj

        def createModelFrom(self, sel: AtomSelectionSpec, extract: boolean):
            '''
            Create a new model from atoms specified by sel.
            If extract, removes selected atoms from existing models
            :param sel: 	Atom selection specification
            :param extract: If true, remove selected atoms from existing models
            :return:  $3Dmol.GLModel
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def Model(self, data: string, format: string, options: ParserOptionsSpec = None):
            '''
            Create and add model to viewer, given molecular data and its format
            :param data: Input data
            :param format: Input format ('pdb', 'sdf', 'xyz', 'pqr', or 'mol2')
            :param options: format dependent options. Attributes depend on the input file format
            :return: $3Dmol.GLModel
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def Arrow(self, spec: ArrowSpec):
            '''
            Create and add arrow shape
            :param spec: Style specification
            :return: $3Dmol.GLShape
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def Box(self, spec: BoxSpec):
            '''
            Create and add box shape. This method provides a shorthand way to create a box shape object
            :param spec: Box shape style specification
            :return: $3Dmol.GLShape
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        # def addCurve(self, spec: CurveSpec):
        #     '''
        #     Create and add Curve shape
        #     :param spec: 	Style specification
        #     :return: $3Dmol.GLShape
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        # def addCustom(self, spec: CustomShapeSpec):
        #     '''
        #     Add custom shape component from user supplied function
        #     :param spec: Style specification
        #     :return: $3Dmol.GLShape
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def Cylinder(self, spec: CylinderSpec):
            '''
            Create and add cylinder shape
            :param spec: Style specification
            :return: $3Dmol.GLShape
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def Label(self, text: string, options: LabelSpec, sel: AtomSelectionSpec, noshow: boolean=None):
            '''
            Add label to viewer
            :param text: 	Label text
            :param options: Label style specification
            :param sel: Set position of label to center of this selection
            :param noshow: if true, do not immediately display label - when adding multiple labels this is more efficient
            :return:$3Dmol.Label
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        # def addIsosurface(self, data: VolumeData, spec: IsoSurfaceSpec):
        #     '''
        #         Construct isosurface from volumetric data. This is more flexible
        #     than addVolumetricData, but can not be used with py3Dmol
        #     :param data: volumetric data
        #     :param spec: Shape style specification
        #     :return: $3Dmol.GLShape
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        # def addAsOneMolecule(self, data: string, format: string):
        #     '''
        #     Create and add model to viewer. Given multimodel file and its format, all atoms are added to one model
        #     :param data:
        #     :param format:
        #     :return: $3Dmol.GLModel
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def Line(self, spec: LineSpec):
            '''
            Create and add line shape
            :param spec: Style specification, can specify dashed, dashLength, and gapLength
            :return: $3Dmol.GLShape
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        # def addMesh(self, mesh: Mesh, style: Object):
        #     '''
        #     Adds an explicit mesh as a surface object.
        #     :param mesh:  $3Dmol.Mesh
        #     :param style: Object
        #     :return:
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        # def addModels(self, data: string, format: string):
        #     '''
        #     Given multimodel file and its format, add atom data to the viewer as separate models
        #     and return list of these models
        #     :param data: Input data
        #     :param format: 	Input format (see FileFormats)
        #     :return: Array.<$3Dmol.GLModel>
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())
        #
        # def addModelsAsFrames(self, data: string, format: string):
        #     '''
        #     Create and add model to viewer. Given multimodel file and its format,
        #     different atomlists are stored in model's frame
        #     property and model's atoms are set to the 0th frame
        #     :param data: Input data
        #     :param format: 	Input format (see FileFormats)
        #     :return: $3Dmol.GLModel
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def PropertyLabels(self, prop: string, sel: AtomSelectionSpec, style: LabelSpec):
            '''
            Add property labels. This will generate one label per a selected
            atom at the atom's coordinates with the property value as the label text.
            :param prop: property name
            :param sel: AtomSelectionSpec
            :param style: LabelSpec
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())


        def ResLabels(self, sel: AtomSelectionSpec, style: LabelSpec, byframe: boolean):
            '''
            Add residue labels. This will generate one label per a
            residue within the selected atoms. The label will be at the
            centroid of the atoms and styled according to the passed style.
            The label text will be [resn][resi]
            :param sel: AtomSelectionSpec
            :param style:LabelSpec
            :param byframe: if true, create labels for every individual frame, not just current
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())

        def Shape(self, shapeSpec: ShapeSpec):
            '''
            Add shape object to viewer
            :param shapeSpec: style specification for label
            :return: $3Dmol.GLShape
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def Sphere(self, spec: SphereShapeSpec):
            '''
            Create and add sphere shape. This method provides a shorthand
            way to create a spherical shape object
            :param spec: Sphere shape style specification
            :return: $3Dmol.GLShape
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def Style(self, sel: AtomSelectionSpec, style: AtomStyleSpec):
            '''
            Add style properties to all selected atoms
            :param sel: Atom selection specification
            :param style: style spec to add to specified atoms
            :return:
            '''
            self._obj._update("add"+sys._getframe().f_code.co_name, locals().items())

        # def addSurface(self, type: SurfaceType, style: SurfaceStyleSpec, atomsel: AtomSelectionSpec,
        #                allsel: AtomSelectionSpec, focus: AtomSelectionSpec, surfacecallback: function):
        #     '''
        #     Add surface representation to atoms
        #     :param type: 	$3Dmol.SurfaceType | string	   Surface type (VDW, MS, SAS, or SES)
        #     :param style: optional style specification for surface material (e.g. for different coloring scheme, etc)
        #     :param atomsel: Show surface for atoms in this selection
        #     :param allsel: Use atoms in this selection to calculate surface; may be larger group than 'atomsel'
        #     :param focus: Optionally begin rendering surface specified atoms
        #     :param surfacecallback: function to be called after setting the surface
        #     :return:
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        # def addUnitCell(self, model: GLModel, spec: UnitCellStyleSpec):
        #     '''
        #     Create and add unit cell visualization.
        #     :param model: Model with unit cell information (e.g., pdb derived). If omitted uses most recently added model.
        #     :param spec: visualization style
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

        # # TODO: need to be attention of [my]or here
        # def addVolumetricData(self, data: string, format: string, myor: IsoSurfaceSpec):
        #     '''
        #     Construct isosurface from volumetric data in gaussian cube format
        #     :param data: Input file contents
        #     :param format: 	Input file format
        #     :param myor: {VolumetricRenderSpec} spec - Shape style specification
        #     :return: $3Dmol.GLShape
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())
        #
        # def addVolumetricRender(self, data: VolumeData, spec: VolumetricRendererSpec):
        #     '''
        #     Create volumetric renderer for volumetricData
        #     :param data: 	volumetric data
        #     :param spec:    specification of volumetric render
        #     :return:        $3Dmol.GLShape
        #     '''
        #     self._obj._update(sys._getframe().f_code.co_name, locals().items())

    class _remove(object):
        def __init__(self,obj):
            self._obj=obj

        def AllLabels(self):
            '''Delete all existing models'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def AllModels(self):
            '''Delete all existing models'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def AllShapes(self):
            '''Remove all shape objects from viewer'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def AllSurfaces(self):
            '''Remove all surfaces.'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def Label(self, label: Label):
            '''Remove label from viewer'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def Model(self, model: GLModel):
            '''Delete specified model from viewer'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def Shape(self, shape: GLShape):
            '''Remove shape object from viewer'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def Surface(self, surf: number):
            '''Remove surface with given ID'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

        def UnitCell(self, model: GLModel):
            '''Remove unit cell visualization from model.'''
            self._obj._update("remove"+sys._getframe().f_code.co_name, locals().items())

    class _set(object):
        def __init__(self,obj):
            self._obj=obj

        def fitSlab(self, sel: Object):
            '''
            Adjust slab to fully enclose selection (default everything).
            :param sel:Selection specification specifying model and atom properties to select. Default: all atoms in viewer
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def replicateUnitCell(self, A: int, B: int, C: int, model: GLModel):
            '''
            Replicate atoms in model to form a super cell of the specified dimensions.
    Original cell will be centered as much as possible.
            :param A: number of times to replicate cell in X dimension.
            :param B: number of times to replicate cell in Y dimension. If absent, X value is used.
            :param C: number of times to replicate cell in Z dimension. If absent, Y value is used.
            :param model: Model with unit cell information (e.g., pdb derived). If omitted uses most recently added model.
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def resize(self):
            '''Resize viewer according to containing HTML element's dimensions'''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def enableFog(self, fog: boolean):
            '''Enable/disable fog for content far from the camera'''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def AutoEyeSeparation(self):
            '''Used for setting an approx value of eyeSeparation. Created for calling by StereoViewer object
            :return: camera x position
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def BackgroundColor(self, hex: ColorSpec, a: number = 1):
            '''
            Set the background color (default white)
            :param hex: Hexcode specified background color, or standard color spec
            :param a: Alpha level (default 1.0)
            :return:
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def CameraParameters(self, parameters):
            '''
            Set camera parameters (distance to the origin and field of view)
            :param parameters:
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Clickable(self, sel: AtomSelectionSpec, clickable: boolean, callback: function = None):
            '''
            Set click-handling properties to all selected atomsthis.
            :param sel: atom selection to apply clickable settings to
            :param clickable: whether click-handling is enabled for the selection
            :param callback: function called when an atom in the selection is clicked
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def ColorByElement(self, sel: AtomSelectionSpec, colors: ColorSpec):
            '''
            :param sel:  	AtomSelectionSpec
            :param colors: type
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def ColorByProperty(self, prop, scheme):
            '''
            :param prop:
            :param scheme:
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Container(self, element: Union[Object, string]):
            '''
            Change the viewer's container element
            Also useful if the original container element was removed from the DOM.
            :param element: 	Object | string	Either HTML element or string identifier. Defaults to the element used to initialize the viewer.
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def DefaultCartoonQuality(self):
            '''
            Set the default cartoon quality for newly created models. Default is 5.
            Current models are not affected.
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Frame(self, framenum: number):
            '''
            Sets the atomlists of all models in the viewer to specified frame.
            Shapes and labels can also be displayed by frame.
            Sets to last frame if framenum out of range
            :param framenum: fame index to use, starts at zero
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Height(self, h: number):
            '''Set viewer height'''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Hoverable(self, sel: AtomSelectionSpec, hoverable: boolean,
                         hover_callback: function, unhover_callback: function):
            '''
            TODO
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def HoverDuration(self, hoverDuration: number):
            '''
            TODO
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def InternalState(self):
            '''
            Overwrite internal state of the viewer with passed object
            which should come from getInternalState.
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def LabelStyle(self, label: Label, stylespec: LabelSpec):
            '''
            Modify existing label's style
            :param label: $3Dmol label
            :param stylespec: Label style specification
            :return: $3Dmol.Label
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def LabelText(self, label: Label, text: string):
            '''
            Modify existing label's text
            :param label: $3Dmol label
            :param text: Label text
            :return: $3Dmol.Label
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def PerceivedDistance(self, distance: number = None):
            '''TODO
            Set the distance between the model and the camera
            Essentially zooming. Useful while stereo rendering.
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Projection(self, set="orthographic"):
            '''
            Set view projection scheme. Either orthographic or perspective.
            Default is perspective. Orthographic can also be enabled on viewer creation
            by setting orthographic to true in the config object.
            :param set: perspective|orthographic
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Slab(self, near: number, far: number):
            '''
            Set slab of view (contents outside of slab are clipped).
            Must call render to update.
            :param near: 	near clipping plane distance
            :param far:   far clipping plane distance
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def StateChangeCallback(self):
            '''TODO'''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Style(self, sel: AtomSelectionSpec = dict(), style: AtomStyleSpec = dict()):
            '''
            Set style properties to all selected atoms
            :param sel: Atom selection specification
            :param style: Style spec to apply to specified atoms
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def SurfaceMaterialStyle(self, surf: number, style: SurfaceStyleSpec):
            '''
            Set the surface material to something else, must render change
            :param surf: Surface ID to apply changes to
            :param style: new material style specification
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def View(self, arg: List[number]):
            '''
            Sets the view to the specified translation, zoom, and rotation.
            :param arg:Array formatted identically to the return value of getView
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def ViewChangeCallback(self):
            '''
            Set a callback to call when the view has potentially changed.
            TODO
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def ViewStyle(self, style):
            '''TODO
            Set global view styles.
            :param style:
            :return:
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def Width(self, w: number):
            '''Set viewer width in pixels'''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

        def ZoomLimits(self, lower: number, upper: number):
            '''
            Set lower and upper limit stops for zoom.
            :param lower:  limit on zoom in (positive number). Default 0.
            :param upper: 	limit on zoom out (positive number). Default infinite.
            '''
            self._obj._update("set"+sys._getframe().f_code.co_name, locals().items())

    class _get(object):
        def __init__(self,obj):
            self._obj=obj

        def selectToModelDistance(self):
            '''
            return list of atoms selected by sel
            :return: Array.<Object>
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def targetedObjects(self, x: number, y: number, object):
            '''
            Return a list of objects that intersect that at the specified viewer position.
            :param x: x position in screen coordinates
            :param y: y position in screen coordinates
            :param object: list of objects or selection object specifying what object to check for targeting
            :return:
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def selectAtoms(self, sel: AtomSelectionSpec):
            '''
            return list of atoms object. Yet it should be a str in python:)
            :param sel: AtomSelectionSpec
            :return: Array.<Object>
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def Frame(self):
            '''
            Gets the current viewer frame.
            :return:
            '''
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())

        def InternalState(self):
            '''
            Return object representing internal state of
            the viewer appropriate for passing to setInternalState
            :return:
            '''
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())

        def Model(self, id: number):
            '''
            Return specified model
            :param id: Retrieve model with specified id
            :return: GLModel
            '''
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())
            return GLModel(random_name())

        def NumFrames(self):
            """
            Returns the number of frames that the model with the most frames in the viewer has
            :return:
            """
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())

        def PerceivedDistance(self):
            '''
            Return the z distance between the model and the camera
            :return:
            '''
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())

        def Slab(self, near: number, far: number):
            '''
            Get slab of view (contents outside of slab are clipped).
            :param near: near clipping plane distance
            :param far: far clipping plane distance
            :return:
            '''
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())

        def View(self):
            '''
            Returns an array representing the current viewpoint.
            Translation, zoom, and rotation quaternion.
            :return: [ pos.x, pos.y, pos.z, rotationGroup.position.z, q.x, q.y, q.z, q.w ]
            '''
            self._obj._update("get"+sys._getframe().f_code.co_name, locals().items())

    class _animate(object):
        def __init__(self,obj):
            self._obj=obj

        def animate(self, options: Object):
            '''TODO: Animate all models in viewer from their respective frames'''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def center(self, sel: Object, animationDuration: number, fixedPath: boolean):
            ''' TODO
            Re-center the viewer around the provided selection (unlike zoomTo, does not zoom).
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def isAnimated(self):
            '''
            Return true if viewer is currently being animated, false otherwise
            :return: boolean
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def modelToScreen(self, coor: Union[Object, List[Object]]):
            ''' TODO
            Convert model coordinates to screen coordinates.
            :param coor: 	an object or list of objects with x,y,z attributes (e.g. an atom)
            :return: object | list
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def rotate(self, angle: number, axis: string, animationDuration: number, fixedPath: boolean):
            """
            Rotate scene by angle degrees around axis
            :param angle: Angle, in degrees, to rotate by.
            :param axis:Axis ("x", "y", "z", "vx", "vy", or "vz") to rotate around.
                            Default "y". View relative (rather than model relative) axes are prefixed with v.
                            Axis can also be specified as a vector.
            :param animationDuration:   an optional parameter that denotes
                                        the duration of the rotation animation. Default 0 (no animation)
            :param fixedPath: if true animation is constrained to
                                requested motion, overriding updates that happen during the animation *
            """
            self._update(sys._getframe().f_code.co_name, locals().items())

        def screenOffsetToModel(self):
            '''
            For a given screen (x,y) displacement return model displacement
            :return: model displacement
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def screenToModelDistance(self):
            '''
            Distance from screen coordinate to model coordinate assuming screen point
    is projected to the same depth as model coordinate
            :return:
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def spin(self, axis: string, speed: number):
            '''
            Continuously rotate a scene around the specified axis.
            Call $3Dmol.GLViewer.spin(false) to stop spinning.
            :param axis:    Axis ("x", "y", "z", "vx", "vy", or "vz") to rotate around.
                         Default "y". View relative (rather than model relative) axes are prefixed with v.
            :param speed: Speed multiplier for spinning the viewer. 1 is default and a negative
                        value reverses the direction of the spin.
                        value reverses the direction of the spin.
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def stopAnimate(self):
            '''Stop animation of all models in viewer'''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def translate(self, x: number, y: number, animationDuration: number, fixedPath: boolean):
            '''
            Translate current view by x,y screen coordinates
            This pans the camera rather than translating the model.
            :param x: Relative change in view coordinates of camera
            :param y: Relative change in view coordinates of camera
            :param animationDuration: an optional parameter that denotes the duration of a zoom animation
            :param fixedPath: if true animation is constrained to requested motion, overriding updates that happen during the animation *
            :return:
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def translateScene(self, x: number, y: number, animationDuration: number, fixedPath: boolean):
            '''
            Translate current models by x,y screen coordinates
    This translates the models relative to the current view. It does
    not change the center of rotation.
            :param x: Relative change in x screen coordinate
            :param y: 	Relative change in y screen coordinate
            :param animationDuration: an optional parameter that denotes the duration of a zoom animation
            :param fixedPath: if true animation is constrained to requested motion, overriding updates that happen during the animation *
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

        def vibrate(self, numFrames: number, amplitude: number, bothWays: boolean, arrowSpec: ArrowSpec):
            '''
            If atoms have dx, dy, dz properties (in some xyz files), vibrate populates each model's frame property based on parameters.
            Models can then be animated
            :param numFrames: number of frames to be created, default to 10
            :param amplitude: amplitude of distortion, default to 1 (full)
            :param bothWays: if true, extend both in positive and negative directions by numFrames
            :param arrowSpec: specification for drawing animated arrows. If color isn't specified, atom color (sphere, stick, line preference) is used.
            '''
            self._update(sys._getframe().f_code.co_name, locals().items())

    class _export(object):
        def __init__(self,obj):
            self._obj=obj

        def exportJSON(self, includeStyles: boolean, modelID: number):
            '''
            Export one or all of the loaded models into ChemDoodle compatible JSON.
            :param includeStyles: Whether or not to include style information.
            :param modelID: Optional parameter for which model to export. If left out, export all of them.
            :return: string
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def exportVRML(self):
            '''return a VRML string representation of the scene. Include VRML header information'''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())


        def pdbData(self, sel: Object):
            '''
            Return pdb output of selected atoms (if atoms from pdb input)
            :param sel: Selection specification specifying model and atom properties to select. Default: all atoms in viewer
            :return: PDB string of selected atoms
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def pngURI(self):
            '''
            Return image URI of viewer contents (base64 encoded).
            :return: image URI
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

    class __test(object):
        def __init__(self,obj):
            self._obj=obj

        def hasVolumetricRender(self):
            '''
            Return true if volumetric rendering is supported (WebGL 2.0 required)
            :return: boolean
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def linkViewer(self):
            '''TODO'''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())

        def mapAtomProperties(self, props: Object, sel: AtomSelectionSpec):
            '''
            Add specified properties to all atoms matching input argument
            :param props:	either array of atom selectors with associated props, or function that takes atom and sets its properties
            :param sel: 	subset of atoms to work on - model selection must be specified here
            '''
            self._obj._update(sys._getframe().f_code.co_name, locals().items())



if __name__ == "__main__":
    ...

    from rdkit import Chem
    from rdkit.Chem import AllChem

    a = view()
    m = Chem.AddHs(Chem.MolFromSmiles("C"))
    AllChem.EmbedMolecule(m)
    m = Chem.MolToMolBlock(m)
    a.add.Model(m, format="mol")
    b=a.get.Model(9)
    print(b.name)
    # a.add
    # a.show()
    # print(a.js())
