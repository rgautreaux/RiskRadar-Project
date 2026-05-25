Parity Checklist — Web & Mobile Parity / CI Contract Tests
=========================================================

Purpose:
- Short enforceable checklist and CI template for parity/contract testing so integrated features are verified on both web and mobile before rollout.

Checklist (run on every PR that touches backend APIs or platform adapters):
- **Contract Spec Updated**: The OpenAPI/Pydantic contract for changed endpoints is updated and committed.
- **Parity Matrix Updated**: Add mapping entry in `docs/PARITY_MATRIX.md` for any new/changed endpoint.
- **Contract Tests Run**: Run contract tests for both web and mobile expectations (shape, required fields, status codes).
- **Integration Smoke Tests**: Run end-to-end smoke tests for affected user flows on both platforms (trip → events → itinerary → share).
- **Accessibility Snapshot**: Verify UI responses include accessibility metadata where applicable (labels, alt-text, ARIA in responses when required).
- **Feature Flag Check**: New features are behind feature flags and flags default to off in production.
- **Performance Gate**: Critical endpoints have a p95 latency benchmark and are measured in CI (mocked/stubbed providers acceptable).
- **Security Gate**: CORS, auth, rate-limit headers verified for exposed endpoints.

Quick CI snippet (GitHub Actions-like pseudocode):

1. Run unit and contract tests
   - `pytest tests/contract_tests -q`  # contract tests validate schema parity

2. Run parity matrix validation
   - `python tools/validate_parity_matrix.py --matrix docs/PARITY_MATRIX.md`

3. Run platform adapters
   - `pytest tests/parity_platform_tests -q`  # runs both web and mobile adapter expectations

4. Gate on results
   - If any test fails, mark PR blocked and require fixes before merge.

Notes:
- Keep contract tests fast and focused (schema/required fields) so they can run on each PR.
- Larger end-to-end parity tests can run in nightly pipelines if they are expensive.
