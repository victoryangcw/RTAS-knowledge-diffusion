# Analysis-code notes

This directory preserves the numbered analysis and audit scripts used during the RTAS study.

## Public-repository scope

The public repository intentionally does **not** contain the private project registry, advisor-identifying linkage tables, the full OpenAlex retrieval tables, or embedding arrays. Consequently, this directory is a provenance and reproducibility record, but it is not a turnkey end-to-end package from the public checkout alone.

Several scripts were written against the original private Windows workspace and still contain historical absolute paths. Those paths identify the original execution environment; they do not mean the corresponding private files are present in this repository.

`22_exclude_2022_sensitivity.py` already supports the `RTAS_DATA_HOME` environment variable. Other scripts with absolute paths should be pointed to an authorized local private-data mirror before rerunning.

## Suggested local layout

For an authorized rerun, restore the private inputs outside Git and preserve the expected study layout, for example:

```text
<RTAS_DATA_HOME>/
├── 01_DATA/                 # private frozen inputs
├── 03_FINAL_ANALYSIS/       # regenerated/intermediate analysis outputs
└── ...
```

Never commit raw project records, advisor names, private linkage tables, or other personally identifying information.

## Figure regeneration

`10_generate_figures.py` regenerates the engineering figure set from frozen analysis CSVs. The public checkout alone does not contain all of those input CSVs, so figure regeneration requires authorized access to the private frozen-output store.

## Current numerical reference

For post-audit headline values, use:

- `../06_RESULTS/19_numerical_provenance_ledger.csv`
- `../manuscript/data_verification.tex`
- the root `README.md`

The historical v0.2 protocol/config files in `../01_README/` are retained for provenance and include superseded development-stage values.
