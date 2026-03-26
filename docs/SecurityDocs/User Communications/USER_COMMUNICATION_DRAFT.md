# RiskRadar — User Communication Drafts

**Prepared by:** Noah Benoit (Security Lead)
**Date:** March 22, 2026
**Purpose:** Draft communications to inform RiskRadar users of upcoming security improvements to email and account data handling

---

## Communication 1 — Pre-Migration Notice (Send ~1 week before migration)

**Channel:** In-app banner / push notification / email
**Audience:** All registered RiskRadar users
**Tone:** Informative, reassuring

---

**Subject:** We're upgrading how we protect your account

**Body:**

We're making an important security improvement to RiskRadar.

Starting [DATE], we will be encrypting your email address in our database. This means that even if our database were ever accessed without authorization, your email address would be protected.

**What this means for you:**

- You don't need to do anything. The upgrade happens automatically.
- Your login credentials will continue to work exactly as they do today.
- You may be briefly logged out and asked to sign in again after the upgrade is complete.

This change is part of our ongoing commitment to keeping your personal information safe.

If you have questions or notice any issues after [DATE], please contact us at [SUPPORT EMAIL].

Thank you for using RiskRadar.

— The RiskRadar Team

---

## Communication 2 — Post-Migration Confirmation (Send within 24 hours after migration)

**Channel:** In-app banner / push notification
**Audience:** All registered RiskRadar users
**Tone:** Brief, positive

---

**Subject:** Your account security has been upgraded

**Body:**

The RiskRadar security upgrade is complete. Your email address is now encrypted in our database.

If you were logged out during the upgrade, please sign in again — your account and all your preferences are intact.

Questions? Contact us at [SUPPORT EMAIL].

— The RiskRadar Team

---

## Communication 3 — If a User Reports a Login Issue Post-Migration

**Channel:** Support reply
**Audience:** Individual user who reported a problem
**Tone:** Helpful, apologetic

---

**Subject:** Re: Login issue — RiskRadar support

Hi [NAME],

Thanks for reaching out. We recently completed a security upgrade to RiskRadar, and in rare cases some users have reported trouble signing in afterward.

Here are a few steps to resolve the issue:

1. Make sure you're using the email address you originally registered with.
2. If you've forgotten your password, use the "Forgot password" option on the login screen.
3. If the issue persists, reply to this message with the email address associated with your account and we'll look into it directly.

We apologize for the inconvenience and appreciate your patience.

— The RiskRadar Support Team

---

## Communication 4 — Privacy Policy Introduction (Send when Privacy Policy is published)

**Channel:** In-app notification
**Audience:** All registered users
**Tone:** Transparent, professional

---

**Subject:** RiskRadar Privacy Policy — what we collect and why

**Body:**

We've published our Privacy Policy, which explains exactly what personal information RiskRadar collects, how we use it, and your rights regarding your data.

Here's a quick summary:

- We collect your email, display name, and location (ZIP code / coordinates) to provide personalized local alerts.
- We store your alert preferences and notification settings.
- We do not sell your data to third parties.
- You can request deletion of your account and all associated data at any time by contacting [SUPPORT EMAIL].

Read the full Privacy Policy at: [LINK]

If you have any questions or concerns, please reach out to us.

— The RiskRadar Team

---

## Communication 5 — Data Breach Notification Template (Emergency Use Only)

**Channel:** Email (direct to affected users)
**Audience:** Users whose data may have been exposed
**Tone:** Urgent, transparent, apologetic
**Note:** This template should only be sent after consulting with team leadership and legal counsel. Timing must comply with GDPR Art. 33 (notify within 72 hours of discovery).

---

**Subject:** Important security notice regarding your RiskRadar account

Dear [NAME],

We are writing to inform you of a security incident that may have affected your RiskRadar account.

**What happened:** On [DATE], we discovered that [brief, factual description of the incident — e.g., "unauthorized access to our database was detected"].

**What information was involved:** [List of affected data — e.g., "Email addresses stored in encrypted form. Passwords were not affected — they are stored as one-way hashes and cannot be reversed."]

**What we have done:** We immediately [describe response — e.g., "took the affected system offline, rotated all encryption keys, and notified the appropriate authorities"].

**What you should do:**
- Be alert to any suspicious emails claiming to be from RiskRadar.
- If you use the same password on other websites, we recommend changing it there as a precaution.
- Contact us at [SUPPORT EMAIL] if you notice any unusual activity.

We sincerely apologize for this incident and are committed to protecting your information. We will provide updates as our investigation continues.

— The RiskRadar Team

---

## Notes for Sending

- Replace all `[DATE]`, `[NAME]`, `[SUPPORT EMAIL]`, and `[LINK]` placeholders before sending.
- Communications 1 and 2 should be coordinated with the migration timeline set by Rebecca and Qui.
- Communication 4 should be sent only after the Privacy Policy has been reviewed and approved by the team.
- Communication 5 should never be sent without team and legal review first.

---

*Prepared as part of the RiskRadar User Security Plan. Last updated March 22, 2026.*
