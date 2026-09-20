# v0.1.0 release verification

Verified on 20 September 2026. Scope: one measured silicon Raman case plus
explicitly synthetic verification, uncertainty/sensitivity, API/CLI and reporting.

| Gate | Verified result |
|---|---|
| Automated suite | **62 passed, 0 failed, 0 skipped** |
| Code quality | Ruff lint and formatting pass |
| Packaging | `python -m build` produces sdist and universal Python wheel |
| Source archive | Includes raw data, provenance, examples, tests, figures and reports |
| Clean installation | Built wheel installed in a new Python 3.12 virtual environment; `pip check` passes |
| Installed API | Imported from `site-packages` outside checkout; measured fit and 200-refit bootstrap work |
| Installed CLI | Entry point and `python -m raman_analysis` work outside checkout; measured report and plot generated |
| Fresh-clone README | Clone, venv, source installation, CLI, API, reproduction, dev install, tests, Ruff and build verified |
| Reproducibility | Full 200-refit case study and synthetic batch execute; committed synthetic metrics match exactly locally; measured estimates/intervals have tolerance-based regression tests |
| Scientific figures | All three reviewed visually; axis units, legend, residual sign, captions and narrow sensitivity scales checked |
| Documentation | Relative links resolve; equations/units and distinction between measured, fitted and synthetic quantities reviewed |
| GitHub | Published source compared with local tree; preview images load; description/topics reviewed |
| CI | All four jobs pass: Linux Python 3.11, 3.12, 3.13; Windows Python 3.12 |

Verified CI checkpoint: [run 35517863663](https://github.com/Atabrahim/semiconductor-raman-analysis/actions/runs/35517863663),
commit `44515fd1ac2f237bc64befad318f813e72d486f0`. Final documentation commits are
also subject to the same workflow; the release tag must target its final passing
commit. See the GitHub Actions page and release for that publication record.

The first CI run passed on Linux but failed the Windows source-README checksum
because checkout changed line endings. `.gitattributes` now preserves both
downloaded source files byte-for-byte. The original checksum assertions remain;
the corrected Windows run passes. No test was skipped or weakened to hide this.
GitHub runners emit a non-failing Node-runtime transition notice for the official
actions; this does not affect the verified scientific/packaging checks.

Local verification environment: Python 3.12, NumPy 2.5.3, SciPy 1.18.1,
pandas 3.0.6, Matplotlib 3.11.2, pytest 9.1.1, Ruff 0.16.8. CI resolves compatible
versions separately for each supported Python. Dependencies are lower-bounded;
exact environment versions are evidence, not a promise about all future releases.

No essential software failure remains. Scientific limitations remain explicit:
correlated measured residuals, unknown calibration/instrument response, single
acquisition and no supported property inversion or spatial mapping. Passing tests
certify the stated software behaviour, not industrial metrology accuracy.

Release procedure: tag `v0.1.0` only after CI passes on the final published commit;
verify the tag target and GitHub release, and attach the corresponding sdist/wheel.
