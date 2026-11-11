# Space Weather Impact Observatory handbook

By Jason Stys.

Inspect frozen observations and forecast revisions, compare lead/window coverage and export reviews with 1.1 portable applications.

Makes a complete offline review of sparse evidence practical while preserving missingness, issuance eligibility and the identity of the downloaded source/runtime.

## Read the documentation

The [illustrated Windows guide](reports/windows-application-guide.docx) adds actual
installed-app screenshots, a worked scenario, source excerpts and dated acceptance.
Its [review manifest](reports/windows-application-guide.json) identifies the exact
reviewed bytes. Earlier Office editions below retain their historical baselines.

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [RELEASE](RELEASE.md)
- [USER GUIDE](USER_GUIDE.md)

### Design and contracts

- [API](API.md)
- [ARCHITECTURE](ARCHITECTURE.md)
- [MODEL](MODEL.md)

### Security and validation

- [VALIDATION](VALIDATION.md)

## Historical results and reproduction

The reviewed source is [`5f2363643ca7fe7ce624550dcd45e0ae4cb0185a`](https://github.com/JasonStys/space-weather-impact-observatory/tree/5f2363643ca7fe7ce624550dcd45e0ae4cb0185a). The observed functional workflow baseline is `5f2363643ca7fe7ce624550dcd45e0ae4cb0185a`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/PORTABLE_RELEASE_20261109.md)
- [Current Actions](https://github.com/JasonStys/space-weather-impact-observatory/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Frozen public and synthetic snapshots do not provide current conditions, causal mission-impact prediction or operational guidance.
- Lead cutoffs overlap and fixed-half comparisons are descriptive; they are not independent samples or statistical significance tests.
- Unsigned desktop portable packages; no system installer, hosted account service or native mobile installation.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
