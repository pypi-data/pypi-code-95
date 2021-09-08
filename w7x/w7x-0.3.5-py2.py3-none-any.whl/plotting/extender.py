"""
specific methods for poincare plotting
"""
import matplotlib as mpl

import tfields
import rna
import w7x


def plot_field(tensor_field: tfields.TensorFields, **kwargs):
    """
    Plot the magnetic field
    """
    tensor_field.transform(tfields.bases.CARTESIAN)
    kwargs.setdefault("field_index", 0)
    kwargs.setdefault("scale_units", "xy")
    kwargs.setdefault(
        "scale", 7.5  # 1 / tensor_field.min_dists().min()  # min_dists is expensive
    )  # 1 [T] per unit length
    kwargs.setdefault("norm", mpl.colors.LogNorm)
    kwargs.setdefault("normalize", False)
    kwargs.setdefault("color", "norm")
    kwargs.setdefault("cmap", "coolwarm")
    artist = tensor_field.plot(**kwargs)
    return artist


class FieldFigure(rna.plotting.Figure):
    """
    Figure providing plotting for mgrid fields.
    """

    def __init__(self, data=None):
        if isinstance(data, w7x.State):
            state = data
            if state.has(w7x.model.Traces) and state.equilibrium.field is not None:
                data = (state.equilibrium.field,)
            else:
                data = None
        super().__init__(data=data)

    @rna.plotting.plot_signature
    def _plot(self, axes, **kwargs):
        """
        Args:
            state
            sufaces: poincare Surfaces
            assemblies: list of cuts through assemblies
        """
        labels = kwargs.pop("labels", ["x (m)", "y (m)"])

        self.set_aspect_equal(axes)
        self.set_labels(axes, *labels)
        if self.data is not None:
            artist = self.plot_field(self.data, axes=axes, **kwargs)
            rna.plotting.set_colorbar(axes, artist, label=r"$B\;(T)$", extend="max")

        return artist

    @staticmethod
    # pylint:disable=redefined-outer-name
    def plot_field(field, **kwargs):
        """
        Plot the magnetic field
        """
        artist = plot_field(field, **kwargs)
        return artist


if __name__ == "__main__":
    path = "tests/resources/extender/field_dboe_id_1000_1000_1000_1000_+0000_+0000_v_00_pres_00_it_12.npz"  # noqa, pylint:disable=invalid-name,line-too-long
    field = tfields.TensorGrid.load(path)
    z_vals = field[:, 2]
    mask = z_vals == 0.008579881656804789
    field_sl = field[mask]

    fig = FieldFigure(field_sl)
    fig.plot(scale_units="xy", scale=10)
    fig.show()
