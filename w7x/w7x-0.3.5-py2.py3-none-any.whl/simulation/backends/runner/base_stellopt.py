import copy

import h5py
import numpy as np


class ExecArg:
    name: str
    dependency: list
    description: str = ""
    path: str = None

    def __init__(
        self,
        name: str,
        dependency: list,
        description: str = None,
        path_required: bool = False,
    ):
        self.name = name
        assert self.name.startswith("-")
        self.dependency = dependency
        if description is not None:
            self.description = description
        self.path_req = path_required

    def set_path(self, path: str):
        assert self.path_req, f"Xfieldlines arg {self.name} does not requires a path"
        self.path = path

    def __eq__(self, other):
        if not isinstance(other, ExecArg):
            raise NotImplementedError(f"Cannot compare with {type(other)}")
        return all(
            [
                self.name == other.name,
                self.dependency == other.dependency,
                self.description == other.description,
                self.path == other.path,
                self.path_req == other.path_req,
            ]
        )

    def __str__(self):
        if self.path_req:
            assert self.path is not None, "set path first"
            return f"{self.name} {self.path}"  # or rna.path.resolve(self.path)
        else:
            return f"{self.name}"


_args = {
    # todo missing pies, spec, screen, reverse, edge, field, raw, auto, noverb, help
    "vmec": ExecArg(
        name="-vmec",
        dependency=[{"-coil": True}],
        description="filename of input",
        path_required=True,
    ),
    "coil": ExecArg("-coil", [], "path to coils file", path_required=True),
    "mgrid": ExecArg(
        "-mgrid", [], "Makegrid style vacuum grid file", path_required=True
    ),
    "vessel": ExecArg(
        "-vessel", [{"-coil": True}], "First wall file", path_required=True
    ),
    "vac": ExecArg("-vac", [{"-coil": True}], "Only compute the vacuum field"),
    "raw": ExecArg("-raw", [{"-coil": True}], "Take Extcur as raw values"),
    "hitonly": ExecArg(
        "-hitonly",
        [{"-coil": True}, {"-vessel": True}],
        "Only save strikepoint locations",
    ),
    "full": ExecArg("-full", [], "Auto calculate axis and edge maximum resolution"),
    "reverse": ExecArg("-reverse", [], "Run in reverse for ConnectionLength"),
    "field_start": ExecArg(
        "-field_start", [], "Init fieldline for FLD run", path_required=True
    ),  # the path should also include the fieldline
}


class GeneralArgs(object):
    # todo rna.path.resolve IF path to vmec input can be aboslute
    def __init__(self, args_req, args_opt, **kwargs):
        self.args = {}
        self.args_opt = args_opt

        # handle required arguments
        for arg in args_req:
            xfieldarg = copy.deepcopy(_args[arg])
            if xfieldarg.path_req:
                path = kwargs.pop(arg)
                xfieldarg.set_path(path)
            self.args.update({arg: xfieldarg})

        self._handle_optional_args(kwargs)

    def _handle_optional_args(self, kwargs: dict):
        for key, item in kwargs.items():
            if key not in self.args_opt:
                raise KeyError(f"{key} not in optional arguments: {self.args_opt}")
            xfieldarg = copy.deepcopy(_args[key])
            if xfieldarg.path_req:
                path = item.pop("path")
                xfieldarg.set_path(path)
            self.args.update({key: xfieldarg})

    def __eq__(self, other):
        if not set(self.args.keys()) == set(other.args.keys()):
            return False
        return all([s == other.args[k] for k, s in self.args.items()])

    def __str__(self):
        return " ".join([str(a) for _, a in self.args.items()])

    def __add__(self, other):
        assert isinstance(other, dict), f"{other} has to be dict with options"
        self._handle_optional_args(other)


class BiotSavartArgs(GeneralArgs):
    args_req = ("vmec", "coil", "vac")
    args_opt = ("reverse", "full")  # optional arguments

    def __init__(self, **kwargs):
        super(BiotSavartArgs, self).__init__(self.args_req, self.args_opt, **kwargs)


class FldArgs(GeneralArgs):
    args_req = ("vmec", "coil", "vessel", "hitonly", "vac")
    args_opt = (
        "reverse",
        "field_start",
        "full",
    )  # full should not be used when init from surface/lcfs

    def __init__(self, **kwargs):
        super(FldArgs, self).__init__(self.args_req, self.args_opt, **kwargs)


def read_fieldlines(res_file):
    # credit to samuel lazerson, PySTEL
    fieldline_data = {}
    # read file
    with h5py.File(res_file, "r") as f:
        # Logicals
        for temp in [
            "ladvanced",
            "laxis_i",
            "lcoil",
            "lmgrid",
            "lmu",
            "lpies",
            "lreverse",
            "lspec",
            "lvac",
            "lvessel",
            "lvmec",
        ]:
            if temp in f:
                fieldline_data[temp] = np.int(f[temp][0])
        # Integers
        for temp in ["nlines", "nphi", "npoinc", "nr", "nsteps", "nz"]:
            if temp in f:
                fieldline_data[temp] = np.int(f[temp][0])
        # Floats
        for temp in ["VERSION", "iota0"]:
            if temp in f:
                fieldline_data[temp] = np.float(f[temp][0])
        # Arrays
        for temp in [
            "phiaxis",
            "raxis",
            "zaxis",
            "B_lines",
            "PHI_lines",
            "R_lines",
            "Z_lines",
            "B_PHI",
            "B_R",
            "B_Z",
            "wall_vertex",
            "wall_faces",
            "wall_strikes",
            "A_R",
            "A_PHI",
            "A_Z",
            "L_lines",
            "Rhc_lines",
            "Zhc_lines",
        ]:
            if temp in f:
                fieldline_data[temp] = np.array(f[temp][:])
    # Make derived arrays
    fieldline_data["X_lines"] = fieldline_data["R_lines"] * np.cos(
        fieldline_data["PHI_lines"]
    )
    fieldline_data["Y_lines"] = fieldline_data["R_lines"] * np.sin(
        fieldline_data["PHI_lines"]
    )
    brtemp = np.zeros(fieldline_data["B_R"].shape)
    bztemp = np.zeros(fieldline_data["B_Z"].shape)
    for i in range(fieldline_data["nr"]):
        brtemp[i, :, :] = (
            fieldline_data["B_R"][i, :, :]
            * fieldline_data["B_PHI"][i, :, :]
            / fieldline_data["raxis"][i]
        )
        bztemp[i, :, :] = (
            fieldline_data["B_Z"][i, :, :]
            * fieldline_data["B_PHI"][i, :, :]
            / fieldline_data["raxis"][i]
        )
    fieldline_data["B_R"] = brtemp
    fieldline_data["B_Z"] = bztemp
    return fieldline_data


def calc_iota(data):
    # credit to samuel lazerson, PySTEL

    import numpy as np

    x = np.zeros(data["R_lines"].shape)
    y = np.zeros(data["Z_lines"].shape)
    nstep = data["nsteps"]
    for i in range(data["nsteps"]):
        x[i, :] = data["R_lines"][i, :] - data["R_lines"][i, 0]
        y[i, :] = data["Z_lines"][i, :] - data["Z_lines"][i, 0]
    theta = np.arctan2(y, x)
    dtheta = np.diff(theta, axis=0)
    dtheta = np.where(dtheta < -np.pi, dtheta + 2 * np.pi, dtheta)
    dtheta = np.where(dtheta > np.pi, dtheta - 2 * np.pi, dtheta)
    theta = np.cumsum(dtheta, axis=0)
    out = {}
    out["rho"] = np.mean(np.sqrt(x * x + y * y), axis=0)
    out["iota"] = np.zeros(out["rho"].shape)
    out["iota_err"] = np.zeros(out["rho"].shape)
    for i in range(data["nlines"]):
        p, residuals, _, _, _ = np.polyfit(
            data["PHI_lines"][0 : nstep - 1, i], theta[:, i], 1, full=True
        )
        out["iota"][i] = p[0]
        out["iota_err"][i] = np.sqrt(residuals)
    out["iota"][0] = 2 * out["iota"][1] - out["iota"][2]
    return out


if __name__ == "__main__":
    pass
    res = read_fieldlines("../../../../../../fieldlines_w7x/fieldlines_w7x_dbm+250.h5")
    iota = calc_iota(res)
    print(iota["iota"])

    # res = read_fieldlines('../stellopt/tmp/fieldlines_infile.h5')
    # iota = calc_iota(res)
    # print(iota['iota'])

    # p = BiotSavartArgs(vmec='infile', coil='abc')
    # p + {'reverse': True}
    # print(f'{p}')
