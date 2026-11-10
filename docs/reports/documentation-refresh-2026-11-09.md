# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `5f2363643ca7fe7ce624550dcd45e0ae4cb0185a`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 79437 | `e0c377863d636891e73c67d4d0dd5d266f5199de4fe1406c33dbbfcf2c1878c8` | 4 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     | 43606 | `9e79997a55775aeec5c29a38aecbd2d9ac4b3e9bcd81a1781e013c97e6abfde4` | 4 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7379 | `e0fdad9dda982002f800f3eb79454feae59cacc5681f990d2abb00c86e4c2549` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `5f2363643ca7fe7ce624550dcd45e0ae4cb0185a`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Local integration validation

The complete Python suite passed 361 tests at 99.68% combined statement/branch
package coverage, retaining the original 90% floor. Eight real Office ZIP regressions
are included: only the named edition paths are decoded with bounded bytes/members
and strict UTF-8 XML/relationships; text remains visible to the original privacy
scan. Malformed/unknown/oversized archives fail. Package and CLI imports are explicit.

Ruff, exact generated source/file maps, 12 TypeScript unit tests and strict
TypeScript/Vite production build passed. Existing warning policy and hosted
cross-platform/browser/security gates remain. Exact approved Office/hash/ZIP/source
and local-link validation are separate from the dated functional observations;
this integration does not assert future PR/main, new installation or release results.
