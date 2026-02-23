#!/usr/bin/env python

import re
from compliance_checker.base import TestCtx


def _is_cmip7(ds) -> bool:
    """Detect CMIP7 from global attrs when available."""
    try:
        if str(ds.getncattr("mip_era")).upper() == "CMIP7":
            return True
    except Exception:
        pass
    try:
        if str(ds.getncattr("drs_specs")) == "MIP-DRS7":
            return True
    except Exception:
        pass
    return False


def _to_int_index(attr_value, prefix: str, is_cmip7: bool):
    """
    Convert index attribute to int.
    CMIP6: often "1" (or int 1)
    CMIP7: often "r1"/"i1"/"p1"/"f3" (string with prefix)
    """
    if attr_value is None:
        return None

    # Already numeric
    if isinstance(attr_value, int):
        return attr_value

    s = str(attr_value).strip()
    if not s:
        return None

    # CMIP7 prefixed form (e.g. "r1")
    if is_cmip7 and s.lower().startswith(prefix.lower()):
        s = s[len(prefix):].strip()

    # Some files may still store numeric as string
    try:
        return int(s)
    except Exception:
        return None


def check_variant_label_consistency(ds, severity):
    """
    [ATTR006] Consistency: variant_label vs index attributes

    Checks if variant_label (r<i>i<j>p<k>f<l>) is consistent with:
      realization_index, initialization_index, physics_index, forcing_index

    CMIP6 commonly stores index attributes as numeric (e.g. "1" or 1).
    CMIP7 commonly stores index attributes prefixed (e.g. "r1","i1","p1","f3").
    This check supports both.
    """
    fixed_check_id = "ATTR006"
    description = f"[{fixed_check_id}] Consistency: variant_label vs index attributes"
    ctx = TestCtx(severity, description)

    required_attrs = [
        "variant_label",
        "realization_index",
        "initialization_index",
        "physics_index",
        "forcing_index",
    ]

    try:
        attributes = {attr: ds.getncattr(attr) for attr in required_attrs}
        variant_label = str(attributes["variant_label"])

        match = re.match(r"^r(\d+)i(\d+)p(\d+)f(\d+)$", variant_label)
        if not match:
            ctx.add_failure(
                f"The format of 'variant_label' ('{variant_label}') is invalid. "
                "Expected format is 'r<k>i<l>p<m>f<n>'."
            )
            return [ctx.to_result()]

        parsed_indices = {
            "realization_index": int(match.group(1)),
            "initialization_index": int(match.group(2)),
            "physics_index": int(match.group(3)),
            "forcing_index": int(match.group(4)),
        }

        is_cmip7 = _is_cmip7(ds)

        # Normalize attribute values to ints
        normalized_attrs = {
            "realization_index": _to_int_index(attributes["realization_index"], "r", is_cmip7),
            "initialization_index": _to_int_index(attributes["initialization_index"], "i", is_cmip7),
            "physics_index": _to_int_index(attributes["physics_index"], "p", is_cmip7),
            "forcing_index": _to_int_index(attributes["forcing_index"], "f", is_cmip7),
        }

        failures = []
        for key, parsed_value in parsed_indices.items():
            attr_raw = attributes[key]
            attr_int = normalized_attrs[key]

            if attr_int is None:
                failures.append(
                    f"Could not interpret '{key}' attribute value '{attr_raw}' as an integer."
                )
                continue

            if parsed_value != attr_int:
                failures.append(
                    f"Inconsistency for '{key}': variant_label implies '{parsed_value}', but attribute is '{attr_raw}'."
                )

        if not failures:
            ctx.add_pass()
        else:
            for f in failures:
                ctx.add_failure(f)

    except AttributeError as e:
        # missing attributes should be handled elsewhere (attribute suite)
        ctx.messages.append(
            f"Missing a required attribute for this check: {e}. Check skipped."
        )
    except Exception as e:
        ctx.add_failure(f"An unexpected error occurred: {e}")

    return [ctx.to_result()]