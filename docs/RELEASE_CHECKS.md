# Release verification

Status: final checks pending. The existence of this file does not certify a release.

Verified development checkpoint: 61 tests passed; Ruff lint/format checks passed;
complete measured/synthetic reproduction executed. Raw and measured-fit figures
visually inspected. Sensitivity plot labels corrected; final visual inspection
will be recorded before release.

Remaining: build wheel/sdist, install the wheel in a clean environment, run the
full suite and README/API/CLI/reproduction commands using that installation,
verify GitHub Actions on the published commit, inspect final repository presentation,
and publish/verify v0.1.0 only after all essential checks pass.
