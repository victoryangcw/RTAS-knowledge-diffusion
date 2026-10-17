# Analysis-code notes

This directory preserves the numbered analysis and audit scripts used during the RTAS study.

## Public-repository scope

The public repository intentionally does **not** contain the private project registry, advisor-identifying linkage tables, the full OpenAlex retrieval tables, or embedding arrays. Consequently, this directory is a provenance and reproducibility record, but it is not a turnkey end-to-end package from the public checkout alone.

Some historical scripts require authorized private inputs. Machine-specific absolute paths are not part of the public snapshot; scripts that need local data should use documented environment variables or a private local configuration.

`22_exclude_2022_sensitivity.py` supports the `RTAS_DATA_HOME` environment variable. `20_raw_registry_audit.py` uses `RTAS_RAW_DIR`, `RTAS_FROZEN_DATA`, and optionally `RTAS_AUDIT_OUT_DIR`. Never commit the values of these variables or the data they point to.

## Suggested local layout

For an authorized rerun, restore the private inputs outside Git and preserve the expected study layout, for example:

```text
<RTAS_DATA_HOME>/
├── 01_DATA/                 # private frozen inputs
├── 03_FINAL_ANALYSIS/       # regenerated/intermediate analysis outputs
└── ...
```

Public validation files use `PAIR_###` and `ARTICLE_###` placeholders and retain pairwise scores without distributing the original title mapping. Text-dependent validation, lexical-baseline, and encoder reruns require authorized access to the private title-pair source. Never commit raw project records, advisor names, private linkage tables, API keys, or other personally identifying information.

## Figure regeneration

`10_generate_figures.py` regenerates the engineering figure set from frozen analysis CSVs. The public checkout alone does not contain all of those input CSVs, so figure regeneration requires authorized access to the private frozen-output store.

## Current numerical reference

For post-audit headline values, use:

- `../06_RESULTS/19_numerical_provenance_ledger.csv`
- `../manuscript/data_verification.tex`
- the root `README.md`

The historical v0.2 protocol/config files in `../01_README/` are retained for provenance and include superseded development-stage values.
