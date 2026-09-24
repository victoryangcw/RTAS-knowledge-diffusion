# Scientometrics Springer submission format

This directory is an **alternate submission-format layer**. It does not replace the content-first working master.

## What changed

- `main.tex` uses Springer Nature `sn-jnl` with `sn-apa` author-year references.
- The supplement is split into standalone `ESM_1.tex`.
- Existing scientific results/statistics are frozen; only template/formatting changes were made.
- The author name and correspondence e-mail remain placeholders by design.
- ORCID to add at submission: `0009-0006-9788-3365`.
- The 115-check numerical-provenance statement remains concise in Methods; the full ledger stays in the repository.
- The AI-use disclosure is placed in Methods, following current Scientometrics guidance.
- The build script copies the tracked vector-PDF figures to flat `Fig*.pdf` names before compilation.

## Reference system

The previous `biblatex`/Biber wrapper is not used here. `sn-apa` selects Springer's APA-based BibTeX route, while the manuscript retains its existing natbib-compatible `\\citet`, `\\citep`, and `\\citealp` commands.

## Template provenance

`sn-jnl.cls` and `sn-apacite.bst` in this branch are included so CI can compile the migrated source. Before the actual journal upload, replace them with the then-current files from Springer Nature's official LaTeX author-support package.

## Submission upload layout

Springer Nature advises avoiding subdirectories in the LaTeX upload. The final upload ZIP should therefore contain `main.tex`, `references_FINAL.bib`, `sn-jnl.cls`, `sn-apacite.bst`, and `Fig1.pdf`–`Fig7.pdf` in one directory. Upload the compiled `ESM_1.pdf` separately as Online Resource 1.

## Still TODO

- final author spelling/order
- active corresponding-author e-mail
- Funding
- actual Ethics/IRB determination
- Author contributions
- final ORCID display/linkage
