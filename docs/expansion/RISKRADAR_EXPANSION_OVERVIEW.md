# RISKRADAR_EXPANSION_OVERVIEW.md

# Plan: RiskRadar Traveler Intelligence Expansion

**Executive Summary**

This plan delivers a production-grade expansion of RiskRadar that transforms it from an environmental alert system into a comprehensive travel intelligence platform. The expansion adds five new capability domains: Event Intelligence (festivals, attractions, tours), Traffic & Travel Tracking (smart routing with hazard awareness), Interactive Itineraries (day-level activity planning), Collaborative Trip Planning (with invited users and public links), and Cross-Platform Parity (unified Golby AI assistant on web and mobile).

The approach is designed for full production maturity, not MVP shortcuts. It prioritizes schema safety, provider abstraction, security-by-design, and explicit risk mitigation across 8 phases plus a hardening layer. It targets full capability delivery in ~10–12 weeks with parallel tracks and clear go/no-go milestones.

---

## Core Principles

1. **API-First Design**: Features delivered via stable, contract-tested REST/GraphQL endpoints, enabling web and mobile to consume the same logic without deep coupling.
2. **Schema Safety**: All data model changes follow expand-migrate-contract patterns with rollback scripts, parity validators, and preflight gating.
3. **Provider Neutrality**: Routing, LLM, and event data sources abstracted via adapters so decisions can be deferred and vendors swapped without rework.
4. **Security-by-Default**: Authorization enforced at data access layer, sharing links are signed and time-bounded, audit trails on collaboration actions.
5. **Observable Degradation**: When external providers fail, system shifts to safe fallback modes (cached routes, risk-only advisories) with clear uncertainty messaging.
6. **Explainability**: Recommendations, alerts, and itinerary suggestions include "why" and confidence fields so users understand reasoning.

---

## Phase Breakdown

### Phase 0: Program Setup and Architectural Guardrails (Week 1)

**Goals**: Lock success metrics, feature flags, API contracts, and release gates.

**Tasks**:
1. Define success metrics and SLOs (latency, availability, freshness, accessibility, cost budgets).
2. Establish feature flags for events, routing, recommendations, sharing, Golby parity with remote kill-switches.
3. Define bounded domains: Alerts, Travel, Collaboration, Assistant.
4. Lock API evolution strategy: additive changes on /api/v1; reserve /api/v2 for breaking changes.
5. Build release gate automation: preflight checks, parity validators, migration blockers, regression test gates.

**Risk Controls**: 
- Emergency feature disable paths prevent cascading failures.
- Budget caps prevent cost overruns from external APIs.

---

### Phase 1: Core Domain Model Foundation (Weeks 2–4, Critical Path)

**Goals**: Establish schema and authorization layer for all downstream features.

**Tasks**:
1. Design relational entities: Trip, TripStop, RoutePlan, RouteLeg, Event, Itinerary, ItineraryItem, PackingList, TripShare, TripCollaboratorActivity.
2. Enforce ownership and foreign keys with CASCADE semantics.
3. Preserve backward compatibility: keep legacy SavedDestination flows, dual-write to new Trip structures.
4. Write expand-migrate-contract SQL + rollback scripts.
5. Build parity validators ensuring legacy and new representations stay consistent.
6. Add indexes for: trip date windows, geospatial lookups, source dedup, collaboration paths, route joins.
7. Implement row-level authorization patterns (owner, editor, viewer).

**Key Files**:
- backend/db/models.py
- backend/db/migrations/2026-05-XX_phase1_trip_foundation.sql
- backend/db/normalization.py (extend dual-write patterns)
- backend/tests/test_trip_models.py, test_trip_authorization.py

**Verification**:
- Migration preflight passes on staging.
- Parity validators show zero divergence between old and new representations.
- 50+ unit tests for model relationships and authorization.

**Risk Controls**:
- All migrations are reversible and tested in staging first.
- Preflight gates prevent schema drift.

---

### Phase 2: Event Intelligence Scraper Platform (Weeks 5–7, Parallel with Phase 1 end)

**Goals**: Ingest and expose events data from curated sources.

**Tasks**:
1. Build EventScraper base class extending BaseScraper.
2. Add YAML config templates for event sources (Eventbrite, Meetup, Festivals API, web extraction fallback).
3. Implement event normalization: schema validation, category mapping (festival, attraction, tour, sports, cultural), confidence scoring.
4. Build deduplication: (source, source_id) constraint + fuzzy matching for near-duplicates.
5. Add quality controls: stale-event pruning (>6mo old), anomaly detection (invalid coords/dates).
6. Implement per-trip event query APIs with filtering by date/location and ranking by user interest.
7. Build event scraper integration tests with mocked responses.

**Key Files**:
- backend/db/models.py (Event, EventSourceTrust tables)
- backend/scrapers/event_scraper.py (new)
- backend/config/sources.yaml (event sources config)
- backend/api/events.py (new)
- backend/tests/test_event_scrapers.py

**Verification**:
- Event scraper normalizes test payloads without errors.
- Deduplication prevents duplicate inserts across runs.
- Trip-scoped event query returns results in user-relevance order.
- 30+ integration tests.

**Risk Controls**:
- Quality scores surface low-confidence events separately.
- Malformed records quarantine to dead-letter table for manual review.
- Rate limiting on event API calls prevents abuse.

---

### Phase 3: Traffic and Travel Tracking (Weeks 6–9)

**Goals**: Compute safe routes and overlay environmental hazards.

**Tasks**:
1. Define routing provider adapter interface (primary + fallback provider).
2. Implement provider implementations:
   - OpenRouteService (recommended as primary, free tier)
   - Google Maps (optional secondary, paid)
3. Build route computation API: origin + destination + optional waypoints → Route with legs, distance, duration.
4. Store route snapshots with provider metadata and timestamps.
5. Implement travel risk enrichment: overlay alerts and traffic incidents onto route legs.
6. Build safe-reroute engine: score alternative routes on travel time Δ, hazard severity, closure probability, confidence.
7. Add degraded mode: cache last-known-safe route + risk-only advisory when provider down.
8. Implement cost/abuse controls: request quotas, per-user limits, response caching, backoff.

**Key Files**:
- backend/db/models.py (RoutePlan, RouteLeg, RouteProviderConfig tables)
- backend/services/routing_adapter.py (new, abstract interface)
- backend/services/routing_providers/ (new, OpenRouteService + fallback impls)
- backend/api/routes.py (new)
- backend/tests/test_routing_adapter.py, test_routing_fallback.py

**Verification**:
- Route compute returns multi-leg route with hazard overlay.
- Fallback provider activates when primary times out.
- Reroute scoring favors lower-hazard alternatives.
- 40+ tests including provider outage scenarios.

**Risk Controls**:
- Provider abstraction prevents vendor lock-in.
- Circuit breaker pattern with fast fallback (< 2s).
- Cost budgets and quotas prevent runaway charges.

---

### Phase 4: Interactive Itineraries and Recommendations (Weeks 8–11)

**Goals**: Enable users to plan day-by-day activities with AI recommendations.

**Tasks**:
1. Build Itinerary CRUD: create, list, update, delete with day-level views.
2. Add ItineraryItem for activities with time, location, category, linked events/alerts.
3. Implement recommendation engine:
   - Combine risk signals (alerts), event availability, user interests, travel constraints.
   - Generate candidate activities ranked by relevance and safety.
   - Return recommendation scores with "why" explanation and confidence.
4. Add conflict detection: overlapping activities, unrealistic travel windows, high-risk times.
5. Implement itinerary health checks: proactively flag when conditions degrade.
6. Build explainability fields: recommendation reason, risk tradeoffs, data freshness, confidence.

**Key Files**:
- backend/db/models.py (Itinerary, ItineraryItem, ItineraryRecommendation tables)
- backend/api/itineraries.py (new)
- backend/services/recommendation_engine.py (new)
- backend/llm/prompts.py (extend with itinerary generation prompts)
- backend/llm/summarizer.py (add itinerary summarization)
- backend/tests/test_itinerary_crud.py, test_recommendation_engine.py, test_conflict_detection.py

**Verification**:
- Itinerary CRUD operations work end-to-end.
- Recommendation engine returns top-3 suggestions with scores and explanations.
- Conflict detection flags overlaps and impossible travel windows.
- Health checks trigger alerts when risk thresholds crossed.
- 50+ tests.

**Risk Controls**:
- Confidence scores below threshold suppress recommendations.
- Guardrails prevent unsafe suggestions (e.g., outdoor activity during critical air quality alert).

---

### Phase 5: Packing Lists and Planning Guides (Weeks 10–12)

**Goals**: Generate and manage intelligent packing recommendations tied to trips.

**Tasks**:
1. Extend existing packing guide API into persistent trip-scoped PackingList artifacts.
2. Generate category-based packing: clothing/layers, weather gear, documents, health/first aid, activity-specific.
3. Tie recommendations to itinerary activities, route conditions, and active alerts with traceable rationale.
4. Add user-editable workflows: checkboxes, item categories, assignment tags, due dates.
5. Support collaborative packing: shared lists, cross-user assignment.
6. Implement guardrails: suppress advice when data sparse, require uncertainty language, prevent unsafe suggestions.

**Key Files**:
- backend/db/models.py (PackingList, PackingItem, PackingCategory tables)
- backend/api/packing.py (extend existing endpoint)
- backend/llm/prompts.py (extend TRIP_PACKING_* prompts with category guidance)
- backend/tests/test_packing_generation.py, test_packing_guardrails.py

**Verification**:
- Packing lists generate with all 4 categories populated.
- Items are traceable to underlying alerts/activities.
- Collaborative edits merge without conflicts.
- Guardrails suppress low-confidence advice.
- 30+ tests.

**Risk Controls**:
- Medical/safety recommendations reviewed by guardrail layer before surfacing.
- Rationale fields prevent "black box" recommendations.

---

### Phase 6: Trip Sharing and Collaboration (Weeks 9–13)

**Goals**: Enable users to share trips with friends/family with fine-grained access control.

**Tasks**:
1. Implement collaboration model:
   - Owner: full control, delete trip, manage shares.
   - Editor: modify itinerary, packing, route; cannot delete or share.
   - Viewer: read-only access.
2. Add share mechanisms:
   - Account-based invite: owner → recipient email, auto-accept on recipient login.
   - Public link: short-lived signed token, expiry (default 7 days), revocation, brute-force detection.
3. Enforce row-level authorization: all trip/itinerary/packing/route endpoints check user role.
4. Add optimistic concurrency: versioned updates, conflict detection, server-side merge policy.
5. Build activity feed: track changes (edited by, timestamp, field delta).
6. Implement audit logging: all access and modifications logged.

**Key Files**:
- backend/db/models.py (TripShare, TripCollaboratorActivity, AccessAuditLog tables)
- backend/auth/permissions.py (new, role-based authorization checks)
- backend/api/trips.py (add share endpoints)
- backend/tests/test_trip_sharing.py, test_collaboration_conflicts.py, test_authorization.py

**Verification**:
- Invite flow creates share record; recipient gains access after login.
- Public link works for unauthenticated access; expires at T+7d.
- Concurrent edits resolve without data loss.
- Authorization checks block unauthorized access (403).
- Audit log records all actions.
- 50+ tests including edge cases (expired link, concurrent conflict).

**Risk Controls**:
- Share links are signed opaque tokens (not incrementing IDs).
- Brute-force detection blocks >10 failed attempts per link per IP per hour.
- Explicit consent required to share trip; recipient sees who shared it.

---

### Phase 7: Web-App Integration and Cross-Platform Feature Parity (Weeks 11–14)

**Goals**: Integrate external web app and ensure web/mobile feature equivalence.

**Tasks**:
1. Audit compatibility between current RiskRadar APIs and external web-app contract expectations.
2. Publish parity matrix: required endpoints, request/response schemas, expected behaviors.
3. Implement API parity adapter layer (map web-app calls to stable RiskRadar endpoints).
4. Integrate Golby assistant:
   - Centralize backend contracts in RiskRadar APIs.
   - Deploy identical Golby widget to both web and mobile.
   - Ensure onboarding state, guardrails, profile shaping, feedback loop consistent across platforms.
5. Build shared schemas: UserOut, TripOut, EventOut, ItineraryOut, etc., with parity tests.
6. Add platform-specific UX (responsive CSS for web, Expo Router navigation for mobile) while preserving feature equivalence.
7. Contract tests: for every new API, verify web and mobile responses match exactly (excluding presentation).

**Golby Intelligence Layer**:
- Make Golby the primary assistant surface for trip planning, itinerary building, packing guidance, event discovery, route advice, and feature navigation.
- Feed Golby with live RiskRadar context: active alerts, forecasts, event data, route plans, itinerary items, packing lists, collaboration state, and trip sharing permissions.
- Add an explicit user preference and memory model so Golby can learn the traveler’s style over time, including preferred tone, risk tolerance, packing habits, pace of travel, and repeated destinations.
- Use feedback signals to refine future answers: thumbs up/down, follow-up corrections, skipped suggestions, and saved recommendations should influence ranking and response style.
- Keep responses warm, friendly, and encouraging while staying source-grounded, safety-first, and transparent about uncertainty.
- Let Golby proactively advise the user: suggest itinerary changes when weather or alerts shift, recommend packing items before departure, explain why a route or activity is risky, and surface the next best action inside the app.
- Require Golby to cite the live context it used when available, and to fall back to clear uncertainty language when data is sparse or conflicting.

**Golby Advice Principles**:
- Lead with the safest, most useful recommendation first.
- Explain why the advice matters using live RiskRadar context.
- Separate facts, confidence, and next steps so users can act quickly.
- Adapt tone and detail to the traveler’s preferences and past feedback.
- Ask a clarifying question only when it materially improves the answer.

**Key Files**:
- backend/api/parity/ (new, API contract definitions)
- backend/api/router.py (register parity adapter routes)
- frontend/RiskRadar/utils/api.ts (extend API client for new endpoints)
- backend/templates/ (web Golby integration)
- backend/tests/test_parity_contracts.py
- docs/PARITY_MATRIX.md (new)

**Verification**:
- Parity matrix covers 100% of required features.
- Contract tests pass for all shared endpoints (web ≈ mobile response).
- Golby widget loads on both platforms and accepts input.
- Accessibility (WCAG AA) verified on web and mobile.
- 60+ parity tests.

**Risk Controls**:
- Contract tests are release blockers.
- Feature flags allow gradual rollout to 10% → 50% → 100% of users.

---

### Phase 8: Production Hardening, Security, and Operations (Weeks 1–14, Cross-Cutting)

**Goals**: Ensure production readiness across all phases.

**Tasks**:

**Security (Weeks 1–14)**:
- Implement strict CORS allowlist (specific origins, not wildcard).
- Add endpoint-level rate limiting (not just auth endpoints): 100 req/min per user for routes, 50 for recommendations.
- Add abuse detection: repeated failed authorization attempts, unusual API patterns.
- Implement token rotation: JWT refresh tokens, logout invalidation.
- Secret hygiene: rotate LLM API keys monthly, use HashiCorp Vault or equivalent.

**Data Privacy (Weeks 4–10)**:
- Minimize retention: delete collaboration audit logs after 1 year.
- Share link tokens encrypted at rest.
- Shared-view redaction: hide sensitive health conditions, device tokens from viewers.
- GDPR/CCPA compliance: user data export, deletion, opt-out audit.

**Reliability (Weeks 4–14)**:
- Implement retries with exponential backoff for external APIs.
- Circuit breaker pattern: fail open to degraded mode after 3 failures.
- Idempotency keys for mutations (prevent double-posts).
- Dead-letter handling for failed event ingestion.

**Observability (Weeks 5–14)**:
- Structured logging: JSON logs with request ID, user ID, trace ID.
- Distributed tracing: instrument scraper, recommendation engine, routing calls.
- Metrics: event ingestion rate, recommendation latency p50/p95/p99, share link usage.
- Alerting: high error rates, SLO violations, cost overruns.

**Cost Governance (Weeks 6–14)**:
- Provider request budgets: stop routing calls if monthly quota exceeded.
- Caching: route snapshots (7d), event lists (1h), forecast (4h).
- Sampling: LLM recommendation calls only for 20% of traffic initially, then ramp.
- Dashboard: per-feature spend visibility.

**Rollout Strategy (Weeks 13–14)**:
- Canary releases: 5% → 25% → 50% → 100% over 1 week.
- Feature flags enable per-feature rollout independently.
- Predefined rollback triggers: error rate >5%, p95 latency >2s, cost spike >20%.
- Post-release runbook: validation checks, alerting configuration.

**Key Files**:
- backend/auth/security.py (extend CORS, rate limiting)
- backend/middleware/ (new, observability, abuse detection)
- backend/config/logging.py (structured logging)
- backend/config/feature_flags.py (extended flags)
- backend/tests/test_security.py (rate limiting, authorization edge cases)
- backend/tests/test_observability.py (trace propagation)
- ops/rollout_plan.md (new)

**Verification**:
- All endpoints have rate-limit headers.
- CORS allows only registered origins.
- Traces propagate across service boundaries.
- Degraded mode engages when provider latency >2s.
- All tests pass; no regressions.

---

## Delivery Sequencing and Parallelization

### Track A: Backend Core (Critical Path)
- Phase 0 (Week 1): Guardrails ✓
- Phase 1 (Weeks 2–4): Foundation ✓
- Phase 2 (Weeks 5–7): Events ingestion ✓
- Phase 3 (Weeks 6–9): Routing adapter ✓ (overlap with Phase 2)
- Phase 4 (Weeks 8–11): Itineraries ✓ (overlap with Phase 3)
- Phase 5 (Weeks 10–12): Packing ✓

### Track B: Collaboration & Sharing
- Phase 1 (Weeks 2–4): Authorization layer ✓
- Phase 6 (Weeks 9–13): Sharing & collab ✓ (depends on Phase 1)

### Track C: UI and Platform Parity
- Phase 2 (Weeks 5–7): UI scaffolding begins (trip planner, events list) ✓
- Phase 4 (Weeks 8–11): Itinerary UX (mobile/web) ✓
- Phase 5 (Weeks 10–12): Packing UX ✓
- Phase 6 (Weeks 9–13): Sharing UX ✓
- Phase 7 (Weeks 11–14): Web-app integration & parity ✓

### Track D: Security/Operations (Gating)
- Phase 0 (Week 1): Requirements ✓
- Phase 8 (Weeks 1–14): Ongoing hardening, gates each release ✓

---

## Risk Register and Mitigation Strategies

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Schema drift during expansion | HIGH | Enforce preflight checks, parity validators, staged migrations. Test rollback in staging. |
| External API outage (routing, events) | HIGH | Provider abstraction, fallback provider, stale-while-revalidate caching, degraded UI mode. |
| Event data quality | MEDIUM | Confidence scoring, source trust tiers, dedup heuristics, quarantine malformed records. |
| Sharing security (link enumeration, token leaks) | MEDIUM | Signed opaque tokens, short expiry (7d), brute-force detection, audit logging. |
| Privacy leakage in shared views | MEDIUM | Least-privilege roles, redaction of sensitive fields, retention SLAs, consent audit. |
| Cost overrun from external providers | MEDIUM | Quotas, caching, sampling, per-feature spend dashboard, emergency caps. |
| Unsafe recommendations | MEDIUM | Deterministic guardrails, confidence thresholds, explainability, medical review. |
| Concurrent edit conflicts | MEDIUM | Optimistic concurrency, version vectors, server-side merge policy. |
| Web/mobile divergence | MEDIUM | Shared API contracts, parity tests as release blockers. |
| Performance regression | MEDIUM | Load tests on expensive endpoints, index verification, p95 latency gates. |
| Migration rollback complexity | MEDIUM | Reversible migrations, backup verification, staged rollback rehearsals. |

---

## Go/No-Go Milestones

### Milestone A: Foundation Complete (End of Week 4)
**Gate**: 
- Phase 1 models deployed and tested.
- Authorization layer in place.
- Migration preflight gates passing.
- Security baseline (CORS, rate limiting on auth endpoints) live.

**Acceptance Criteria**:
- 100+ unit tests passing (models, authorization, migrations).
- Zero parity divergence on legacy vs. new trip representations.
- Staging rollback rehearsal completed successfully.

---

### Milestone B: Event + Routing Intelligence in Beta (End of Week 9)
**Gate**:
- Phase 2 event ingestion live (limited events from Eventbrite, Meetup).
- Phase 3 routing adapter live with primary + fallback provider.
- Trip-scoped event API and route computation API exposed.
- Beta testing with 10% of users.

**Acceptance Criteria**:
- 30+ event sources integrated and normalized.
- Routes computed with <1s latency (p95).
- Fallback provider activates within 2s of primary failure.
- Zero data loss during provider outages.
- 80+ tests passing (scraper, routing, integration).

---

### Milestone C: Itinerary + Packing + Collaboration Complete (End of Week 13)
**Gate**:
- Phase 4 itineraries with recommendation engine live.
- Phase 5 packing lists generated and persistent.
- Phase 6 trip sharing with owner/editor/viewer roles live.
- Collaboration features (concurrent edits, activity feed) working.

**Acceptance Criteria**:
- Itinerary recommendations return top-3 with explanations.
- Conflict detection flags 100% of overlaps and travel impossibilities.
- Packing lists tie to underlying alerts with traceable rationale.
- Share links expire correctly; brute-force detection active.
- Concurrent edits resolve without data loss.
- 100+ tests (itinerary, recommendations, sharing, conflicts).

---

### Milestone D: Web/Mobile Parity + Production Hardening (End of Week 14)
**Gate**:
- Phase 7 web-app integration complete; Golby unified across platforms.
- Phase 8 security/operations hardening complete.
- Parity matrix 100% covered; contract tests passing.
- Canary rollout to 50% of users; no rollback triggers.

**Acceptance Criteria**:
- Web and mobile responses match for all shared endpoints (parity tests pass).
- Golby assistant available on both platforms with identical guardrails/feedback.
- CORS allowlist strict; rate limiting active on all endpoints.
- Observability (traces, metrics, logs) instrumented end-to-end.
- Cost spend within budget; provider usage monitored.
- Full accessibility audit passed (WCAG AA).
- 150+ tests total (all phases); zero regressions.

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Feature completeness | 100% of 5 capabilities | Feature flags all enabled, tests passing |
| API latency (p95) | <500ms (routes), <200ms (events, itinerary) | Prometheus metrics |
| Availability | 99.9% | Uptime monitoring |
| Data freshness (events) | <1h stale | Last ingestion timestamp |
| User adoption | 50% of users on trip features by Week 16 | Analytics |
| Cost per trip planned | <$0.05 (routing + LLM) | Spend dashboard |
| Authorization bypass attempts | 0 | Audit log review |
| Share link misuse attempts | <0.1% of generated links | Brute-force detection logs |

---

## Appendix: Integration Points with External Web App

The external web-app repository (cmps-357-sp26-final-project-cmps357-team-3) provides these features that will be integrated:

1. **Golby AI Assistant**: Onboarding tutorial, chat widget, personality shaping, feedback loop.
2. **Risk Scoring and Personalization**: User profile-aware risk weighting.
3. **Interactive Map**: Plotly-based map with risk overlays and filtering.
4. **Forecast Display**: Detailed 5/7-day forecast with personalized advice.
5. **Settings & Preferences**: User profile, notification settings, health conditions.

**Integration Strategy**:
- Map Golby backend endpoints to stable RiskRadar contracts.
- Reuse risk scoring engine for itinerary conflict detection.
- Preserve map and forecast UX; adapt to new trip/itinerary contexts.
- Deploy unified Golby to both web and mobile via shared backend service.

---

## Next Steps

1. **Approval & Kickoff**: Review plan with stakeholders; gain sign-off on scope and timeline.
2. **Team Allocation**: Assign engineers to Tracks A–D; establish stand-ups.
3. **Phase 0 Execution**: Finalize SLOs, feature flags, release gates in Week 1.
4. **Phase 1 Sprint**: Begin schema design and authorization layer (Week 2).
5. **Ongoing**: Weekly progress reviews; monthly risk reviews; go/no-go gates at milestones.

</parameter>