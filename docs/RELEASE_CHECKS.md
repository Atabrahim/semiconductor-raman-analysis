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

Verified CI checkpoint: [run 35518094851](https://github.com/Atabrahim/semiconductor-raman-analysis/actions/runs/35518094851),
commit `c25d388cb0f3926fb5a5751d040594b5b4b0a409`, the verified `v0.1.0` tag target.
All four jobs passed. The later completion-record commit changes documentation
only and remains subject to the same CI workflow.

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

Publication verified: [v0.1.0](https://github.com/Atabrahim/semiconductor-raman-analysis/releases/tag/v0.1.0)
was published after the final implementation commit passed CI. The tag target
matches `c25d388cb0f3926fb5a5751d040594b5b4b0a409`. The original tested assets
were preserved in the GitHub draft and published without replacement:

- Wheel SHA-256: `bc3bb0b9fc4391d74f65777c9bebe3dc1775515843c7401409db320ad5cb7a3a`
- Source distribution SHA-256: `6f0b3079b7635ebea7e538c6be556464b28c44b412f84d17b73669390278d27d`
- Checksum file SHA-256: `09cda26655e34f0766be092ff92e67bb23327792a5a6015fcc0f046e0891cfd9`

No release task remains.
