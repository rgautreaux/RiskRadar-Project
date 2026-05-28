# RISKRADAR_EXPANSION_OVERVIEW.md

# Plan: RiskRadar Traveler Intelligence Expansion

**Executive Summary**

This plan delivers a production-grade expansion of RiskRadar that transforms it from an environmental alert system into a comprehensive travel intelligence platform. The expansion adds five new capability domains: Event Intelligence (festivals, attractions, tours), Traffic & Travel Tracking (smart routing with hazard awareness), Interactive Itineraries (day-level activity planning), Collaborative Trip Planning (with invited users and public links), and Cross-Platform Parity (unified Golby AI assistant on web and mobile).

The approach is designed for full production maturity, not MVP shortcuts. It prioritizes schema safety, provider abstraction, security-by-design, and explicit risk mitigation across 8 phases plus a hardening layer. It targets full capability delivery in ~10–12 weeks with parallel tracks and clear go/no-go milestones.

---

**Sync Checklist (high level)**

- New capability domains: Events, Routing, Itineraries, Packing, Collaboration, Golby parity.
- Data & schema changes: `Trip`, `Itinerary`, `ItineraryItem`, `PackingList`, `TripShare`, `Place` (add `allergen_flags`, `diet_tags`, `source`, `confidence`), `user_health_profile`, `item_health_score`.
- Deterministic safety layers: `backend/services/health_guardrails.py` and guardrail checks before any LLM output.
- Provenance & explainability: attach `{why, confidence, sources[], timestamp}` to recommendations; surface `clinician_review_required` where applicable.
- Operational controls: LLM sampling/caching, provider circuit-breakers, quotas, offline route snapshots, and parity contract tests.
- UI changes: Medical & Allergy settings, `Why?` explainability view, emergency CTA, packing and itinerary UIs.
- System integration goal: every feature must read from and write to a shared traveler intelligence core so all datasets communicate as one system and Golby can orchestrate them coherently.

**Security Posture and Threat Model**

This plan does not claim to guarantee perfect safety. It defines the controls RiskRadar must implement so the new travel, collaboration, and assistant features are hardened against realistic attack paths and data-loss scenarios.

Primary threat classes to cover:

- Account takeover, session theft, credential stuffing, and brute-force attacks.
- Broken authorization, IDOR, privilege escalation, and insecure public-link sharing.
- Injection risks across SQL, HTML, CSRF, SSRF, and prompt-injection paths.
- Sensitive-data exposure through logs, caches, backups, shared views, or third-party providers.
- Supply-chain compromise through dependencies, containers, CI/CD, or scraper inputs.
- Abuse, scraping, bot traffic, rate-limit bypass, and denial-of-service attempts.
- Malicious or poisoned external data from events, places, routing, and health sources.
- Unsafe LLM behavior, tool misuse, hallucinated citations, and unsafe advice.
- Insider misuse, leaked secrets, misconfiguration, and incomplete incident recovery.

Mandatory security controls:

- Least-privilege RBAC and row-level authorization for all trip, sharing, and assistant data paths.
- TLS everywhere, service-to-service authentication, encrypted secrets, and encryption at rest for databases, backups, and sensitive fields.
- Strong session security: short-lived access tokens, refresh-token rotation, reuse detection, revocation, and secure cookie settings.
- Security headers and browser protections: strict CSP, HSTS, X-Frame-Options, CSRF defenses, and origin allowlists.
- Abuse prevention: endpoint-level rate limits, bot detection, link enumeration throttling, and anomaly alerts.
- Secure SDLC gates: threat modeling, SAST, DAST, secret scanning, dependency scanning, container/IaC scanning, and SBOM generation.
- AI safety: prompt-injection defenses, tool allowlists, citation validation, confidence thresholds, and human-review gates for high-risk recommendations.
- Auditability and recovery: immutable audit logs, alerting on sensitive actions, tested backups, restore drills, incident-response runbooks, and rollback paths.


## Core Principles

1. **API-First Design**: Features delivered via stable, contract-tested REST/GraphQL endpoints, enabling web and mobile to consume the same logic without deep coupling.
2. **Schema Safety**: All data model changes follow expand-migrate-contract patterns with rollback scripts, parity validators, and preflight gating.
3. **Provider Neutrality**: Routing, LLM, and event data sources abstracted via adapters so decisions can be deferred and vendors swapped without rework.
4. **Security-by-Default**: Authorization enforced at data access layer, sharing links are signed and time-bounded, service credentials are least-privilege and rotated, sensitive data is encrypted, and audit trails cover collaboration and assistant actions.
5. **Observable Degradation**: When external providers fail, system shifts to safe fallback modes (cached routes, risk-only advisories) with clear uncertainty messaging.
6. **Explainability**: Recommendations, alerts, and itinerary suggestions include "why" and confidence fields so users understand reasoning.

---

## Shared Traveler Intelligence Core

This section is the cohesion rule for the entire expansion. It closes the conceptual gap between the individual datasets by defining one canonical traveler context that every feature must use.

**Canonical context contract**

All features must assemble and consume a shared traveler context object that includes:
- Traveler identity, trip membership, and collaboration permissions.
- Saved preferences, health profile, allergies, risk tolerance, tone preferences, and import consent.
- Live environmental, weather, astronomy, crime, event, route, itinerary, packing, and sharing data.
- Provenance fields for every record: `source`, `confidence`, `trust_tier`, `last_seen`, `timestamp`, and timezone.
- Derived safety outputs: personalized risk score, `clinician_review_required`, route hazard score, itinerary conflict score, packing urgency, and data freshness.

**Core rules**

- Every dataset must be normalized into the shared traveler core before it can influence recommendations or UI.
- Every recommendation must cite the same underlying traveler context object, not separate feature-specific lookups.
- Every feature must publish its outputs back into the core so downstream features can reuse the same truth.
- If any critical input is stale, missing, or low-confidence, the system must degrade to a safe advisory and explain the limitation.
- The core must support both real-time lookups and cached fallback snapshots for offline or provider-failure scenarios.

**What this solves**

- Eliminates isolated datasets that cannot talk to each other.
- Prevents Golby from giving advice without the same context used by routes, itineraries, packing, and safety checks.
- Makes the environmental, crime, event, travel, astronomy, and health layers equally actionable.
- Gives the roadmap one integration contract instead of many loose feature contracts.

**Required integrations**

- Environmental risks must feed the core at full depth, including weather, air quality, pollen, tides, and astronomy.
- Crime and safety feeds must influence route safety, event attendance, lodging, and after-dark planning.
- Events, places, and lodging must be scored against the same traveler context so the user gets consistent recommendations.
- Itinerary, packing, sharing, and imports must all write back to the core so Golby can keep advising across the full trip lifecycle.
- Web and mobile must render the same core-derived recommendations and explanations.

---

## Golby Orchestration Layer

Golby is not just a chat surface. It is the strict orchestration layer that reads the shared traveler intelligence core, coordinates the feature layers, and returns the best next action.

**Golby responsibilities**

- Orchestrate the live traveler context before answering any question.
- Compare tradeoffs across weather, crime, events, routes, astronomy, itinerary, packing, and sharing.
- Turn raw data into plain-language guidance that is warm, supportive, and precise.
- Surface next-best actions such as plan, reroute, repack, reschedule, share, import, or review.
- Preserve safety rules, confidence thresholds, and clinician review gating.
- Learn from feedback, preferences, and corrections without losing safety guardrails.

**Golby operating rules**

- Golby must never bypass the shared traveler core or use conflicting feature-specific truths.
- Golby must explain why a recommendation changed whenever the core changes.
- Golby must remain the same across web and mobile, with the same guardrails, same evidence, and same persona.
- Golby must be able to orchestrate all feature domains, including the newly planned astronomy, crime, itinerary import, and route safety surfaces.
- Golby must default to safe degradation when data is sparse, stale, or contradictory.

---

## Phase Breakdown

### Phase 0: Program Setup and Architectural Guardrails (Week 1)

**Goals**: Lock success metrics, feature flags, API contracts, and release gates.

**Tasks**:
1. Define success metrics and SLOs (latency, availability, freshness, accessibility, cost budgets).
2. Establish feature flags for events, routing, recommendations, sharing, astronomy, imports, and Golby parity with remote kill-switches.
3. Define bounded domains: Alerts, Travel, Collaboration, Assistant, and the shared traveler intelligence core.
4. Lock API evolution strategy: additive changes on /api/v1; reserve /api/v2 for breaking changes.
5. Build release gate automation: preflight checks, parity validators, migration blockers, regression test gates.
6. Define the canonical traveler context contract and require every feature to read/write through it.
7. Define Golby orchestration boundaries so all advice flows through the shared core before being surfaced.

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
8. Wire the shared traveler intelligence core into the web-app contract so both surfaces consume the same traveler context and Golby orchestration results.

**Golby Intelligence Layer**:
- Make Golby the primary assistant surface for trip planning, itinerary building, packing guidance, event discovery, route advice, and feature navigation.
- Feed Golby with live RiskRadar context: active alerts, forecasts, event data, route plans, itinerary items, packing lists, collaboration state, and trip sharing permissions.
- Add an explicit user preference and memory model so Golby can learn the traveler’s style over time, including preferred tone, risk tolerance, packing habits, pace of travel, and repeated destinations.
- Use feedback signals to refine future answers: thumbs up/down, follow-up corrections, skipped suggestions, and saved recommendations should influence ranking and response style.
- Keep responses warm, friendly, and encouraging while staying source-grounded, safety-first, and transparent about uncertainty.
- Let Golby proactively advise the user: suggest itinerary changes when weather or alerts shift, recommend packing items before departure, explain why a route or activity is risky, and surface the next best action inside the app.
- Require Golby to cite the live context it used when available, and to fall back to clear uncertainty language when data is sparse or conflicting.
- Extend Golby across the newly backfilled feature set as the user's persistent guide: forecast interpretation, UV and weather nuance, allergen-aware places and meals, tides, outbreak advisories, multimodal route choices, itinerary imports, public/private sharing, and health-aware recommendations.
- Make Golby able to compare tradeoffs in plain language: safer vs. faster routes, indoor vs. outdoor activities, allergy-safe vs. higher-risk places, and when to defer to a clinician or emergency CTA.
- Require Golby to offer the next best action for every major flow: plan, reroute, repack, reschedule, share, import, or review an alert.
- Ensure Golby can explain the user's current risk score, why it changed, which live signals moved it, and what the user can do about it.
- Keep Golby friendly and supportive, but never chatty at the expense of clarity; it should act like the user's best travel companion, not just a command-driven assistant.

**Golby Orchestration Guarantees**:
- Golby must orchestrate the shared traveler intelligence core rather than assemble fragmented feature-specific answers.
- Golby must prefer the highest-confidence combined context across sources and explicitly call out conflicts between datasets.
- Golby must use the same orchestration rules on web and mobile so the experience is consistent everywhere.
- Golby must be able to coordinate route, itinerary, packing, event, sharing, import, astronomy, and safety decisions in one response.

**Golby Advice Principles**:
- Lead with the safest, most useful recommendation first.
- Explain why the advice matters using live RiskRadar context.
- Separate facts, confidence, and next steps so users can act quickly.
- Adapt tone and detail to the traveler’s preferences and past feedback.
- Ask a clarifying question only when it materially improves the answer.
- When a feature is newly added or partially inferred, Golby must state uncertainty plainly and point users to the underlying source or settings screen.

**Golby Feature Coverage**:
- Risk scoring: explain the personalized risk score, what moved it, and how users can adjust it.
- Maps: describe interactive maps, route overlays, hazards, closures, and safer alternatives.
- Itineraries: build, explain, and revise day-by-day plans using live alerts, weather, and events.
- Packing: generate packing guidance tied to itinerary, weather, risk, and destination context.
- Events and places: recommend activities and venues with provenance, confidence, and allergy/health suitability.
- Sharing and collaboration: help users invite collaborators, manage permissions, and understand who can see what.
- Imports: help users bring in trips from supported sources and explain what was imported.
- Health and safety: explain when a clinician review, emergency CTA, or safer alternative is required.
- Astronomy: explain sunrise and sunset, moonrise and moonset, current moon phase, moon illumination, next full moon, and notable events such as supermoons or blood moons.

---
**Refinements For Accuracy & UX**

- **Provenance & Confidence:** standardize metadata fields (`source`, `confidence`, `trust_tier`, `last_seen`) for all external data (events, alerts, forecasts). Always attach this metadata to recommendations so users can inspect where advice came from and how fresh it is.
- **User Risk Controls:** surface a per-user `risk_tolerance` setting that adjusts itinerary and routing scoring (safer ↔ faster). Use it to tune recommendation aggressiveness and notify users when their preferences would suppress otherwise relevant items.
- **Item Health & Explainability:** add an `item_health_score` for `ItineraryItem` and other recommendations; attach a compact explainability object `{why, confidence, sources[], timestamp}` to every recommendation, itinerary item, route option, and packing suggestion.
- **Hybrid Recommendation Stack:** combine deterministic rules (activity→items, safety guardrails) with ML/LLM ranking for personalization. Use LLMs sparingly (sampling + caching) and require human review or higher-confidence thresholds for medical/safety-critical advice.
- **UX & Collaboration Enhancements:** progressive disclosure with a short summary + a `Why?` view; one-tap safety fixes (auto-resolve conflicts); offline edits with background sync and simple conflict resolution UI; collaborative presence indicators and per-change comments.
- **Operational & Cost Controls:** sample and cache LLM outputs, enforce provider budgets, circuit-breaker for external providers, and cached degraded-mode fallbacks annotated with uncertainty language.

These refinements prioritize user trust, clarity, and safety while keeping operational costs and provider risk manageable. They are reflected in the Roadmap's prioritized next steps and sprint tasks.

**Differentiators & Competitive Advantages**

- **Medical‑aware travel advice**: opt‑in, auditable health profiles + deterministic guardrails with clinician review for any prescriptive advice (differentiates from generic travel apps).
- **Provenance‑first recommendations**: every recommendation includes `source`, `confidence`, `trust_tier`, `last_seen` and a `{why, confidence, sources[], timestamp}` explainability object.
- **Actionable assistant (Golby)**: not just suggestions — one‑tap bookings, reroutes, emergency CTAs, and collaborative actions with clear safety tradeoffs shown.
- **Operational cost & model governance**: LLM sampling/caching, hallucination monitoring, guardrail metrics, and a model‑ops cadence to keep reliability high and costs bounded.
- **Human‑in‑the‑loop safety ops**: small triage team and clinician workflows to review flagged cases and continuously improve deterministic rules.
- **Offline‑first resilience**: route snapshots, cached alerts, and local maps so travelers remain safe without connectivity.
- **Astronomy-aware planning**: sunrise, sunset, and moon-phase context to support safe timing, night travel, photography, outdoor events, and tide-adjacent planning.

These capabilities position RiskRadar as a safety‑centric travel intelligence platform that blends deterministic public‑safety rules, verified data provenance, and action‑oriented assistant features.

**Health & Allergy Safety**

Add an opt-in `user_health_profile` (allergies, asthma, chronic conditions, relevant medications) with explicit consent, export/delete controls, and minimal retention. Implement a deterministic health guardrail layer (`backend/services/health_guardrails.py`) that runs before ML/LLM outputs to enforce safety rules and block or flag high-risk advice. Example guardrail rules:
- Asthma + AQI > 150 → mark outdoor exertion as unsafe; recommend N95 and indoor alternatives.
- Severe peanut/nut allergy → filter Places and menu items with `allergen_flags.contains_nuts`; mark exposures as high-risk and require manual verification.
- Heart condition + heat advisory → advise reduced exertion, show nearest medical facility, and surface emergency CTA.

Requirements:
- Scrapers and `Place` schema must include `allergen_flags`, `diet_tags`, `confidence`, and `source` provenance fields so recommendations can be traced and filtered.
- All medical/allergy guidance must include an explainability object `{why, confidence, sources[], timestamp}` and a `clinician_review_required` flag when deterministic rules mark output high-risk.
- LLMs may only be used for phrasing/explanations when guardrails permit; LLM outputs must include citation tokens and be suppressed below configured confidence thresholds.
- UI: provide a "Medical & Allergy" settings UI (opt-in), a `Why?` explainability view on itinerary/place/packing cards, and a prominent emergency CTA when severe risks are detected.
- Privacy: redact health fields in shared/public views, encrypt health data at rest, and expose export/delete endpoints.

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
- Perform feature-by-feature threat modeling using STRIDE and maintain a living risk register with explicit owners and due dates.
- Require security sign-off before rollout of events, routing, itineraries, sharing, packing, or assistant changes.
- Implement strict CORS allowlist (specific origins, not wildcard).
- Add endpoint-level rate limiting (not just auth endpoints): 100 req/min per user for routes, 50 for recommendations.
- Add abuse detection: repeated failed authorization attempts, unusual API patterns.
- Implement token rotation: JWT refresh tokens, logout invalidation.
- Secret hygiene: rotate LLM API keys monthly, use HashiCorp Vault or equivalent.
- Add MFA for privileged/admin/support roles and step-up authentication for risky actions like link creation, share changes, and health-profile edits.
- Enforce browser protections: CSP, HSTS, X-Content-Type-Options, CSRF tokens, and clickjacking defenses.
- Add detection for credential stuffing, session hijacking, link enumeration, scraping, and rapid request bursts.
- Harden AI calls: tool allowlists, prompt-injection filters, output citation checks, and a hard stop for low-confidence or policy-violating responses.
- Protect supply chain: pin dependencies, generate SBOMs, scan dependencies/containers/IaC in CI, and block releases on critical findings.
- Add WAF/bot mitigation and basic DDoS throttling in front of public endpoints.

**Data Privacy (Weeks 4–10)**:
- Minimize retention: delete collaboration audit logs after 1 year.
- Share link tokens encrypted at rest.
- Encrypt sensitive health, identity, and collaboration metadata at rest and in backups using managed keys with rotation.
- Shared-view redaction: hide sensitive health conditions, device tokens from viewers.
- Separate public, collaborator, and owner views so shared APIs never leak private fields by default.
- GDPR/CCPA compliance: user data export, deletion, opt-out audit.
- Add secure deletion verification and document backup retention so deleted records are not reintroduced inadvertently.

**Reliability (Weeks 4–14)**:
- Implement retries with exponential backoff for external APIs.
- Circuit breaker pattern: fail open to degraded mode after 3 failures.
- Idempotency keys for mutations (prevent double-posts).
- Dead-letter handling for failed event ingestion.
- Back up databases before every migration and rehearse restore/rollback in staging.
- Add incident-response runbooks for provider compromise, leaked tokens, data exfiltration, and unsafe assistant behavior.

**Observability (Weeks 5–14)**:
- Structured logging: JSON logs with request ID, user ID, trace ID.
- Distributed tracing: instrument scraper, recommendation engine, routing calls.
- Metrics: event ingestion rate, recommendation latency p50/p95/p99, share link usage.
- Alerting: high error rates, SLO violations, cost overruns.
- Security metrics: auth failures, authorization denials, link-enumeration attempts, token revocations, guardrail triggers, and suspicious provider responses.
- Redact secrets and health data from logs by default, with explicit allowlists for any exceptional diagnostic access.

**Cost Governance (Weeks 6–14)**:
- Provider request budgets: stop routing calls if monthly quota exceeded.
- Caching: route snapshots (7d), event lists (1h), forecast (4h).
- Sampling: LLM recommendation calls only for 20% of traffic initially, then ramp.
- Dashboard: per-feature spend visibility.
- Add cost-abuse controls for automated scraping, repeated route recomputation, and public-link brute-force traffic.

**Rollout Strategy (Weeks 13–14)**:
- Canary releases: 5% → 25% → 50% → 100% over 1 week.
- Feature flags enable per-feature rollout independently.
- Predefined rollback triggers: error rate >5%, p95 latency >2s, cost spike >20%.
- Post-release runbook: validation checks, alerting configuration.
- Require an external penetration test or red-team review before any full production rollout.

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
- Security scans are clean for critical/high findings before release.
- Penetration-test findings are triaged and remediated before rollout beyond canary.
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
- Deploy all integrated features (Golby, risk scoring, interactive map, forecast, settings) to both web and mobile through the shared RiskRadar backend; enforce contract/parity tests, feature flags, and coordinated rollouts so both platforms expose the same useful capabilities and behavior.
- Expand the web-app feature matrix to include the personalized risk score, interactive maps with route overlays, forecast/risk explanation, itinerary planning, packing guidance, trip sharing, health/allergy settings, and import flows.
- Ensure the web app and mobile app both surface the same recommendations, warnings, confidence values, and `Why?` explainability panels for every feature.
- Make Golby the first-line guide in both surfaces so the user experience feels consistent whether the traveler is on web or mobile.

**Additional Integrations (Local Safety & Services)**:

The expansion will also add three locally-focused data domains to improve traveler situational awareness and planning. Each will be ingested via scrapers, normalized into shared schemas, surfaced via trip-scoped APIs, and subject to the same cross-platform parity and CI contract testing described above (see docs/PARITY_CHECKLIST.md).

---

## Completeness Backfill: Partially-Implemented & Previously-Unplanned Features

Summary: convert partially implemented items and previously unplanned items into explicit tracked engineering tasks with owners, sprint targets, acceptance criteria, and security/privacy checklists.

1. Forecast: UV Index (UVI) + extended meteorological fields
   - What: add `uvi`, `dew_point`, `visibility`, `pressure`, `feels_like` to forecast schema and API; persist `forecast.uvi` in DB.
   - Steps: provider selection (OpenWeather paid tier or alternate), DB migration + rollback, API update (`backend/api/forecast.py`), tests, UI surface.
   - Owner: Forecast subteam. Target sprint: Sprint 2. Acceptance: UVI and fields present in `GET /forecast`, tests and docs updated.

2. Place-level allergen flags & menu extraction
   - What: implement `Place.allergen_flags`, `diet_tags`; add `PlacesScraper` and menu extraction pipeline (structured + fallback text/OCR) and confidence scoring.
   - Steps: schema migration, scraper adapters, NLP/OCR pipeline, guardrail integration, dead-letter handling.
   - Owner: Scrapers + Backend. Target sprint: Sprint 2–3. Acceptance: `Place` rows include `allergen_flags` used by `health_guardrails`.

3. Tides & coastal hazards
   - What: add tide provider adapter (NOAA or vendor), surface coastal tide risk to trip safety APIs and route enrichment.
   - Owner: Routing/Weather. Target sprint: Sprint 3. Acceptance: tide data appears for coastal itineraries and affects route scoring.

4. Disease/outbreak feeds
   - What: ingest authoritative outbreak feeds (CDC/HealthMap), normalize severity, add `clinician_review_required` gating for sensitive advisories.
   - Owner: Data Partnerships + Backend. Target sprint: Sprint 3–4. Acceptance: outbreak incidents visible with provenance and gating.

5. Multimodal routing provider completeness
   - What: implement `backend/services/routing_adapter.py` providers for walking, biking, transit, driving, ferry; provider metadata and cost controls; multimodal tests.
   - Owner: Routing subteam. Target sprint: Sprint 3. Acceptance: multi-modal route responses with hazard overlays and fallback tests.

6. Import/connectors for itineraries (PNR, calendar, optional email)
   - What: calendar ICS import, manual PNR import adapters, and an opt-in email parser for itinerary extraction; consent, retention, audit requirements enforced.
   - Owner: Integrations + Privacy. Target sprint: Sprint 4–5. Acceptance: ICS import and manual PNR import with consent flows and redaction.

7. Place menu allergen extraction (NLP)
   - What: OCR/text extraction + classifier to extract ingredient/allergen mentions from menus; attach confidence and surface to guardrails.
   - Owner: Data + LLM team. Target sprint: Sprint 4. Acceptance: extracted allergens above confidence threshold applied in guardrails.

8. Additional weather/sensor fields & fusion
   - What: ingest and normalize dew point, pressure, visibility; use them in route/guardrail evaluations (e.g., fog/visibility hazards).
   - Owner: Forecast team. Target sprint: Sprint 2. Acceptance: fields available in API and used in tests.

Requirements for each backfill task: provider selection note, billing/keys plan, DB migration script + rollback, unit/integration tests, privacy impact assessment (if PII/health data involved), and mapping to `RISKRADAR_EXPANSION_SECURITYPLAN.md` security checks.

These tasks are mirrored in the sprint roadmap to ensure tracked tickets with owners and acceptance criteria.

1. **Crime & Safety Scraper**

   Tasks:
   - Implement `CrimeScraper` extending the scraper base class to ingest crime history and active crime alerts (police blotters, public crime datasets, community reports).
   - Normalize incidents into a `CrimeIncident` schema (type, severity, timestamp, location, source, confidence).
   - Provide trip-scoped and route-overlay APIs to surface nearby incidents and aggregated safety scores by area.
   - Quarantine low-confidence/community-sourced reports and surface with clear uncertainty language.

   Key Files:
   - `backend/scrapers/crime_scraper.py` (new)
   - `backend/db/models.py` (add `CrimeIncident`, `CrimeAreaScore` tables)
   - `backend/api/safety.py` (new endpoints)
   - `backend/tests/test_crime_scraper.py`, `test_safety_apis.py`

   Verification:
   - Scraper normalizes representative payloads without errors.
   - Trip and route overlays return incidents within requested geometry and time window.
   - Confidence scoring separates verified vs. community-sourced reports.

   Risk Controls:
   - Label community-sourced or low-confidence incidents prominently.
   - Rate-limit and quarantine ambiguous sources; provide appeals workflow for disputed records.

2. **Food Recommendations (Places) Scraper**

   Tasks:
   - Add scrapers to ingest restaurants, grocery stores, markets, and essential services (Yelp, Google Places, OpenStreetMap, local directories).
   - Normalize into a `Place` schema (name, category, cuisine tags, hours, diet tags, allergy flags, rating, review_count, location, source).
   - Add personalization layer that filters and ranks by user food preferences, allergies, and dietary restrictions.
   - Surface per-trip/place recommendations with distance, travel time, risk overlay (safety), and review context.

   Key Files:
   - `backend/scrapers/places_scraper.py` (new)
   - `backend/db/models.py` (add `Place`, `PlaceReview` tables)
   - `backend/api/places.py` (new endpoints)
   - `backend/tests/test_places_scraper.py`, `test_places_ranking.py`

   Verification:
   - Place ingestion normalizes core fields and deduplicates cross-sourced entries.
   - Recommendations respect user dietary filters and allergy exclusions.
   - Ratings and review counts included in ranking signals.

   Risk Controls:
   - Avoid medical/advisory claims; include uncertainty and source attribution for reviews.
   - Respect provider TOS and rate limits; cache responses and honor opt-outs.

3. **Hotel & Lodging Recommendations Scraper**

   Tasks:
   - Ingest lodging inventory (hotels, hostels, B&Bs, short-term rentals) from public APIs and directories.
   - Normalize into `Lodging` schema (name, type, price_range, amenities, rating, safety_score, location, source).
   - Integrate area safety signals (from `CrimeIncident`/`CrimeAreaScore`), user preferences, and reviews into ranking and trust signals.
   - Expose trip-scoped lodging recommendations with booking links (where permitted), cancellation policy highlights, and safety notes.

   Key Files:
   - `backend/scrapers/lodging_scraper.py` (new)
   - `backend/db/models.py` (add `Lodging`, `LodgingAmenity` tables)
   - `backend/api/lodging.py` (new endpoints)
   - `backend/tests/test_lodging_scraper.py`, `test_lodging_ranking.py`

   Verification:
   - Lodging results include safety-aware ranking and clearly attributed review data.
   - Recommendations surface cancellation and booking-relevant metadata when available.

   Risk Controls:
   - Do not surface unverified listings as 'recommended'—require minimum review_count/confidence.
   - Apply area-level safety flags and allow users to filter out high-risk zones.


---

## Next Steps

1. **Approval & Kickoff**: Review plan with stakeholders; gain sign-off on scope and timeline.
2. **Team Allocation**: Assign engineers to Tracks A–D; establish stand-ups.
3. **Phase 0 Execution**: Finalize SLOs, feature flags, release gates in Week 1.
4. **Phase 1 Sprint**: Begin schema design and authorization layer (Week 2).
5. **Ongoing**: Weekly progress reviews; monthly risk reviews; go/no-go gates at milestones.

</parameter>