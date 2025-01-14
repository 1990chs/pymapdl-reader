"""Provides a basic interface to computing the minimum scaled Jacobian
cell quality from VTK unstructured grids.
"""
import numpy as np
import pyvista as pv

from ansys.mapdl.reader.misc import vtk_cell_info


def quality(grid):
    """Compute the minimum scaled Jacobian cell quality of an UnstructuredGrid.

    Negative values indicate invalid cells while positive values
    indicate valid cells.  Varies between -1 and 1.

    Parameters
    ----------
    grid : pyvista.UnstructuredGrid or pyvista.StructuredGrid
        Structured or Unstructured Grid from ``pyvista``.

    Examples
    --------
    >>> from ansys.mapdl import reader as pymapdl_reader
    >>> import pyvista as pv
    >>> x = np.arange(-10, 10, 5)
    >>> y = np.arange(-10, 10, 5)
    >>> z = np.arange(-10, 10, 5)
    >>> x, y, z = np.meshgrid(x, y, z)
    >>> grid = pv.StructuredGrid(x, y, z)
    >>> pymapdl_reader.quality(grid)
    array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.,
           1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
    """

    # lazy load to speed up import
    from ansys.mapdl.reader._cellqual import cell_quality, cell_quality_float

    flip = False
    if isinstance(grid, pv.StructuredGrid):
        grid = grid.cast_to_unstructured_grid()
        flip = True
    elif not isinstance(grid, pv.UnstructuredGrid):
        grid = pv.wrap(grid)
        if not isinstance(grid, pv.UnstructuredGrid):
            raise TypeError("Input grid should be a pyvista or vtk UnstructuredGrid")

    celltypes = grid.celltypes
    points = grid.points
    cells, offset = vtk_cell_info(grid)
    if points.dtype == np.float64:
        qual = cell_quality(cells, offset, celltypes, points)
    elif points.dtype == np.float32:
        qual = cell_quality_float(cells, offset, celltypes, points)
    else:
        points = points.astype(np.float64)
        qual = cell_quality(cells, offset, celltypes, points)

    # set qual of null cells to 1
    qual[grid.celltypes == 0] = 1
    if flip:  # for structured grids
        return -qual
    return qual
