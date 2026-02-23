# WCRP Plugins

The **WCRP plugins** provide project-specific compliance checks for WCRP datasets such as **CMIP6** and **CORDEX-CMIP6**, built on top of the [IOOS Compliance Checker](https://ioos.github.io/compliance-checker/).

Each plugin has its own orchestration layer (`wcrp_project.py`), which acts as the **controller** for WCRP validation logic deciding:

- Which checks to run  
- With what severity  
- According to each project’s configuration  

---

## Available Plugins

| Plugin Name           | Checker Tag             | Description                                 |
| --------------------- | ----------------------- | ------------------------------------------- |
| **wcrp_cmip6**        | `wcrp_cmip6:1.0`        | Validation of CMIP6 NetCDF files            |
| **wcrp_cordex_cmip6** | `wcrp_cordex_cmip6:1.0` | Validation of CORDEX-CMIP6 NetCDF files     |
| **wcrp_cmip7**        | `wcrp_cmip7:1.0`        | Validation of CMIP7 NetCDF files            |
| **wcrp_data**         | `wcrp_data:1.0`         | Data Validation of CMIP6/CMIP7 NetCDF files |



Each plugin has its own **TOML configuration file** defining specific rules, severities, and variable mappings.

---

## What Each Plugin Does

Each WCRP plugin:

**Loads its configuration file** (`wcrp_cmip6.toml` / `wcrp_cordex_cmip6.toml` / `wcrp_cmip6.toml`/ `wcrp_data.toml`), which defines:

 - Which checks to run (DRS, attributes, time, metadata, etc.)
 - The severity of each check (High = Mandatory, Medium = Recommended, Low = Warning)

**Runs the atomic checks** implemented in `checks/…`:
  
 - Examples: dimension existence/size, variable shape, time bounds, filename/DRS consistency, physical plausibility, missing values, etc.

**Aggregates results** and returns them to the Compliance Checker core,  
   which formats them into human-readable or machine-readable outputs (text, HTML, JSON).

---

## TOML Configuration Files

Each plugin is driven by its own TOML file:

- **`wcrp_cmip6.toml`**  / **`wcrp_cmip7.toml`** 
  Main configuration for CMIP6/CMIP7 checks, mapping variables, severities, and project rules.

- **`wcrp_cordex_cmip6.toml`**  
  Adapted version for CORDEX-CMIP6)context.

- **`wcrp_data.toml`**  
  Adapted version for Data checks.  

- **`mapping_variables.toml`**  
  Helper file mapping `<table_id>.<variable_id>` to standard variable definitions  
  (dimensions, expected attributes, cell methods, etc.).  
  This is a **temporary bridge** for CMIP6 until the official ESGVOC vocabulary exposes all required metadata.

---