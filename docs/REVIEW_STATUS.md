# Verification and scope

The original v0.1.0 methods paper and publication companion are preserved as
historical documents. Their results refer to the bundled Linux reference
run. The release preparation changed the test fixture's handling of Windows
symlink privileges and the validation runner. The five runtime Python modules
and the supplied zipapp match the original candidate byte for byte.

| Evidence | Environment | Observed result |
| --- | --- | --- |
| Historical reference validation | CPython 3.13.15, Linux x86-64 | 67 tests passed, 20 authored and 64 generated matches |
| Fresh validation | CPython 3.12.10, Windows 11 AMD64 | 66 tests passed, 1 skip, 20 authored and 64 generated matches |
| Fresh standalone packaging | CPython 3.12.10, Windows 11 AMD64 | 10 checks passed, including byte-identical zipapp rebuild |

Windows raised WinError 1314 while the test attempted to create the source
symlink. The fixture now records this exact privilege case as a skip. Strict
validation returned exit 1 for that run. With the Windows-only exception
explicitly enabled, validation returned exit 0. All other skips fail validation.
Linux CI requires the real symlink test to pass.

See [historical validation](../evidence/reference-run/validation.json),
[Windows validation](../evidence/windows-validation/validation.json) and
[Windows packaging](../evidence/windows-packaging.json).

The cases use synthetic data and overlap across check families. QuoteLedger
compares records and text snapshots. Source identity, the accuracy of a review,
and whether a quotation supports a claim depend on the evidence and reviewer.
