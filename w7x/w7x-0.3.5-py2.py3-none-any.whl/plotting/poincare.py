"""
specific methods for poincare plotting
"""
import typing

import tfields
import rna
import w7x


class Poincare(rna.plotting.Figure):
    @property
    def state(self):
        return self.data

    @state.setter
    def state(self, state):
        self.data = state

    def _plot(self, **kwargs):
        """
        Args:
            state
            sufaces: poincare Surfaces
            assemblies: list of cuts through assemblies
        """
        axes = self.gca()
        rmin = self.retrieve(
            kwargs, "rmin", "rMin", default=4.0, keep=False, deprecated=["rMin"]
        )
        rmax = self.retrieve(
            kwargs, "rmax", "rMax", default=6.6, keep=False, deprecated=["rMax"]
        )
        zmin = self.retrieve(
            kwargs, "zmin", "zMin", default=-1.3, keep=False, deprecated=["zMin"]
        )
        zmax = self.retrieve(
            kwargs, "zmax", "zMax", default=+1.3, keep=False, deprecated=["zMax"]
        )
        labels = kwargs.pop("labels", ["r (m)", "z (m)"])
        phi = kwargs.pop("phi", None)

        self.set_aspect_equal(axes)
        self.set_limits(axes, [rmin, rmax], [zmin, zmax])
        self.set_labels(axes, *labels)
        state = self.state
        if state:
            if state.has(w7x.model.Assembly):
                self.plot_assembly(
                    axes,
                    state.assembly,
                    phi=phi,
                )
            if (
                state.has(w7x.model.Traces)
                and state.traces.poincare_surfaces is not None
            ):
                self.plot_poincare_surfaces(
                    axes,
                    state.traces.poincare_surfaces,
                    phi=phi,
                )

    @rna.plotting.plot_signature
    def plot_poincare_surfaces(
        self, axes, poincare_surfaces: typing.List[tfields.Points3D], **kwargs
    ):
        """
        Args:
            poincare_surfaces (list of Points3D): each Points3D instance is one
                fieldLine followed around the torus
            **kwargs:
                phi (float): phi in rad
                method (str): plot method (scatter or plot)

        """
        phi = self.retrieve(kwargs, "phi", default=None, keep=False)

        kwargs.setdefault("y_index", 2)
        method = kwargs.pop("method", "scatter")
        if method == "scatter":
            kwargs.setdefault("marker", ".")
            kwargs.setdefault("s", 1)

        color_given = True
        if "color" not in kwargs:
            color_given = False
            cmap, _, _ = self.get_norm_args(kwargs)
            color_cycle = rna.plotting.colors.color_cycle(cmap, len(poincare_surfaces))
        elif isinstance(kwargs.get("color"), list):
            color_given = False  # hack to set the color from list
            color_cycle = iter(kwargs.get("color"))

        artists = []
        for i, surface_points in enumerate(poincare_surfaces):
            with surface_points.tmp_transform(tfields.bases.CYLINDER):
                phi_surface = surface_points[:, 1]
                if phi is None:
                    phi = phi_surface[0]
                mask = phi_surface == phi
                if ~mask.any():
                    continue
                if not color_given:
                    kwargs["color"] = next(color_cycle)
                artists.append(surface_points[mask].plot(axes=axes, **kwargs))
        return artists

    @rna.plotting.plot_signature
    def plot_assembly(self, axes, assembly, **kwargs):
        """
        Plot the assembly as a sliue
        """
        phi = self.retrieve(kwargs, "phi", default=None, keep=False)
        artists = []
        for component in assembly.get_components(flat=True):
            phi_slice = component.slices[phi]
            if phi_slice is None:
                continue
            print(component.color)
            artists.append(
                phi_slice.plot(
                    axes=axes,
                    map=2,
                    x_index=0,
                    y_index=2,
                    color=component.color or "k",
                    **kwargs
                )
            )
        return artists


if __name__ == "__main__":
    ps = tfields.Points3D.load("test.npz")
    poincare_figure = Poincare()
    # poincare_figure.plot_poincare_surfaces([ps])
    poincare_figure.plot([ps])
    poincare_figure.show()
