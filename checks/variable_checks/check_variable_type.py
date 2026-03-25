#!/usr/bin/env python

from compliance_checker.base import BaseCheck, TestCtx


def check_variable_type(ds, variable_name, allowed_types=None, severity=BaseCheck.HIGH):
    check_id = "VAR005"
    ctx = TestCtx(severity, f"[{check_id}] Variable Type Check: '{variable_name}'")

    if variable_name not in ds.variables:
        return []

    var = ds.variables[variable_name]
    if allowed_types is None:
        allowed_types = ["f"]

    try:
        dtype_kind = var.dtype.kind
    except AttributeError:
        ctx.add_failure(f"Could not determine dtype for variable '{variable_name}'.")
        return [ctx.to_result()]

    if dtype_kind in allowed_types:
        ctx.add_pass()
    else:
        ctx.add_failure(
            f"Variable '{variable_name}' has type '{dtype_kind}' (expected one of {allowed_types}). "
            f"Full dtype: {var.dtype}"
        )
    return [ctx.to_result()]
