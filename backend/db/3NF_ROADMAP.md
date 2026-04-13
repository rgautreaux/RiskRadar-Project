# 3NF Roadmap (Expand-Migrate-Contract)

This roadmap defines a low-risk normalization path while preserving current API behavior.

## Goals

- Eliminate JSON-array relationship storage where relational joins are appropriate.
- Preserve backward compatibility during transition.
- Use phased dual-write and parity checks before cutover.

## Principles

- Expand first: add new tables and write paths without removing old columns.
- Migrate safely: backfill in batches with checkpoints and retries.
- Contract last: switch reads, freeze legacy writes, then retire columns only after validation.

## Phase A: Summaries to Alerts Junction

Current:

- `summaries.alert_ids` stores JSON list of alert IDs.

Target:

- New table `summary_alerts(summary_id, alert_id, created_at)` with unique composite key.

Steps:

1. Create `summary_alerts` table with indexes on `(summary_id)` and `(alert_id)`.
2. Update summary generation code to dual-write:
   - keep writing `summaries.alert_ids`
   - also write `summary_alerts` rows
3. Backfill historic data from `summaries.alert_ids` in batches.
4. Add parity validator: JSON IDs vs junction rows must match.
5. Switch read path to junction table behind feature flag.
6. Freeze legacy `alert_ids` writes once parity is stable.
7. Remove `alert_ids` only after one full release cycle.

## Phase B: User Alert Preferences Normalization

Current:

- `users.alert_types` stores JSON list.

Target:

- New table `user_alert_type_preferences(user_id, alert_type, created_at)`.

Steps:

1. Create preference table with unique `(user_id, alert_type)`.
2. Dual-write from preferences update endpoints.
3. Backfill from legacy JSON arrays.
4. Add parity checks and invalid-value reporting.
5. Switch read filters to normalized table.
6. Retire legacy JSON column after stabilization window.

## Phase C: Zip/Geo Lookup Normalization

Current:

- `users.zip_code`, `users.latitude`, `users.longitude` can drift.

Target:

- Introduce `zip_geo(zip_code, latitude, longitude, state, city)` and reference where feasible.

Steps:

1. Create `zip_geo` lookup and seed with trusted source.
2. Add consistency checks between user zip and coordinates.
3. Move write path to derive coordinates from zip where possible.
4. Keep user-level overrides only if explicitly needed.

## Safety Gates Per Phase

- Preflight passes before and after migration changes.
- Backfill can resume safely (idempotent checkpoints).
- Rollback path is tested in staging.
- API contract tests pass in dual-write and switched-read modes.
- No unresolved parity mismatches.

## Suggested Rollout Pattern

1. Staging dry run with production-like snapshot.
2. Limited production rollout with monitoring.
3. Full rollout after error-free window.
4. Contract cleanup in a separate release.
