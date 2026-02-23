# Checks Overview

cc_plugin-wcrp is built from many **atomic checks**, grouped by category. Eah plugin (e.g., `wcrp_cmip6`, `wcrp_cordex_cmip6`) just decides which ones to run; each category focuses on a specific aspect of file quality.

---

## 📏 Dimension Checks
Ensure that all **dimensions** exist and match the variable shapes.  
These checks confirm that:
- Dimensions (e.g. `time`, `lat`, `lon`, `bnds`) are present.
- Their sizes are **positive** and coherent with variable shapes.
- Bounds variables (e.g. `time_bnds`) are consistent in size and order.

## 📊 Variable Checks
Ensure variables are present, their shape matches their dimensions, and (when bounds are declared) each value lies **within its bounds**.

##  ⏱️ Time Checks
Focus on the `time` axis: presence of bounds with the right shape, and consistency between the time axis and the filename’s time range.

## 🏷️ Attribute Checks
Check that mandatory global and variable attributes are there, correctly typed/encoded, and their values are valid against regex patterns or controlled vocabularies.

## 📁 DRS & Path Consistency Checks
Validate filenames and directory paths and compare with the netcdf file's attributes; verify consistency between attributes like **frequency vs table_id**, `experiment_id`, `institution`, `variant_label`, etc., against project rules/CVs.

## 🧬 Data Plausibility Checks
Perform **data-level plausibility tests** on numeric variables:

- Check NaN and infinite .  
- Check Constant .  
- Check Fill Value or Missing values filling.  
- Detect Physically impossible or statistically extreme outliers.  
- Check Chunk size.

## 📦 File Format & Compression Checks
These checks ensure that the **NetCDF file format** and **compression options** comply with project and ESGF recommendations.

## Detailed Inventory
For the full list of checks (IDs, description) :

| Category   | Check                                                                                | Check_id |
| ---------- | ------------------------------------------------------------------------------------ | -------- |
| File       | Validate filename pattern and tokens against CV                                      | FILE001  |
| File       | Check file format                                                                    | FILE002  |
| File       | Check compression file settings                                                      | FILE003  |
| Attributes | Check the existence of an attribute                                                  | ATTR001  |
| Attributes | Check the type on an attribute                                                       | ATTR002  |
| Attributes | Check encoding (e.g., UTF-8) of an  attribute                                        | ATTR003  |
| Attributes | Check the value of an attribute against CV or another constraint                     | ATTR004  |
| Attributes | Check the constitency of filename tokens with global attributes                      | ATTR005  |
| Attributes | Check the consistency of attributes related to variant/member                        | ATTR006  |
| Attributes | Check the consistency of attributes related to experiment details                    | ATTR007  |
| Attributes | Check the consistency between table_id and frequency attributes                      | ATTR008  |
| Attributes | Check the consistency of attributes related to institution details                   | ATTR009  |
| Attributes | Check the consistency of attributes related to source details                        | ATTR010  |
| Variables  | Dimensions count vs Variable Registry                                                | VAR000   |
| Variables  | Check the existence of variable                                                      | VAR001   |
| Variables  | Check the shape aligns with corresponding dimension                                  | VAR002   |
| Variables  | Check the consistency of time axis coverage with time range from filename            | VAR003   |
| Variables  | Ensure each value lies within the range specified by corresponding boundary variable | VAR004   |
| Variables  | Check the type of the variable                                                       | VAR005   |
| Dimensions | Check the existence of dimension                                                     | DIM001   |
| Dimensions | Check the value is a positive integer                                                | DIM002   |
| Dimensions | Check dimension size                                                                 | DIM003   |
| Directory  | Check consistency of directory structure tokens with global attributes               | PATH001  |
| Directory  | Check consistency of directory structure tokens with filename tokens                 | PATH002  |
| Directory  | alidate directory structure tokens and pattern against CV                            | PATH003  |
| Data       | Check for NaN/Inf values in variable                                                 | DATA001  |
| Data       | FillValue/MissingValue plausibility for variable                                     | DATA002  |
| Data       | Constant field detection for variable                                                | DATA003  |
| Data       | Check pysically impossible outlier                                                   | DATA004  |
| Data       | Check spatial statistical outliers                                                   | DATA005  |
| Data       | Chunk size Check                                                                     | DATA006  |


