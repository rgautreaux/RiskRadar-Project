# RiskRadar — GDPR & CCPA Compliance Review

**Prepared by:** Noah Benoit (Security Lead)
**Date:** March 22, 2026
**Scope:** User data collection, storage, processing, and rights obligations under GDPR and CCPA

---

## Overview

RiskRadar collects personally identifiable information (PII) from users to deliver location-based environmental risk alerts. This review analyzes the current state of the application against the requirements of the General Data Protection Regulation (GDPR) and the California Consumer Privacy Act (CCPA), identifies gaps, and specifies the actions needed to achieve compliance before production deployment.

---

## Data Inventory

The following user data is currently collected and stored by RiskRadar, based on the codebase audit and Tech Stack Reference:

| Category | Data Points | Storage Location | Sensitivity |
|---|---|---|---|
| Account | Email address | `users.email` (plaintext) | HIGH — PII |
| Account | Hashed password | `users.password_hash` (bcrypt) | MEDIUM — stored safely |
| Identity | Display name | `users.display_name` (plaintext) | LOW–MEDIUM |
| Location | ZIP code, latitude, longitude | `users.zip_code`, `users.latitude`, `users.longitude` | MEDIUM — PII when combined |
| Device | Push notification token | `users.device_token` | MEDIUM — device identifier |
| Preferences | Alert type preferences, severity filter | `users.alert_types`, `users.notify_severity` | LOW |
| Behavioral | Articles read, read timestamps, reading progress | Not yet confirmed in codebase | MEDIUM |
| Environmental | Alerts and AI summaries | `alerts`, `summaries` tables | LOW — public data |

---

## GDPR Analysis

GDPR applies to any application that processes the personal data of individuals in the European Union, regardless of where the company is located. If any RiskRadar users are in the EU (or if the app is made available to EU residents), GDPR obligations apply.

### Lawful Basis for Processing (Article 6)

GDPR requires a documented lawful basis for each type of personal data processing. For RiskRadar, the most applicable basis is **consent** (the user creates an account and agrees to terms) or **legitimate interests** (delivering the safety service the user signed up for).

**Current gap:** There is no visible Terms of Service, Privacy Policy, or consent mechanism in the codebase or templates. The registration flow (`backend/templates/register.html`, `frontend/RiskRadar/app/auth/registration.tsx`) should include a consent checkbox and a link to a Privacy Policy before launch.

**Action required:** Draft a Privacy Policy and add a consent acknowledgment to the registration flow (task for team; Noah to review for compliance).

---

### Data Minimization (Article 5(1)(c))

GDPR requires that only the minimum data necessary for the stated purpose is collected.

**Assessment:** RiskRadar's data collection appears reasonably minimal for its core purpose. Location data (zip code + lat/lon) is needed to deliver local alerts. Email is needed for account identification. Push notification tokens are needed for alert delivery.

**Potential gap:** Behavioral data (articles read, read timestamps, reading progress) is listed in the Tech Stack Reference but is not confirmed in the current database schema or codebase. If this data is collected in the future, a clear justification for it must be documented.

**Action required:** Before adding behavioral tracking, confirm it serves a documented, necessary purpose and disclose it in the Privacy Policy.

---

### Right to Erasure / Right to be Forgotten (Article 17)

Users have the right to request deletion of all their personal data.

**Current gap:** There is no DELETE user endpoint in the current API (`backend/api/users.py`). The API supports GET and PUT for user data but not deletion. This means there is currently no mechanism to honor an erasure request.

**Action required:** Implement a `DELETE /users/me` endpoint (or equivalent) that removes or anonymizes all user PII. This is a task for Qui. Noah to verify that the deletion covers all relevant tables (users, any linked alert preferences, device tokens).

---

### Data Portability (Article 20)

Users have the right to receive a copy of their personal data in a portable format.

**Current gap:** There is no data export endpoint. Users cannot currently request their data in a structured, machine-readable format.

**Action required:** Implement a `GET /users/me/export` endpoint that returns all stored user data as JSON or CSV. Moderate priority — lower urgency than erasure.

---

### Security of Processing (Article 32)

GDPR requires that personal data be protected with appropriate technical measures.

**Current status:**
- Passwords: bcrypt hashing — **compliant**
- Email: plaintext storage — **non-compliant** until encryption is implemented
- JWT secret: hardcoded default fallback — **risk** (see Codebase Audit Report, Finding 3)
- HTTPS: required in production — needs confirmation it is enforced

**Action required:** Complete email encryption migration. Set a strong JWT secret before deployment. Confirm HTTPS is enforced (redirect HTTP → HTTPS) on the production server.

---

### Data Breach Notification (Article 33)

In the event of a data breach, GDPR requires notification to the supervisory authority within 72 hours and, if high risk to users, direct notification to affected individuals.

**Action required:** Draft a breach response procedure (who contacts whom, what information to include, timeline). This is a planning document — see `KEY_MANAGEMENT_PLAN.md` for the monitoring component.

---

## CCPA Analysis

CCPA applies to businesses that collect personal information from California residents and meet at least one of: (1) annual gross revenues over $25M, (2) buys/sells/receives/shares personal information of 100,000+ consumers, or (3) derives 50%+ of annual revenue from selling personal information.

As a student capstone project, RiskRadar does not currently meet these thresholds. However, designing for CCPA compliance is good practice for production readiness and demonstrates security maturity.

### Key CCPA Rights

| Right | Current Status | Gap |
|---|---|---|
| Right to Know (what data is collected) | No Privacy Policy exists | Draft and publish a Privacy Policy |
| Right to Delete | No deletion endpoint | Implement DELETE endpoint |
| Right to Opt-Out of Sale | N/A — RiskRadar does not sell user data | Document this explicitly in Privacy Policy |
| Right to Non-Discrimination | N/A — no tiered access model | No action needed |

---

## Compliance Gaps Summary

| Gap | Regulation | Severity | Owner |
|---|---|---|---|
| No Privacy Policy or consent mechanism at registration | GDPR Art. 6, CCPA | HIGH | Team; Noah to review |
| Email stored in plaintext | GDPR Art. 32 | HIGH | Qui, Rebecca (migration) |
| No user deletion endpoint | GDPR Art. 17, CCPA | HIGH | Qui |
| JWT secret has hardcoded default | GDPR Art. 32 | HIGH | Qui, Noah |
| No data export endpoint | GDPR Art. 20 | MEDIUM | Qui |
| Behavioral data collection undocumented | GDPR Art. 5 | MEDIUM | Team |
| No breach response procedure | GDPR Art. 33 | MEDIUM | Noah |
| CORS wildcard in production | GDPR Art. 32 | MEDIUM | Qui |
| No rate limiting on login | GDPR Art. 32 | MEDIUM | Qui |

---

## Recommended Compliance Roadmap

**Before production launch (required):**
1. Implement email encryption (resolves GDPR Art. 32 gap)
2. Set a strong JWT secret via `.env` (see `KEY_MANAGEMENT_PLAN.md`)
3. Implement user deletion endpoint
4. Draft and publish a Privacy Policy
5. Add consent checkbox to registration

**Shortly after launch:**
6. Implement data export endpoint
7. Restrict CORS to production domains
8. Add rate limiting on login
9. Draft breach response procedure

---

*This review was prepared as part of the RiskRadar User Security Plan. It reflects the state of the codebase as of March 22, 2026 and is intended as a planning document for the team — not legal advice.*
