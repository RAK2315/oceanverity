"""The Grid: model data in the shape the provider published it.

This is the scientific source of truth. The Volume is derived from it for rendering and is
lossy by design; anything that makes a claim about the ocean - a Collocation, a Residual, the
number on a tooltip - reads the Grid, not the Volume.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Grid:
    """One Field at one Timestep on its native axes: values indexed [level, lat, lon]."""

    levels: np.ndarray
    latitudes: np.ndarray
    longitudes: np.ndarray
    values: np.ndarray

    def __post_init__(self) -> None:
        expected = (len(self.levels), len(self.latitudes), len(self.longitudes))
        if self.values.shape != expected:
            raise ValueError(f"values shape {self.values.shape} does not match axes {expected}")

    def column_at(self, latitude: float, longitude: float) -> np.ndarray:
        """The model's water column at an arbitrary position: one value per Level.

        Bilinear between the four surrounding nodes. A Masked node makes the result Masked at
        that Level rather than falling back to the nodes that do have data - near a coastline
        the nodes that have data are the open ocean, and blending them in would quietly
        manufacture a sea temperature for a point that is on land.
        """
        row, row_weight = self.bracket(self.latitudes, latitude, "latitude")
        col, col_weight = self.bracket(self.longitudes, longitude, "longitude")

        corners = self.values[:, row : row + 2, col : col + 2]
        weights = np.array(
            [
                [(1 - row_weight) * (1 - col_weight), (1 - row_weight) * col_weight],
                [row_weight * (1 - col_weight), row_weight * col_weight],
            ]
        )
        return (corners * weights).sum(axis=(1, 2))

    @staticmethod
    def bracket(axis: np.ndarray, value: float, name: str) -> tuple[int, float]:
        """Index of the lower node, and how far between it and the next the value sits.

        Public because it has a second caller. `drift.CurrentSeries._sample` interpolates two
        Grids at once - u and v - so it cannot go through `column_at`, which reads one; it was
        reaching into `_bracket` under its private name, where a change here would not have
        known it had two callers. Raising it to the interface is the honest fix, and it is a
        seam: it decides where a position lands on the axes, which is a question both callers
        must answer identically or a current and a temperature would be read at different
        places.
        """
        if not axis[0] <= value <= axis[-1]:
            raise ValueError(
                f"{name} {value} is outside the grid ({axis[0]} to {axis[-1]})"
            )
        lower = int(np.clip(np.searchsorted(axis, value, side="right") - 1, 0, len(axis) - 2))
        return lower, float((value - axis[lower]) / (axis[lower + 1] - axis[lower]))


@dataclass(frozen=True)
class Surface:
    """One Field at one Timestep that has no depth: values indexed [lat, lon].

    Seven Fields are not a body of water. Five are a depth or a column total the platform
    computes from the analysis, and two more came with the biology round. `bake.py` writes them
    as float32 on these same axes rather than as a quantised Volume, for the reason the
    `FieldSpec.render` note gives: a reader reads metres off a depth sheet and kJ/cm2 off a
    drape, and byte-quantising them would put a rendering artefact where a measurement should
    be.

    Deliberately not a `Grid` with one Level. The difference is load-bearing in two places that
    are outside this repository: CF would serve a one-element depth axis, which says the value
    varies with depth, and WMS would advertise an elevation dimension a client can ask along.
    For Depth of 26 degC, whose value *is* a depth, that is wrong twice. Absent the type, the
    mistake is invisible - a one-Level Grid is well-formed and every client accepts it.
    """

    latitudes: np.ndarray
    longitudes: np.ndarray
    values: np.ndarray

    def __post_init__(self) -> None:
        expected = (len(self.latitudes), len(self.longitudes))
        if self.values.shape != expected:
            raise ValueError(f"values shape {self.values.shape} does not match axes {expected}")
