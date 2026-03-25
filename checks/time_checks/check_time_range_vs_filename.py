#!/usr/bin/env python

import os
import re
from compliance_checker.base import BaseCheck, TestCtx
from netCDF4 import num2date


_TIME_RANGE_RE = re.compile(r"^(?P<start>\d{6}|\d{8})-(?P<end>\d{6}|\d{8})$")


def _extract_time_range_from_filename(filename: str):
    """
    Extract time range token from filename.
    Works for CMIP6 and CMIP7:
      ..._YYYYMM-YYYYMM.nc
      ..._YYYYMMDD-YYYYMMDD.nc
    Returns (start_str, end_str, use_day) or (None, None, None) if not found.
    """
    stem = filename[:-3] if filename.endswith(".nc") else filename
    last_token = stem.split("_")[-1]
    m = _TIME_RANGE_RE.match(last_token)
    if not m:
        return None, None, None

    start_str = m.group("start")
    end_str = m.group("end")
    use_day = (len(start_str) == 8)
    return start_str, end_str, use_day


def _tuple_from_datestr(s: str):
    """YYYYMM or YYYYMMDD -> tuple comparable."""
    if len(s) == 8:
        return (int(s[:4]), int(s[4:6]), int(s[6:8]))
    if len(s) == 6:
        return (int(s[:4]), int(s[4:6]))
    raise ValueError(f"Unrecognized time range token: {s}")


def _coverage_from_time(ds):
    """
    Prefer bounds if available:
      time:bounds="time_bnds" and time_bnds(time, bnds)
    Returns (start_tuple, end_tuple, use_day) where use_day indicates day precision.
    """
    if "time" not in ds.variables:
        return None, None, None, "Missing 'time' variable."

    tvar = ds.variables["time"]

    # If bounds exist, use them (more accurate than midpoints)
    bname = getattr(tvar, "bounds", None)
    if bname and bname in ds.variables:
        bvar = ds.variables[bname]
        try:
            units = tvar.units
            calendar = getattr(tvar, "calendar", "standard")

            bvals = bvar[:]
            # expected shape (n,2)
            start_val = bvals[0, 0]
            end_val = bvals[-1, 1]

            start_dt = num2date(start_val, units=units, calendar=calendar)
            end_dt = num2date(end_val, units=units, calendar=calendar)

            return (start_dt.year, start_dt.month, start_dt.day), (end_dt.year, end_dt.month, end_dt.day), True, None
        except Exception as e:
            # fallback to time points if bounds conversion fails
            pass

    # Fallback: use time points
    try:
        tvals = tvar[:]
        if hasattr(tvals, "compressed"):
            tvals = tvals.compressed()
        if tvals.size == 0:
            return None, None, None, "The 'time' variable is empty."

        units = tvar.units
        calendar = getattr(tvar, "calendar", "standard")
        dts = num2date(tvals, units=units, calendar=calendar)

        first = dts[0]
        last = dts[-1]
        # points are often monthly midpoints; we compare month precision by default
        return (first.year, first.month), (last.year, last.month), False, None
    except Exception as e:
        return None, None, None, f"Error converting time values: {e}"


def check_time_range_vs_filename(ds, severity=BaseCheck.MEDIUM):
    """
    [TIME003] Check that the dataset time axis covers the time range declared in the filename.
    """
    check_id = "TIME003"
    ctx = TestCtx(severity, f"[{check_id}] Check Time Range vs Filename")

    filename = os.path.basename(ds.filepath())
    start_str, end_str, use_day_from_name = _extract_time_range_from_filename(filename)

    if not start_str or not end_str:
        ctx.add_failure("No time range token found in filename; skipping VAR009.")
        return [ctx.to_result()]

    try:
        expected_start = _tuple_from_datestr(start_str)
        expected_end = _tuple_from_datestr(end_str)
    except Exception as e:
        ctx.add_failure(f"Error parsing time range from filename: {e}")
        return [ctx.to_result()]

    cov_start, cov_end, cov_use_day, err = _coverage_from_time(ds)
    if err:
        ctx.add_failure(err)
        return [ctx.to_result()]

    # Compare at month precision if filename is YYYYMM-YYYYMM
    if not use_day_from_name:
        # normalize coverage to (Y,M)
        cov_start = (cov_start[0], cov_start[1])
        cov_end = (cov_end[0], cov_end[1])

    # Fail if dataset starts after expected start OR ends before expected end
    if cov_start > expected_start or cov_end < expected_end:
        ctx.add_failure(
            f"Time coverage [{cov_start} - {cov_end}] does not fully cover filename range [{start_str} - {end_str}]."
        )
    else:
        ctx.add_pass()

    return [ctx.to_result()]