# RISKRADAR_SPRINT_ROADMAP.md

# Sprint-by-Sprint Execution Roadmap: RiskRadar Traveler Intelligence Expansion

## Overview

This roadmap breaks the 8-phase plan into **14 two-week sprints**, with explicit team roles, daily/weekly cadence, and go/no-go acceptance criteria. The timeline assumes a team of **8–10 engineers** split across backend, frontend, QA, and DevOps tracks.

**Sync Checklist (high level)**

- Core additions: Events ingestion, Routing provider adapter, Interactive Itineraries, Packing Lists, Trip Sharing, Golby parity.
- Data model changes: add `Trip`, `Itinerary`, `PackingList`, `TripShare`, extend `Place` with `allergen_flags`/`diet_tags` and provenance fields; add `user_health_profile` and `item_health_score` schemas and migrations.
- Safety & guardrails: `backend/services/health_guardrails.py` deterministic checks; explainability `{why, confidence, sources[], timestamp}`; `clinician_review_required` flagging and triage queues.
- Scraper updates: emit `source`, `confidence`, `trust_tier`, `allergen_flags`, and dead-letter handling for ambiguous records.
- Testing & ops: parity contract tests, migration preflight, LLM sampling/caching, circuit-breakers, and offline route snapshots.



## Team Structure (Recommended)


**Stand-ups**: Daily 15-min sync; weekly full-team sync on Monday.
**Demos**: Every sprint (Friday).
**Planning**: Sprint planning on Monday; retros on Friday.


## Sprint Schedule (14 × 2-week sprints = 28 weeks ≈ 7 months)

## Cross-cutting Priorities & Differentiators

These capabilities are strategic differentiators and must be worked in parallel across early sprints (0–4). Assign a small cross-functional team (Tech Lead, Backend, QA, Clinical Advisor) to coordinate.

- **Clinical & Legal Review Gate**: establish a clinician review workflow and legal sign-off process for any high‑risk medical or allergy guidance. Implement clinician_review_required flags in Phase 1 models and Sprint 2 scrapers.
- **Authoritative Data Partnerships**: prioritize onboarding 2–3 verified data partners (health orgs, municipal alert feeds, trusted event partners) and assign ingestion SLAs and trust tiers.
- **Provenance & Trust Signals**: standardize `source`, `confidence`, `trust_tier`, `last_seen` fields across scrapers and surface in APIs and UI explainability views.
- **Offline & Edge Resilience**: design route snapshotting, cached alerts, and local map tiles; include offline sync stories in Sprint 3 and Sprint 4.
- **Model Ops & Observability**: add LLM usage dashboards, hallucination detection, guardrail metrics, and automated sampling for human review (implement in Sprint 5 integration tests).
- **Human‑in‑the‑loop Ops**: define triage queues for flagged outputs, clinician review UIs, and escalation paths; staff rota in Ops plan.
- **Privacy & Compliance Controls**: encryption-at-rest, consent flows for `user_health_profile`, and data export/redaction APIs added in Sprint 1.
- **Threat Modeling & Security Gates**: run STRIDE reviews for each feature area, maintain a live risk register, and block releases on unresolved critical/high findings.
 
**Security Plan Cross-Link & Tasks**

- The detailed security implementation plan and phase-by-phase breakdown live in `docs/expansion/RISKRADAR_EXPANSION_SECURITYPLAN.md`. All security subtasks below map back to that plan and must be tracked in the living risk register.
- Quick mapping of phases → sprints (high-level):
	- Phase 0 (Baseline) -> Sprint 0 (pre-sprint / week 1): CI gates, SBOM, SAST, assign security owner.
	- Phase 1 (Auth & Authorization) -> Sprint 1: RBAC, row-level checks, refresh-token rotation, MFA hooks.
	- Phase 2 (Data Protection) -> Sprint 1–2: field-level encryption, backups, secure deletion workflows.
	- Phase 3 (API Hardening) -> Sprint 2–4: CORS allowlist, CSP/HSTS, rate-limiting, WAF rules.
	- Phase 4 (LLM & Provider Safety) -> Sprint 4–6: guardrails, prompt-safety pipeline, review queue.
	- Phase 5 (CI/CD & Supply Chain) -> Sprint 5–7: DAST, container/IaC scanning, signed builds, SBOM enforcement.
	- Phase 6 (Observability & IR) -> Sprint 6–9: telemetry, restore drills, pentest, IR runbooks.

- Action: Add a checklist item for each sprint ticket referencing the security plan section and the living risk register entry. CI must include SAST/secret-scan and block merge on critical findings for any PR that touches security-sensitive files.
- **Secure SDLC & Supply Chain**: add SAST, DAST, secret scanning, dependency scanning, container/IaC scanning, SBOM generation, and signed-build verification to CI.
- **Zero-Trust Operations**: use least-privilege service accounts, short-lived credentials, mTLS/service auth, and managed key rotation for sensitive data and backups.
- **Incident Response & Recovery**: rehearse breach response, backup restore, rollback, and provider-compromise playbooks before canary and GA.
- **User Research & Accessibility**: run focused user interviews with allergy/health-affected travelers; schedule accessibility audit (WCAG AA) in Sprint 9–10.

**Backfill Security Addenda for New Planned Features**

The roadmap below now includes explicit security tasks for the newly planned forecast, allergen, tide/outbreak, routing, and import capabilities. These items are release-gating work, not optional polish.

- Sprint 2 security work: Forecast completeness
	- Add provider allowlists, strict schema validation, and timeout/circuit-breaker behavior for forecast enrichment.
	- Add cache-poisoning, stale-data, and missing-field tests for `uvi`, `dew_point`, `visibility`, `pressure`, and `feels_like`.
	- Acceptance gate: degraded mode renders safely if the provider drops fields or fails.

- Sprint 2 security work: Astronomy and celestial timing
	- Add provider allowlists, timezone/DST validation, and freshness checks for sunrise, sunset, moonrise, moonset, moon phase, moon illumination, and celestial events.
	- Add tests for invalid dates, timezone shifts, and stale or malformed moon/sun payloads.
	- Acceptance gate: astronomy data renders with safe fallback values if the provider is unavailable.

- Sprint 2–3 security work: Places and allergen extraction
	- Require sanitization of menu text, OCR output, and any embedded HTML before extraction.
	- Add confidence thresholds and a review/dead-letter path for ambiguous allergen matches.
	- Acceptance gate: low-confidence allergen records never auto-raise unsafe advice.

- Sprint 3 security work: Tides, outbreaks, and multimodal routing
	- Add source trust tiers, freshness checks, and a strict provider allowlist for all coastal, weather, outbreak, and routing feeds.
	- Store route snapshots with provider metadata and reject malformed route legs or advisories.
	- Acceptance gate: provider outage or malformed input falls back to a clearly labeled degraded advisory.

- Sprint 4–5 security work: Import/connectors for itineraries
	- Make calendar, PNR, and email imports opt-in with explicit consent and revocation.
	- Scan and size-limit all imported content before parsing; redact raw message content from logs.
	- Acceptance gate: imported trips can be deleted cleanly and no raw import payload remains in telemetry.

- Sprint 4–6 security work: Health-aware recommendations and guardrails
	- Ensure any recommendation that can become prescriptive passes through `backend/services/health_guardrails.py` first.
	- Require `{why, confidence, sources[], timestamp}` and `clinician_review_required` where the policy or confidence threshold demands it.
	- Acceptance gate: no health-sensitive advice ships without provenance, confidence, and the right escalation flag.

Add a checklist item for each of the above in the sprint ticket itself and link it back to `docs/expansion/RISKRADAR_EXPANSION_SECURITYPLAN.md` so the security review cannot be bypassed.


**Theme**: Lock scope, define contracts, establish automation gates.

**Team**: Tech Lead (1), Backend Lead (1), DevOps (1).

**Daily Goals**:
- Week 1: Define SLOs, feature flags, release gates.
- Week 2: Implement feature flag infrastructure, preflight checks, CI gates.

**Deliverables**:
- SLO document: latency targets, availability, cost budgets, accessibility requirements.
- Feature flag schema and admin UI.
- Preflight check script (migration validation).
- CI gate definitions (test pass rate, coverage min, regression suite).
- API versioning policy documented.
 - Parity checklist added to docs and integrated into CI gates (`docs/PARITY_CHECKLIST.md`).

**Acceptance Criteria**:
- [ ] Feature flags toggleable without redeploy.
- [ ] Preflight checks pass in staging.
- [ ] CI gates block PRs that fail tests or reduce coverage.
- [ ] Tech lead sign-off on scope and approach.

**Risk Mitigation**: 
- Define emergency rollback procedures.
- Lock on-call escalation policy.

---

### **Sprint 1: Schema Foundation & Authorization** (Weeks 3–4)

**Theme**: Database foundation and role-based access control.

**Team**: Backend (2), QA (1).

**Daily Goals**:
- Week 1: Design Trip, TripStop, Event, Itinerary entities; create ORM models and migration scripts.
- Week 2: Implement authorization layer; dual-write to legacy SavedDestination; write parity validators.

**Deliverables**:
- ORM models for Trip, TripStop, Event, Itinerary, ItineraryItem, PackingList, TripShare, TripCollaboratorActivity.
- Migration script (expand phase): add new tables, preserve legacy.
- Rollback script (contract phase): remove legacy if needed.
- Authorization module: row-level checks for owner, editor, viewer, public-link access.
- Parity validator: ensures legacy and new representations stay in sync.
- Index creation script: trip date windows, geospatial, dedup keys, collaboration paths.

**Tests** (>50):
- Unit: model relationships, foreign key constraints.
- Integration: migration rollback, parity checks, authorization enforcement.

**Acceptance Criteria**:
- [ ] All models compile and pass type checks.
- [ ] Migration scripts run without errors on staging.
- [ ] Parity validator shows zero divergence.
- [ ] Authorization tests cover all role combinations.
- [ ] Preflight gates pass; no schema warnings.

**Risk Mitigation**:
- Rehearse rollback in staging.
- Backup database before applying migration.

---

### **Sprint 2: Event Scraper Platform – Ingestion** (Weeks 5–6)

**Theme**: Build event ingestion pipeline and APIs.

**Parallel with Sprint 1 end**.

**Team**: Backend (2), QA (1).

**Daily Goals**:
- Week 1: Design EventScraper base class; add YAML config for Eventbrite, Meetup; implement normalization.
- Week 2: Add deduplication, quality controls; build trip-scoped event API; write integration tests.

**Deliverables**:
- EventScraper base class extending BaseScraper.
- YAML config entries for 3–5 event sources (Eventbrite, Meetup, Festivals API, web extraction fallback).
- Event normalization pipeline: schema validation, category mapping, confidence scoring.
- Deduplication logic: (source, source_id) constraint + fuzzy matching.
- Quality controls: stale-event pruning, anomaly detection.
- Event model and database schema updates.
- API endpoint: GET /api/v1/trips/{id}/events (filters by date/location, ranked by relevance).
- Scraper integration tests with mocked responses.

Additional Deliverables (safety & services):
- `CrimeScraper` and ingestion pipeline for crime incidents; models and trip-scoped safety APIs (`/api/v1/trips/{id}/safety`).
- `PlacesScraper` for food/essentials (restaurants, grocery stores, markets); `Place` models and `/api/v1/trips/{id}/places` API with dietary/allergy filters.
- `LodgingScraper` ingestion for hotels/hostels/short-term rentals; `Lodging` models and `/api/v1/trips/{id}/lodging` API with safety-aware ranking.
- Integration tests covering deduplication, confidence scoring, and ranking across sources.

**Tests** (>30):
- Unit: normalization, dedup, quality checks.
- Integration: scraper end-to-end, API filters.
- Mocked responses: Eventbrite, Meetup, web extraction.

**Acceptance Criteria**:
- [ ] Scraper normalizes test payloads without errors.
- [ ] Deduplication prevents duplicate inserts across runs.
- [ ] Trip event API returns results ranked by user interest.
- [ ] Quality scores flag low-confidence events.
- [ ] 30+ tests passing.

Additional Acceptance Criteria:
- [ ] Crime/places/lodging scrapers normalize representative payloads and appear in parity matrix.
- [ ] Trip safety, places, and lodging endpoints return results constrained to trip geometry/time window and respect confidence filters.
- [ ] 40+ integration tests covering new scrapers and APIs.

**Risk Mitigation**:
- Implement rate limiting on event API calls (prevent abuse).
- Quarantine malformed records to dead-letter table.

---

### **Sprint 3: Routing Provider Adapter & Travel Risk** (Weeks 7–8)

**Theme**: Build routing infrastructure with provider abstraction.

**Parallel with Sprint 2**.

**Team**: Backend (2), QA (1).

**Daily Goals**:
- Week 1: Design routing adapter interface; implement OpenRouteService provider; build route computation API.
- Week 2: Add fallback provider; implement risk enrichment pipeline; add degraded-mode behavior.

**Deliverables**:
- Routing provider adapter interface (primary + fallback).
- OpenRouteService implementation (recommended as primary).
- (Optional) Google Maps or Mapbox as fallback.
- Route model and database schema: RoutePlan, RouteLeg.
- Route computation API: POST /api/v1/trips/{id}/routes (origin, destination, waypoints).
- Route snapshot storage with provider metadata, timestamps.
- Travel risk enrichment: overlay alerts and traffic incidents onto route legs.
- Safe-reroute recommendation engine: score alternatives on travel time, hazard severity, closure probability.
- Degraded-mode fallback: cached route + risk-only advisory when provider down.
- Cost/abuse controls: request quotas, per-user limits, caching, backoff.

**Tests** (>40):
- Unit: adapter interface, provider implementations, risk scoring.
- Integration: route computation end-to-end, fallback activation, degraded mode.
- Mocked responses: multiple route alternatives, outage scenario.

**Acceptance Criteria**:
- [ ] Route computation returns multi-leg route with hazard overlay.
- [ ] Fallback provider activates within 2s of primary timeout.
- [ ] Reroute scoring favors lower-hazard alternatives.
- [ ] Degraded mode surfaces risk-only advisory with uncertainty language.
- [ ] Cost quotas prevent overages.
- [ ] 40+ tests passing.

**Risk Mitigation**:
- Circuit breaker pattern: fail open to degraded after 3 failures.
- Cache routes for 7 days to handle provider downtime.

---

### **Sprint 4: Itinerary CRUD & Conflict Detection** (Weeks 9–10)

**Theme**: Build interactive itinerary planning with conflict detection.

**Depends on Sprint 1 (authorization), Sprint 2 (events), Sprint 3 (routes)**.

**Team**: Backend (2), Frontend (1), QA (1).

**Daily Goals**:
- Week 1: Design Itinerary and ItineraryItem CRUD; add conflict detection logic; build API endpoints.
- Week 2: Integrate with events and routes; add proactive health checks; build mobile/web UI scaffolding.

**Deliverables**:
- Itinerary CRUD API: POST/GET/PUT/DELETE /api/v1/trips/{id}/itinerary.
- ItineraryItem endpoints: add/remove activities, update times/locations.
- Conflict detection logic: overlapping activities, unrealistic travel windows, high-risk times.
- Health checks: flag when conditions degrade (alerts escalate, routes become hazardous).
- Itinerary model with day-level timeline views.
- Mobile UI: trip planner screen, day-by-day activity list (React Native).
- Web UI: itinerary day planner (PHP/HTML).

**Tests** (>30):
- Unit: conflict detection rules, health checks.
- Integration: CRUD operations, permission checks, event/route linkages.
- E2E: create trip, add itinerary, add activities, detect conflicts.

**Acceptance Criteria**:
- [ ] Itinerary CRUD operations work end-to-end.
- [ ] Conflict detection flags 100% of overlaps.
- [ ] Health checks trigger alerts when risk thresholds crossed.
- [ ] Mobile and web UIs render itineraries correctly.
- [ ] 30+ tests passing.

**Risk Mitigation**:
- Guardrails prevent unsafe activity suggestions.
- Explainability fields show why conflicts flagged.

---

### **Sprint 5: Recommendation Engine & Explanation** (Weeks 11–12)

**Theme**: Build AI-powered activity recommendations.

**Depends on Sprint 4, Sprint 2 (events), Sprint 3 (routes)**.

**Team**: Backend (2), QA (1).

**Daily Goals**:
- Week 1: Design recommendation algorithm; integrate risk signals, events, user interests; build explanation fields.
- Week 2: Add confidence scoring, guardrails; tune ranking; write integration tests.

**Deliverables**:
- Recommendation engine API: POST /api/v1/trips/{id}/recommendations (returns top-3 activities with scores).
- Recommendation algorithm: combine risk, event availability, user interests, travel constraints.
- Explanation fields: recommendation reason, risk tradeoffs, confidence, data freshness.
- Confidence scoring: suppress recommendations below threshold.
- Guardrails: prevent unsafe suggestions (e.g., outdoor activity during critical air quality).
- LLM prompt templates for recommendation generation and explanation.
- Recommendation scoring tests: accuracy, ranking quality.

**Tests** (>25):
- Unit: scoring algorithm, confidence thresholds, guardrails.
- Integration: recommendation API end-to-end, explanation generation.
- Mocked: various user profiles, alert combinations.

**Acceptance Criteria**:
- [ ] Recommendation API returns top-3 with explanations and scores.
- [ ] Confidence scores below threshold suppress recommendations.
- [ ] Guardrails prevent unsafe suggestions.
- [ ] 25+ tests passing.

**Risk Mitigation**:
- Medical/safety recommendations require explicit guardrail approval.
- Rationale fields prevent black-box recommendations.

---

### **Sprint 6: Packing List Generation & Persistence** (Weeks 13–14)

**Theme**: Generate and manage trip-specific packing lists.

**Depends on Sprint 1 (Trip model), Sprint 4 (itinerary), existing packing API**.

**Team**: Backend (1), Frontend (1), QA (1).

**Daily Goals**:
- Week 1: Extend existing packing API; add category-based generation; tie to itinerary/alerts.
- Week 2: Build user-editable workflows; add collaborative packing; implement guardrails.

**Deliverables**:
- PackingList persistent storage: category, items, completion state, assignments.
- Extend POST /api/v1/packing/guide to tie recommendations to itinerary/alerts.
- Packing category generation: clothing/layers, weather gear, documents, health/first aid, activity-specific.
- User-editable workflows: checkboxes, item categories, assignment tags, due dates.
- Collaborative packing: shared lists, cross-user assignment.
- Guardrails: suppress advice when data sparse, require uncertainty language.
- Mobile UI: packing list screen with category breakdowns.
- Web UI: packing checklist with item tracking.

**Tests** (>30):
- Unit: category generation, guardrails, conflict resolution in collaborative edits.
- Integration: packing API end-to-end, persistence, multi-user edits.
- E2E: create trip, generate packing list, edit items, share with collaborator.

**Acceptance Criteria**:
- [ ] Packing lists generate with all categories populated.
- [ ] Items traceable to underlying alerts/activities.
- [ ] Collaborative edits merge without conflicts.
- [ ] Guardrails suppress low-confidence advice.
- [ ] Mobile and web UIs fully functional.
- [ ] 30+ tests passing.

**Risk Mitigation**:
- Rationale fields justify all recommendations.
- Uncertainty messaging when data sparse.

---

### **Sprint 7: Trip Sharing – Invite & Link** (Weeks 15–16)

**Theme**: Enable account-based and link-based trip sharing.

**Depends on Sprint 1 (authorization)**.

**Team**: Backend (2), Frontend (1), QA (1).

**Daily Goals**:
- Week 1: Design share model (roles, invite flow, link generation); implement account-based invites.
- Week 2: Implement public links with expiry/revocation; add audit logging; build UI for sharing.

**Deliverables**:
- TripShare model: owner → recipient (account invite) or public link token.
- Account-based invite: email recipient, auto-accept on login, audit logging.
- Public link: signed opaque token, expiry (default 7 days), revocation, brute-force detection.
- Share management API: POST/DELETE /api/v1/trips/{id}/shares.
- Authorization enforcement: viewer/editor/owner role checks on all trip endpoints.
- Activity feed: track edits, assignments, changes over time.
- Audit log: all access, modifications, shares, revocations.
- Mobile UI: share button, invite recipients, view collaborators.
- Web UI: share modal, generate link, manage permissions.

**Tests** (>40):
- Unit: token generation, expiry logic, brute-force detection.
- Integration: invite flow end-to-end, link access control, concurrent edits.
- E2E: create trip, invite user, share link with unregistered user, revoke access.
- Security: attempt unauthorized access, expired link, brute-force link.

**Acceptance Criteria**:
- [ ] Invite flow creates share record; recipient gains access after login.
- [ ] Public link works for unauthenticated access; expires at T+7d.
- [ ] Authorization checks block unauthorized access (403).
- [ ] Audit log records all actions.
- [ ] Brute-force detection blocks >10 failed attempts per link per IP per hour.
- [ ] Mobile and web share UIs fully functional.
- [ ] 40+ tests passing.

**Risk Mitigation**:
- Share links are signed opaque tokens (not incrementing IDs).
- Explicit consent required to share; recipient sees who shared it.

---

### **Sprint 8: Concurrency & Conflict Resolution** (Weeks 17–18)

**Theme**: Handle concurrent edits in shared trips.

**Depends on Sprints 6–7**.

**Team**: Backend (2), QA (1).

**Daily Goals**:
- Week 1: Design versioning/concurrency model; implement optimistic locking.
- Week 2: Add conflict detection and resolution; write comprehensive tests.

**Deliverables**:
- Version vectors or timestamps for optimistic concurrency.
- Conflict detection: when two users edit same field concurrently.
- Server-side merge policy: last-write-wins (LWW) or user-prompted resolution.
- Conflict resolution UI: show delta, let user choose version.
- Idempotency keys for all mutations (prevent double-posts).
- Comprehensive concurrency tests: read-your-writes, conflict scenarios, rollback.

**Tests** (>25):
- Unit: version comparison, merge logic.
- Integration: concurrent CRUD operations, conflict scenarios.
- Stress: 10+ users editing same trip simultaneously.

**Acceptance Criteria**:
- [ ] Concurrent edits resolve without data loss.
- [ ] Conflicts flagged to user with clear options.
- [ ] Idempotency keys prevent double-posts.
- [ ] 25+ tests passing, including stress tests.

**Risk Mitigation**:
- Explicit conflict prompts prevent silent overwrites.
- Audit log tracks all conflict resolutions.

---

### **Sprint 9: Web-App Parity Assessment & Adapter** (Weeks 19–20)

**Theme**: Map external web-app features to RiskRadar APIs.

**Depends on Sprints 1–7 (all backend features)**.

**Team**: Tech Lead (1), Backend (1), Frontend (1), QA (1).

**Daily Goals**:
- Week 1: Audit external web-app API contracts; build parity matrix.
- Week 2: Implement adapter layer; map web-app calls to stable RiskRadar endpoints.

**Deliverables**:
- Parity matrix: external web-app endpoints vs. RiskRadar equivalents.
- Request/response schema mapping for all shared features.
- Adapter layer: map web-app calls to RiskRadar endpoints (middleware or client library).
- API contract definitions (OpenAPI specs or Pydantic models).
- Parity tests: for every shared endpoint, verify web and mobile responses match.
 - Coverage expansion: include personalized risk score, interactive maps, forecast/risk views, itinerary planning, packing guidance, collaboration, sharing, and import flows in the parity matrix.
 - Shared map behavior: ensure route overlays, hazard layers, route alternatives, and location search behave the same on web and mobile.
 - Shared recommendation behavior: ensure web and mobile both expose the same explanations, confidence values, and `Why?` affordances for itineraries, packing, and route advice.
 - Follow `docs/PARITY_CHECKLIST.md` during implementation and CI; ensure contract tests and parity validator run as part of the PR gate.

**Tests** (>30):
- Contract tests: all parity endpoints tested in parallel (web, mobile, direct API).
- Schema validation: request/response shapes match contract.
- E2E: walk through typical user journey (search events, plan itinerary, share trip) on all surfaces.

**Acceptance Criteria**:
- [ ] Parity matrix covers 100% of external web-app requirements.
- [ ] Adapter layer maps all calls without errors.
- [ ] Contract tests pass; all surfaces return equivalent responses.
- [ ] Tech lead reviews and approves parity approach.

**Risk Mitigation**:
- Contract tests are release blockers.
- Defer platform-specific UX optimizations until after parity lock.

---

### **Sprint 10: Golby Unification & Assistant Parity** (Weeks 21–22)

**Theme**: Centralize Golby backend and deploy to both web and mobile.

**Depends on Sprints 1–9**.

**Team**: Backend (1), Frontend (2), QA (1).

**Daily Goals**:
- Week 1: Centralize Golby backend contracts in RiskRadar APIs; ensure onboarding, guardrails, profile shaping centralized.
- Week 2: Deploy Golby widget to mobile; verify parity with web; add context-aware prompts for new features.

**Deliverables**:
- Centralized Golby backend: /api/v1/assistant/* endpoints for chat, onboarding, profile, feedback.
- Unified Golby widget deployed to both web and mobile.
- Shared schema: AssistantRequest, AssistantResponse, GolbyProfile, etc.
- Onboarding state tracking: has_completed_onboarding boolean.
- Guardrails enforced at backend (medical, legal, emergency, unsafe queries).
- Profile shaping: personality dimensions (warmth, calmness, humor, etc.) applied consistently.
- Feedback loop: thumbs up/down influences future responses on both platforms.
- Context-aware prompts for new features: events, routes, itineraries.
- Parity tests: same prompts, same model, same responses on web and mobile.
 - Golby feature breadth: add first-class support for personalized risk score explanation, interactive maps, route overlays, forecast summaries, itinerary planning, packing guidance, trip imports, and collaboration/share workflows.
 - Golby actionability: let users ask Golby to plan, reroute, repack, reschedule, compare safety tradeoffs, and explain why a recommendation is risky or safe.
 - Golby memory: persist preferences for tone, risk tolerance, travel pace, dietary/allergy constraints, preferred map detail, and past itinerary style.
 - Golby web-app parity: the web widget must mirror mobile guidance, recommendations, and safety escalation behaviors exactly.

**Golby Intelligence Requirements**:
- Golby must act as the primary travel advisor inside RiskRadar, not just a chat widget, by understanding the user’s trip, itinerary, packing needs, alerts, saved places, and collaboration state.
- Golby must assemble answers from live app context first, then fall back to summarization, rather than relying on generic travel advice.
- Golby must persist user preferences and conversational learning signals so each traveler gets progressively better recommendations over time.
- Golby must keep a warm, friendly, and encouraging voice while adapting detail level, caution level, and humor to each user.
- Golby must proactively offer the next best action, such as planning a day, updating packing, checking route risk, or warning about a time-sensitive alert.
- Golby must expose its reasoning in user-friendly terms, including what live data it used and why a suggestion was made.
- Golby must support opt-in memory controls, including clear data export, preference editing, and memory reset.
- Golby must also explain the user's personalized risk score, interactive map findings, weather/forecast shifts, route hazards, and import summaries in plain language.
- Golby must help users discover what changed, why it matters, and what to do next when the app surfaces a new event, place, alert, itinerary conflict, packing need, or sharing change.
- Golby must remain the same helpful guide across web and mobile, using the same guardrails, same provenance, and same recommendation rules.

**Golby Advice Principles**:
- Lead with the safest, most useful recommendation first.
- Explain why the advice matters using live RiskRadar context.
- Separate facts, confidence, and next steps so users can act quickly.
- Adapt tone and detail to the traveler’s preferences and past feedback.
- Ask a clarifying question only when it materially improves the answer.

**Tests** (>40):
- Unit: guardrail detection, profile shaping logic.
- Integration: Golby API end-to-end, feedback persistence.
- Parity: identical prompts on web and mobile yield identical responses.
- E2E: register new user, see onboarding, interact with Golby, give feedback, see personality changes.
- Unit: context assembly from trips, itineraries, alerts, and packing lists.
- Integration: memory persistence, preference updates, and next-best-action suggestions.
- E2E: itinerary update triggers a Golby recommendation, packing reminder, or alert explanation.

**Acceptance Criteria**:
- [ ] Golby widget loads on both web and mobile.
- [ ] Chat accepts input and returns responses.
- [ ] Guardrails activate for inappropriate queries.
- [ ] Personality shaping works: different users get different styles.
- [ ] Feedback loop persists; personality drifts over time.
- [ ] Parity tests show web and mobile responses match.
- [ ] Golby can answer itinerary, packing, planning, and feature-navigation questions using live RiskRadar context.
- [ ] Golby learns from user feedback and preference changes without losing safety guardrails.
- [ ] Golby can explain which alerts, trips, itineraries, or packing rules informed each recommendation.
- [ ] 40+ tests passing.

**Risk Mitigation**:
- Guardrails are release blockers.
- Centralized backend prevents divergent behaviors.

---

### **Sprint 11: Security Hardening – Authentication & Authorization** (Weeks 23–24)

**Theme**: Strengthen auth, access control, and abuse prevention.

**Cross-cutting, depends on all previous sprints**.

**Team**: Backend (1), DevOps (1), QA (1).

**Daily Goals**:
- Week 1: Implement strict CORS allowlist, endpoint-level rate limiting, token rotation.
- Week 2: Add abuse detection, secret hygiene, pass security audit.

**Deliverables**:
- Strict CORS allowlist: specific origins, not wildcard.
- Endpoint-level rate limiting: 100 req/min per user for routes, 50 for recommendations, etc.
- JWT refresh tokens; logout invalidation.
- Secure session handling: secure cookies, refresh-token reuse detection, session revocation, and step-up auth for risky actions.
- Abuse detection: repeated failed auth, unusual API patterns.
- Secret rotation: LLM API keys monthly, use HashiCorp Vault or equivalent.
- OWASP Top 10 mitigation: SQL injection (parameterized queries), XSS (sanitization), CSRF tokens, SSRF protection, open-redirect checks, and clickjacking defenses.
- Browser and API hardening: CSP, HSTS, X-Content-Type-Options, secure cache headers, and origin-bound callbacks.
- Security tests: rate limiting bypass attempts, authorization bypass, token leaks, dependency scans, secret scans, and container scan failures.
- WAF/bot mitigation: throttling for credential stuffing, link enumeration, and scraping bursts.

**Tests** (>20):
- Unit: rate limiter, abuse detector, token rotation.
- Integration: auth flow end-to-end, CORS headers, secret rotation.
- Security: attempt bypass of rate limits, unauthorized access, token reuse, CSRF, SSRF, and prompt-injection entry points.
- CI: fail builds on critical SAST/DAST, dependency, or secret-scan findings.

**Acceptance Criteria**:
- [ ] CORS allowlist enforced; wildcard removed.
- [ ] Rate limiting active on all endpoints; bypass attempts fail.
- [ ] Token rotation works; old tokens invalidated on logout.
- [ ] Abuse detection flags unusual patterns.
- [ ] Security headers present on all web responses.
- [ ] Critical/high security scanner findings are fixed before release.
- [ ] Security tests pass; no known vulnerabilities.

**Risk Mitigation**:
- Emergency disable switches for rate limiting in case of issues.
- Secret rotation does not disrupt service.
- All privileged actions are logged and reviewed.

---

### **Sprint 12: Data Privacy & Retention** (Weeks 25–26)

**Theme**: Implement privacy controls and compliance.

**Cross-cutting, depends on Sprints 1–11**.

**Team**: Backend (1), DevOps (1), QA (1).

**Daily Goals**:
- Week 1: Implement data retention policies, encryption at rest, GDPR/CCPA compliance.
- Week 2: Add data export/deletion, audit trail, shared-view redaction.

**Deliverables**:
- Retention policies: delete collab audit logs after 1 year, share links after expiry.
- Encryption at rest: share link tokens, sensitive user data, backups, and derived caches.
- Field-level encryption for health profile, share tokens, and any sensitive collaboration metadata.
- GDPR compliance: user data export endpoint, deletion workflow.
- CCPA compliance: opt-out audit, tracking preference storage.
- Shared-view redaction: hide health conditions, device tokens from viewers.
- Audit trail: all access and modifications logged with user/timestamp.
- Secure deletion: verify deletes propagate to primary data, replicas, caches, and exported artifacts.
- Privacy tests: verify sensitive data not exposed in shared views.

**Tests** (>15):
- Unit: retention policy logic, encryption/decryption.
- Integration: data export end-to-end, deletion workflow, audit trail.
- Privacy: verify sensitive fields redacted in shared views.

**Acceptance Criteria**:
- [ ] Data retention policies enforced; old logs deleted.
- [ ] Sensitive data encrypted at rest.
- [ ] User data export returns correct data.
- [ ] Deletion workflow removes data from all tables.
- [ ] Shared-view redaction hides sensitive fields.
- [ ] Audit trail complete and queryable.
- [ ] 15+ tests passing.

**Risk Mitigation**:
- Retention policies reviewed by legal; backup snapshots kept for compliance.
- Data export tested before compliance deadline.
- Keys rotated on a fixed schedule and after any suspected compromise.

---

### **Sprint 13: Observability & Cost Governance** (Weeks 27–28)

**Theme**: Implement monitoring, logging, and cost controls.

**Cross-cutting, depends on all previous sprints**.

**Team**: Backend (1), DevOps (1), QA (1).

**Daily Goals**:
- Week 1: Add structured logging, distributed tracing, metrics collection.
- Week 2: Add cost dashboard, request quotas, sampling, spend monitoring.

**Deliverables**:
- Structured logging: JSON logs with request ID, user ID, trace ID, severity.
- Distributed tracing: trace routing calls, recommendation engine, event ingestion.
- Metrics: event ingestion rate, recommendation latency p50/p95/p99, share link usage, cost per trip.
- Alerting: high error rates, SLO violations, cost overruns.
- Security telemetry: auth failures, authorization denials, token revocations, link-enumeration attempts, guardrail triggers, and suspicious provider responses.
- Cost dashboard: per-feature spend visibility, quota usage.
- Request quotas: stop routing calls if monthly quota exceeded.
- Caching: route snapshots (7d), event lists (1h), forecast (4h).
- Sampling: LLM recommendation calls only for 20% of traffic initially, then ramp.
- Observability tests: verify traces propagate, logs structured, metrics exported.
- Incident-response alerts: data exfiltration, provider compromise, and brute-force attacks page the on-call team.

**Tests** (>15):
- Unit: quota logic, cache TTL, sampling algorithm.
- Integration: trace propagation end-to-end, metrics exported to Prometheus.
- Load test: cost under load; caching effective; sampling reduces LLM calls.

**Acceptance Criteria**:
- [ ] Logs structured and queryable (Kibana or equivalent).
- [ ] Traces propagate across service boundaries.
- [ ] Metrics exported to Prometheus; dashboards visible.
- [ ] Quota enforcement prevents overages.
- [ ] Caching reduces database load by >20%.
- [ ] Sampling reduces LLM costs by >80% at 20% traffic.
- [ ] 15+ tests passing.

**Risk Mitigation**:
- Alerts trigger on cost spike >20%.
- Fallback to cached data if external API call fails.
- Log redaction prevents secrets and health data from entering telemetry.

---

### **Sprint 14: Accessibility & Platform-Specific UX** (Weeks 29–30, Partial Overlap)

**Theme**: Ensure WCAG AA compliance and polish platform-specific UX.

**Cross-cutting, depends on Sprints 4–7 (UX screens)**.

**Team**: Frontend (2), QA (1).

**Daily Goals**:
- Week 1: Audit accessibility on web and mobile; fix WCAG AA issues; add keyboard navigation.
- Week 2: Polish responsive design; add platform-specific optimizations (native feel for mobile, web polish).

**Deliverables**:
- WCAG AA accessibility audit: color contrast, keyboard nav, screen reader compat.
- Accessibility fixes: alt text, ARIA labels, semantic HTML, focus indicators.
- Keyboard navigation: all UX surfaces navigable without mouse.
- Responsive design: mobile-first, tablet/desktop breakpoints.
- Platform-specific polish: native Expo animations for mobile, CSS polish for web.
- Accessibility tests: automated + manual (screen reader, keyboard).

**Tests** (>20):
- Unit: component props (accessibility attributes).
- E2E: navigate entire UX with keyboard, screen reader.
- Automated: axe-core accessibility scanner.
- Manual: tested with NVDA, JAWS, iOS VoiceOver.

**Acceptance Criteria**:
- [ ] WCAG AA accessibility audit passes.
- [ ] All UX surfaces keyboard navigable.
- [ ] Screen reader announces all content.
- [ ] Responsive design works on mobile/tablet/desktop.
- [ ] Platform-specific UX feels native.
- [ ] 20+ accessibility tests passing.

**Risk Mitigation**:
- Accessibility reviewed by users with disabilities.
- Continuous testing with accessibility tools.

---

### **Sprint 15: Release Prep & Canary Deployment** (Weeks 31–32)

**Theme**: Final testing, documentation, canary rollout.

**Depends on all previous sprints**.

**Team**: All (1 per track + tech lead).

**Daily Goals**:
- Week 1: Final regression tests, documentation, release notes, runbook.
- Week 2: Canary deployment (5% users), monitoring, collect telemetry.

**Deliverables**:
- Final regression test suite: 200+ tests, all passing.
- Release notes: features, fixes, known issues.
- API documentation: OpenAPI specs for all new endpoints.
- Operations runbook: deployment, rollback, alerting.
- Independent penetration test and red-team review, with all critical/high findings closed before GA.
- Disaster-recovery drill: backup restore, failover, and rollback verified in staging.
- Canary deployment: 5% of users on new features; monitoring enabled.
- Rollback procedure: documented, tested.
- Post-release verification checklist.

**Tests** (All**):
- Regression: full suite, no failures.
- Canary: 5% user subset, 48h observation.
- Monitoring: SLO dashboards visible, alerting active.

**Acceptance Criteria**:
- [ ] All regression tests passing.
- [ ] Canary deployment stable (error rate <1%, latency <SLO).
- [ ] Documentation complete and reviewed.
- [ ] Rollback tested and verified.
- [ ] Penetration-test findings resolved or explicitly waived by security leadership.
- [ ] Restore drill proves data can be recovered within the recovery objective.
- [ ] Tech lead sign-off to proceed to wider rollout.

**Risk Mitigation**:
- Predefined rollback triggers: >5% error rate, >2s p95 latency, cost spike >20%.
- 24/7 on-call during canary period.
- Release blocked if critical security findings remain open.

---

### **Sprint 16: Progressive Rollout & Monitoring** (Weeks 33–34)

**Theme**: Gradual rollout to all users; continuous monitoring.

**Depends on Sprint 15 (canary)**.

**Team**: DevOps (1), QA (1), On-call rotation (all).

**Daily Goals**:
- Week 1: Expand canary to 25% users; analyze metrics; fix critical issues.
- Week 2: Expand to 50% → 100%; final validation.

**Deliverables**:
- Progressive rollout: 5% → 25% → 50% → 100% over 2 weeks.
- Monitoring dashboards: SLOs, error rates, cost, recommendation quality.
- Incident playbook: response procedures for alerts.
- User feedback collection: survey, early user interviews.
- Go/no-go decision: proceed to next sprint or rollback.

**Tests** (Continuous**):
- Canary monitoring: error rate, latency, cost trending.
- Production validation: spot checks on production environment.
- User feedback: survey respondents, early adopter interviews.

**Acceptance Criteria**:
- [ ] Canary 5% → 100% rollout completed smoothly.
- [ ] SLOs maintained throughout rollout.
- [ ] Zero critical incidents requiring rollback.
- [ ] Cost within budget.
- [ ] User feedback positive (>80% satisfaction).
- [ ] Tech lead approves full release.

**Risk Mitigation**:
- Rollback capability maintained at every stage.
- Daily metrics reviews; alert thresholds trigger investigation.

---

## Go/No-Go Decision Gates

| Gate | Sprint | Criteria | Owner |
|------|--------|----------|-------|
| **A: Foundation** | Sprint 1 | All models compile; migration tests pass; auth layer solid. | Tech Lead |
| **B: Events + Routing Beta** | Sprint 5 | Event ingestion + routing adapter live; 30+ events; routes <1s latency. | Tech Lead + Backend |
| **C: Itinerary + Packing + Collab** | Sprint 10 | CRUD complete; conflict detection works; sharing secure; >100 tests. | Tech Lead + QA |
| **D: Parity + Hardening + Canary** | Sprint 15 | Web/mobile identical; security audit passed; canary stable; rollback ready. | Tech Lead + DevOps |

---

## Success Metrics (Tracked Weekly)

| Metric | Target | Sprint Baseline | Sprint 16 Target |
|--------|--------|-----------------|-----------------|
| Test coverage | >80% | Baseline | >90% |
| Regression rate | <1% | Baseline | 0% |
| API latency (p95) | <500ms | Baseline | <200ms |
| Availability | 99.9% | N/A (pre-prod) | 99.9% |
| Event freshness | <1h stale | N/A | <1h |
| User satisfaction | >80% | N/A | >85% |
| Cost per trip | <$0.05 | N/A | <$0.05 |
| Security audit pass | 100% | N/A | 100% |

---
**Refinements & Prioritized Next Steps**

- **Short-term priorities (3 weeks):**
	- Implement `source`/`confidence` metadata across scrapers and APIs so every event/alert/forecast carries provenance and freshness.
	- Add a per-user `risk_tolerance` preference and wire it into itinerary and route scoring to let users choose safer vs. faster recommendations.
	- Add a provenance UI affordance (`Why?`) on `ItineraryItem` cards, Event cards, and Route options that displays `why`, `sources[]`, and `confidence`.
	- Add opt-in `user_health_profile` schema + migration (allergies, asthma, conditions, meds); add privacy/export/delete controls and shared-view redaction.
	- Implement `backend/services/health_guardrails.py` with deterministic rules, unit tests, and example rules (asthma+AQI, severe allergy filtering, heat/heart-condition guidance).
	- Extend scrapers/places to emit `allergen_flags` and `diet_tags` plus `source`/`confidence`; add ingestion tests and dead-letter handling for ambiguous records.
	- Wire allergen-aware filters into `/api/v1/trips/{id}/places` and the packing generator; surface `clinician_review_required` and `{why, confidence, sources[]}` in API outputs.
	- Add UI items: "Medical & Allergy" settings, `Why?` explainability affordance on Itinerary/Place/Packing items, and emergency CTA flows.
	- Schedule a clinical/legal review: capture a short sign-off workflow and document required citations/sources (CDC, WHO, EPA, local health agencies).
- **Medium-term (sprints 3–7):**
	- Add `item_health_score` into the data model and surface it in itinerary timelines and conflict checks.
	- Implement a hybrid recommendation engine (deterministic rules + ML/LLM ranker) with LLM sampling, output caching, and guardrails for safety-critical suggestions.
	- Extend routing to be multimodal, accessibility-aware, and hazard-avoidant with tradeoff UI (time vs. safety).
- **Measurement & Ops:**
	- Instrument KPIs: recommendation precision/recall, false-alert rate, packing relevance, LLM usage and hallucination rate.
	- Enforce provider budgets, caching policies, and circuit breakers; add alerts when thresholds are approached.

These refinements will be incorporated into sprint tasks, tracked as part of the Go/No-Go acceptance criteria when they materially affect safety, accuracy, or cost.

---

## Risk Backlog (Managed Sprint-to-Sprint)

1. **Schema drift** (HIGH): Preflight gates + parity validators in every sprint.
2. **Provider outage** (HIGH): Fallback provider tested in Sprint 3, rehearsed monthly.
3. **Collaboration conflicts** (MEDIUM): Sprint 8 specifically addresses; tests comprehensive.
4. **Cost overrun** (MEDIUM): Sprint 13 quota enforcement; dashboard monitored weekly.
5. **Security breach** (HIGH): Sprint 11 hardening; pen test before GA.

---

## Team Communication Plan

- **Daily**: 15-min sync (blockers, progress, handoff).
- **Weekly**: Sprint planning (Monday), retrospective + demo (Friday).
- **Bi-weekly**: Tech lead + PM review (checkpoint).
- **Monthly**: Stakeholder review (progress, risks, budget).
- **Ad-hoc**: Incident response (on-call rotation).

---

## Success Definition

✅ All 4 go/no-go gates passed.
✅ 100% feature completeness (all 5 capability domains live).
✅ >90% test coverage; zero regressions.
✅ 99.9% availability maintained throughout rollout.
✅ Cost within budget; provider usage monitored.
✅ User satisfaction >85%; positive feedback on features.
✅ Web/mobile parity verified; Golby unified.
✅ Security audit passed; compliance audit passed.

---

## Completeness Backfill Plan (ensures all partially-implemented & unplanned items are tracked)

Purpose: Close gaps found in the codebase review by converting partially-implemented or unplanned features into tracked sprint tickets with owners and acceptance criteria.

Backfill items and sprint mapping:

- Sprint 2: Forecast completeness
	- Tasks: Provider selection for UVI, add `uvi`, `dew_point`, `visibility`, `pressure`, `feels_like` to forecast schema and API; DB migration and tests.
	- Acceptance: `GET /forecast` returns UVI and the extra fields; UI surfaces UVI; tests added.

- Sprint 2–3: Place allergen flags & PlacesScraper
	- Tasks: `Place` schema add `allergen_flags`/`diet_tags`; implement `PlacesScraper` and menu extraction pipeline; wire to guardrails.
	- Acceptance: `Place` records include flags; guardrail uses them in evaluations.

- Sprint 3: Tides and coastal hazards
	- Tasks: Tide provider adapter, normalization, route-enrichment for coastal legs.
	- Acceptance: Tide data affects route scoring for coastal itineraries.

- Sprint 3–4: Disease/outbreak feeds
	- Tasks: Ingest authoritative outbreak feeds, normalize, clinician-gated advisories.
	- Acceptance: Outbreak incidents surfaced with provenance and clinician review gating when required.

- Sprint 3: Multimodal routing provider completeness
	- Tasks: Implement full set of provider implementations for walking, biking, transit, driving, ferry; multimodal tests.
	- Acceptance: Multimodal route supports hazards overlay and provider fallback tests pass.

- Sprint 4–5: Itinerary import/connectors (ICS, PNR, opt-in email parsing)
	- Tasks: Calendar ICS import, PNR parser adapters, opt-in email parser; consent/PII handling; retention/audit rules.
	- Acceptance: ICS import and manual PNR import work with consent and redaction.

- Sprint 4: Menu allergen extraction (NLP)
	- Tasks: OCR/text extraction pipeline + classifier for allergen extraction; confidence scoring and dead-letter handling.
	- Acceptance: Extracted allergens used by guardrails when confidence threshold met.

For each backfill ticket: include provider/key notes, billing impact, DB migration script + rollback, unit/integration tests, privacy impact assessment (if PII/health data), and map security checks back to `docs/expansion/RISKRADAR_EXPANSION_SECURITYPLAN.md`.

Next steps: create tracked tickets for each backfill item in the sprint tracker, assign owners, and add to the sprint planning board for the mapped sprint windows.

</parameter>