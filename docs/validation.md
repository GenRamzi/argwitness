# Initial validation record

Date: 2026-09-23. Scope: local alpha implementation. This record does not claim
remote GitHub CI success, registry publication, live server verification, or adoption.

## Environment actually exercised

- Linux, Python 3.12.14.
- jsonschema 4.26.0; referencing 0.37.0.
- setuptools 84.0.0; build 1.6.1.

## Results

| Check | Observed result |
| --- | --- |
| Source unit and subprocess CLI tests | 54 passed |
| Soundness fixture matrix within the test suite | 144 schema pairs; every emitted witness independently revalidated |
| `python -m build --no-isolation` | Source distribution and wheel built successfully |
| Install built wheel, replacing editable install | Succeeded |
| Confirm import location | Loaded from installed site-packages, not source checkout |
| Run all 54 tests against installed package | Passed |
| Run `python examples/demo.py` against installed package | All three assertions passed |
| Registry lookup for `argwitness` | No matching distribution returned at check time; name not reserved |

The demo found a generated breaking `search_docs` argument, marked the first of
two synthetic captured calls invalid and the second valid, and independently
confirmed the saved witness. Unit tests cover required fields, enums, scalar bounds,
arrays, nesting, local refs, metadata review, strict JSON, pagination rejection,
privacy defaults, output escaping, and CLI exit statuses.

The CI file declares Python 3.10, 3.12, and 3.13 jobs. Only Python 3.12 was actually
run locally. Windows/macOS, live providers, adversarial resource exhaustion, and
external user workloads remain unverified. Fixtures are synthetic, not a comparative
benchmark or certification.

## Reproduce

```bash
python -m pip install .
python -m unittest discover -s tests -v
python examples/demo.py
python -m pip install build
python -m build
```
