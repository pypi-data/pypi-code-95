import typing
import tfields
import numpy as np


class CoilStruct(typing.TypedDict):
    xyz: tfields.Points3D
    currents: np.ndarray
    group: int
    groupName: str
    n: int


class StellOptCoils:

    # The format for coils files is defined in LIBSTELL/Sources/Modules/biotsavart.f
    # todo connect to w7x.model.coilset mm_ids, s.t. state -> coilsfile xfieldlines is possible
    #   implement mirror, periods $nfp
    #   check the current parameter of a coils file, its either coil filaments or 1

    def __init__(self, cdat: typing.List[CoilStruct], nfp: int):
        self._data = cdat
        self.periodicity = nfp

    @classmethod
    def from_file(cls, path: str):
        with open(path, "r") as f:
            lines = f.readlines()
        cls._check_format(lines)
        coil_coords = cls._file_to_struct(lines)
        nfp = int(lines[0][9])
        return cls(coil_coords, nfp)

    @classmethod
    def from_mm_id(self):
        # w7x api?
        raise NotImplementedError

    def to_file(self, path: str):
        file_str = "periods  1\nbegin filament\nmirror NIL"
        for coil in self._data:
            for point, current in zip(coil["xyz"], coil["currents"]):
                file_str += f"\n  {point[0]}  {point[1]}  {point[2]}  {current}"
            file_str += f'  {coil["group"]}  {coil["groupName"]}'
        with open(path, "w+") as f:
            f.write(file_str)

    @staticmethod
    def _check_format(lines):
        assert (
            lines[0][:7] == "periods"
        ), f'file should start with "periods" but starts with {lines[0][:8]}'
        assert lines[1][:14] == "begin filament", (
            f'First line should be "begin filaments" '
            f"but starts with {lines[1][:14]}"
        )
        assert (
            lines[-1][:3] == "end"
        ), f'file should end with "end" but ends with {lines[-1][:3]}'

    @staticmethod
    def _file_to_struct(lines: list) -> typing.List[CoilStruct]:
        _thresh = 1e-13  # threshold for closing coils
        coils = []
        xs, ys, zs, currents = [], [], [], []

        for i, line in enumerate(lines[3:-1]):
            vals = line.split()
            assert (len(vals) == 4) or (
                len(vals) == 6
            ), f"line {i+3} does not have 4 or 6 elements"
            x, y, z, current = vals[:4]
            xs.append(float(x))
            ys.append(float(y))
            zs.append(float(z))
            currents.append(float(current))
            if len(vals) == 6:  # end of coil
                assert (
                    xs[-1] - xs[0] < _thresh
                ), f"Coil is not closed in x: {x[0]} to {x[-1]}"
                assert (
                    ys[-1] - ys[0] < _thresh
                ), f"Coil is not closed in y: {y[0]} to {y[-1]}"
                assert (
                    zs[-1] - zs[0] < _thresh
                ), f"Coil is not closed in z: {z[0]} to {z[-1]}"

                current_group = vals[4]
                current_group_name = vals[5]
                assert (
                    i > 2
                ), "circular or infinite straight line not implemented"  # todo
                xyz = tfields.Points3D(np.transpose([xs, ys, zs]))
                coils.append(
                    CoilStruct(
                        xyz=xyz,
                        currents=np.array(currents),
                        n=i,
                        group=current_group,
                        groupName=current_group_name,
                    )
                )
                xs, ys, zs, currents = [], [], [], []
        return coils


if __name__ == "__main__":
    c = StellOptCoils.from_file("/home/thuni/ipp/prog/datastore/coils.w7x_mc_sc_tc_15")
    c.to_file("./abc")
