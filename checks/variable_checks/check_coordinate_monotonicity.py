#!/usr/bin/env python
"""Coordinate monotonicity check.

This is a unitary check (standalone function) and is called from the project
plugins (CMIP6/CMIP7) from their `check_Coordinates` orchestration.
"""

from __future__ import annotations

import numpy as np
from compliance_checker.base import BaseCheck, TestCtx


def check_coordinate_monotonicity(
    ds,
    coord_name: str,
    direction: str,
    severity: int = BaseCheck.MEDIUM,
):
    """Check that a 1D coordinate is strictly monotonic."""
    check_id = "VAR005"
    ctx = TestCtx(severity, f"[{check_id}] Coordinate monotonicity for '{coord_name}'")

    if coord_name not in getattr(ds, "variables", {}):
        ctx.add_failure(f"Coordinate variable '{coord_name}' is missing.")
        return [ctx.to_result()]

    var = ds.variables[coord_name]

    try:
        values = var[:]
        if hasattr(values, "compressed"):
            values = values.compressed()
        arr = np.asarray(values, dtype="float64").reshape(-1)
        arr = arr[~np.isnan(arr)]
    except Exception as e:
        ctx.add_failure(f"Error reading coordinate '{coord_name}': {e}")
        return [ctx.to_result()]

    if arr.size < 2:
        ctx.add_pass()
        return [ctx.to_result()]

    diffs = np.diff(arr)
    if direction == "increasing":
        ok = bool(np.all(diffs > 0))
    elif direction == "decreasing":
        ok = bool(np.all(diffs < 0))
    else:
        ctx.add_failure(f"Unsupported direction '{direction}'.")
        return [ctx.to_result()]

    if ok:
        ctx.add_pass()
    else:
        ctx.add_failure(f"'{coord_name}' is not strictly {direction}.")

    return [ctx.to_result()]
