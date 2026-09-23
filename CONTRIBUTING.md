# Contributing

Small reproducible contract changes are especially useful. Include a sanitized baseline,
candidate, and known old-valid/new-invalid input. Never upload API keys, personal data,
private customer arguments, or proprietary schemas without permission.

1. Create a branch and install with `python -m pip install -e .`.
2. Reproduce the issue using an example or regression test.
3. Run `python -m unittest discover -s tests -v` and `python examples/demo.py`.
4. Explain the observed behavior, change, and limitations in a pull request.

Every emitted input witness must validate against OLD and fail against NEW using
Draft 2020-12 semantics. A missed witness may return review; it must never become a
false promise of compatibility. Provider-specific runtime rules require a separate,
explicitly named check rather than silent changes to JSON Schema semantics.

Useful first contributions: a new minimized fixture, clearer errors for recursive
schemas, improved array/union generation, or verified instructions for another OS.
Please discuss larger protocol integrations before implementation.

Use respectful, technical discussion. Review focuses on evidence and reproducible behavior.
Contributions use the MIT license. No contributor-count or activity-padding campaigns.
