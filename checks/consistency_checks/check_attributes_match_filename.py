#!/usr/bin/env python

import os

from compliance_checker.base import TestCtx

from checks.utils import _parse_filename_components

# CMIP6: time_range exists in filename, not a GA => parse but don't compare
_FILENAME_KEYS_CMIP6_PARSE = [
    "variable_id",
    "table_id",
    "source_id",
    "experiment_id",
    "variant_label",
    "grid_label",
    "time_range",
]
_FILENAME_KEYS_CMIP6_COMPARE = [
    "variable_id",
    "table_id",
    "source_id",
    "experiment_id",
    "variant_label",
    "grid_label",
]

# CMIP7: time_range exists in filename, not a GA => parse but don't compare
_FILENAME_KEYS_CMIP7_PARSE = [
    "variable_id",
    "branding_suffix",
    "frequency",
    "region",
    "grid_label",
    "source_id",
    "experiment_id",
    "variant_label",
    "time_range",
]
_FILENAME_KEYS_CMIP7_COMPARE = [
    "variable_id",
    "branding_suffix",
    "frequency",
    "region",
    "grid_label",
    "source_id",
    "experiment_id",
    "variant_label",
]

# CORDEX-CMIP6: time_range exists in filename, not a GA => parse but don't compare
_FILENAME_KEYS_CORDEX_CMIP6_PARSE = [
    "variable_id",
    "domain_id",
    "driving_source_id",
    "driving_experiment_id",
    "driving_variant_label",
    "institution_id",
    "source_id",
    "version_realization",
    "frequency",
    "time_range",
]
_FILENAME_KEYS_CORDEX_CMIP6_COMPARE = [
    "variable_id",
    "domain_id",
    "driving_source_id",
    "driving_experiment_id",
    "driving_variant_label",
    "institution_id",
    "source_id",
    "version_realization",
    "frequency",
]


def _parse_cmip7_filename(filename: str):
    """
    CMIP7 filename (doc v1.0):
      <variable_id>_<branding_suffix>_<frequency>_<region>_<grid_label>_<source_id>_<experiment_id>_<variant_label>[_<timeRangeDD>].nc
    """
    stem = filename[:-3] if filename.endswith(".nc") else filename
    parts = stem.split("_")
    if len(parts) not in (8, 9):
        return None
    return {
        "variable_id": parts[0],
        "branding_suffix": parts[1],
        "frequency": parts[2],
        "region": parts[3],
        "grid_label": parts[4],
        "source_id": parts[5],
        "experiment_id": parts[6],
        "variant_label": parts[7],
        "time_range": parts[8] if len(parts) == 9 else None,
    }


def _parse_cordex_cmip6_filename(filename: str):
    """
    CORDEX-CMIP6 filename (Archive Specifications v2):
      <variable_id><domain_id><driving_source_id><driving_experiment_id><driving_variant_label><institution_id><source_id><version_realization><frequency>
    """
    stem = filename[:-3] if filename.endswith(".nc") else filename
    parts = stem.split("_")
    if len(parts) not in (9, 10):
        return None
    return {
        "variable_id": parts[0],
        "domain_id": parts[1],
        "driving_source_id": parts[2],
        "driving_experiment_id": parts[3],
        "driving_variant_label": parts[4],
        "institution_id": parts[5],
        "source_id": parts[6],
        "version_realization": parts[7],
        "frequency": parts[8],
        "time_range": parts[9] if len(parts) == 10 else None,
    }


def _unwrap_facets(maybe_tuple):
    """
    In this repo, checks.utils._parse_filename_components may return:
      - dict
      - None
      - (dict, extra)  <-- this is what broke CMIP6
    We only need the dict.
    """
    if (
        isinstance(maybe_tuple, tuple)
        and len(maybe_tuple) > 0
        and isinstance(maybe_tuple[0], dict)
    ):
        return maybe_tuple[0]
    return maybe_tuple


def check_filename_vs_global_attrs(
    ds, severity, project_id="cmip6", filename_template_keys=None
):
    """
    [ATTR005] Consistency: Filename vs Global Attributes

    Important:
    - time_range is NOT a global attribute in CMIP6 or CMIP7.
      It's parsed from filename but not compared here.
      (Your VAR009 handles time-range vs data.)
    """
    fixed_check_id = "ATTR005"
    description = f"[{fixed_check_id}] Consistency: Filename vs Global Attributes"
    ctx = TestCtx(severity, description)

    filepath = ds.filepath()
    if not isinstance(filepath, str):
        ctx.add_failure("File path could not be determined.")
        return [ctx.to_result()]

    filename = os.path.basename(filepath)

    # ---------------- CMIP7 branch ----------------
    if project_id == "cmip7":
        facets = _parse_cmip7_filename(filename)
        if facets is None:
            ctx.add_failure(
                f"Could not perform check. Reason: Filename '{filename}' does not match expected CMIP7 token count (8 or 9 with time_range)."
            )
            return [ctx.to_result()]
        compare_keys = _FILENAME_KEYS_CMIP7_COMPARE
    # ---------------- CORDEX-CMIP6 branch ----------------
    elif project_id == "cordex-cmip6":
        facets = _parse_cordex_cmip6_filename(filename)
        if facets is None:
            ctx.add_failure(
                f"Could not perform check. Reason: Filename '{filename}' does not match expected CORDEX-CMIP6 token count (9 or 10 with time_range)."
            )
            return [ctx.to_result()]
        compare_keys = _FILENAME_KEYS_CORDEX_CMIP6_COMPARE
    # ---------------- CMIP6 (default) branch ----------------
    elif project_id == "cmip6":
        parse_keys = filename_template_keys or _FILENAME_KEYS_CMIP6_PARSE
        facets = _parse_filename_components(filename, parse_keys)
        facets = _unwrap_facets(facets)  # <-- FIX: tuple -> dict

        if facets is None:
            ctx.add_failure(
                f"Could not perform check. Reason: Filename '{filename}' does not have the expected {len(parse_keys)} components (or {len(parse_keys)-1} for time invariant variables)."
            )
            return [ctx.to_result()]
        compare_keys = _FILENAME_KEYS_CMIP6_COMPARE
    else:
        ctx.add_failure(
            f"Could not perform check. Reason: Unknown project '{project_id}'."
        )
        return [ctx.to_result()]

    # ---------------- Compare tokens to global attributes ----------------
    failures = []
    for key in compare_keys:
        if key in ds.ncattrs():
            attr_value = str(ds.getncattr(key))
            file_value = str(facets.get(key))
            if file_value != attr_value:
                failures.append(
                    f"Filename component '{key}' ('{file_value}') does not match global attribute ('{attr_value}')."
                )
        else:
            ctx.messages.append(
                f"Global attribute '{key}' not found, skipping comparison."
            )

    for f in failures:
        ctx.add_failure(f)

    if not failures:
        ctx.add_pass()

    return [ctx.to_result()]
