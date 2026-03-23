## Additional Technical Details & Best Practices

To further guarantee safety and robustness, incorporate these recommendations:

1. **Encryption Algorithm Details**
	- Use AES-256-GCM for email encryption (authenticated encryption).
	- Generate a unique initialization vector (IV) for each email; store IV securely alongside the encrypted email.

2. **Key Management**
	- Use a dedicated secrets manager (e.g., AWS Secrets Manager, Azure Key Vault) for production.
	- Rotate keys periodically and document recovery procedures.
	- Limit access to keys via role-based access control.

3. **Password Hashing Details**
	- Use bcrypt or argon2 with a strong, unique salt for each password.
	- Set a high work factor (cost parameter) to resist brute-force attacks.
	- Never use MD5, SHA1, or unsalted hashes.

4. **Migration Safety**
	- Validate encrypted emails and hashed passwords after migration (e.g., test login for migrated users).
	- Keep old data until new format is confirmed working.

5. **Error Handling**
	- Handle decryption failures gracefully (log and alert, do not crash).
	- Provide clear error messages for authentication failures.

6. **Audit Logging**
	- Log access to sensitive operations (encryption, decryption, password changes).
	- Monitor for suspicious activity.

7. **Documentation**
	- Document encryption/hashing logic, key management, and migration steps for future maintainers.

8. **Compliance**
	- Ensure the solution meets all relevant legal and regulatory requirements (GDPR, CCPA, etc.).

By following these technical details and best practices, the team can ensure a safe, compliant, and future-proof implementation of email and password encryption.
# USER_SECURITY_PLAN.md

## RiskRadar User Security Plan: Email & Password Encryption
---

## Session Update: Security Planning, Migration, and Staging (March 19, 2026)

### Summary of Changes
This session focused on preparing the RiskRadar project for secure email encryption and password hashing migration. All preparatory and planning tasks that are safe to execute independently were completed, including:
- Database backup and restore setup
- Codebase audit for email/password storage
- Schema design and documentation
- Drafting migration and rollback scripts
- Migration logging plan
- Monitoring/logging tool setup
- Staging environment setup and testing plan

These steps were implemented to ensure that all future migration and integration work can proceed safely, with minimal risk to the codebase or overlap with other teammates. Each task was documented and linked below for easy navigation and reference.

### Navigation & Reference: New Files Created

- [backend/db/migrations/email_encryption_schema_plan.md](../backend/db/migrations/email_encryption_schema_plan.md)
	- **Purpose:** Outlines the proposed schema changes for encrypted email and unique constraints.
	- **What it does:** Details table modifications, migration steps, and integration notes.
	- **Why needed:** Provides a clear, reviewed plan for secure schema changes, reducing risk during implementation.
	- **Contribution:** Ensures all team members understand and agree on the schema before changes are made, improving user data safety.

- [backend/db/migrations/draft_email_encryption_migration.py](../backend/db/migrations/draft_email_encryption_migration.py)
	- **Purpose:** Draft migration script for encrypting emails and enforcing unique constraints.
	- **What it does:** Pseudocode for adding new columns, encrypting emails, and validating uniqueness.
	- **Why needed:** Allows safe review and iteration of migration logic before execution.
	- **Contribution:** Prevents accidental data loss or corruption by ensuring migration is fully planned and tested.

- [backend/db/migrations/draft_email_encryption_rollback.py](../backend/db/migrations/draft_email_encryption_rollback.py)
	- **Purpose:** Draft rollback script for reverting the email encryption migration.
	- **What it does:** Pseudocode for restoring the original email field and removing encrypted columns.
	- **Why needed:** Ensures a safe path to revert changes if issues arise during migration.
	- **Contribution:** Provides a safety net, reducing risk of permanent data loss.

- [backend/db/migrations/migration_logging_plan.md](../backend/db/migrations/migration_logging_plan.md)
	- **Purpose:** Plan for logging all migration actions and errors.
	- **What it does:** Specifies requirements, example schema, and logging logic for traceability.
	- **Why needed:** Enables auditing and troubleshooting of migration steps.
	- **Contribution:** Improves accountability and error recovery during migration.

- [backend/db/migrations/monitoring_logging_setup_plan.md](../backend/db/migrations/monitoring_logging_setup_plan.md)
	- **Purpose:** Plan for monitoring and logging tool setup during migration.
	- **What it does:** Details requirements, tool options, and example queries for tracking migration progress and anomalies.
	- **Why needed:** Ensures issues are detected and addressed quickly during and after migration.
	- **Contribution:** Enhances post-deployment safety and operational visibility.

- [backend/db/migrations/staging_environment_setup_plan.md](../backend/db/migrations/staging_environment_setup_plan.md)
	- **Purpose:** Plan for setting up and testing a staging environment for migration.
	- **What it does:** Outlines steps for preparing a safe staging environment, testing migration/rollback scripts, and validating monitoring tools.
	- **Why needed:** Allows all migration logic to be safely tested before production.
	- **Contribution:** Reduces risk of production outages or data loss by validating all changes in a controlled environment.

### Why These Changes Were Needed
These changes were implemented to ensure that all future work on email encryption and password hashing can proceed with maximum safety, transparency, and auditability. By documenting every step, preparing rollback and monitoring plans, and validating in staging, the team can avoid common pitfalls and ensure a smooth, secure transition.
---

### Schema Design & Documentation
For details on the planned schema changes for encrypted email and unique constraints, see:
- [backend/db/migrations/email_encryption_schema_plan.md](../backend/db/migrations/email_encryption_schema_plan.md)

This file outlines the proposed table modifications, migration steps, and integration notes to guide safe implementation and future review.
---

### Codebase Audit Results: Email & Password Storage
**Investigation conducted by Rebecca Gautreaux (Database Administrator)**

The following files and code regions were identified as handling user email and password storage, processing, and authentication:

- **backend/db/models.py**: The `User` model defines the `email` and `password_hash` fields, storing user credentials in the database.
- **backend/api/users.py**: Handles user registration and login. Checks email uniqueness, hashes passwords, verifies credentials, and stores new users.
- **auth/security.py** (referenced): Implements password hashing and verification logic used during registration and login.

These regions are the primary locations for email and password handling. Any changes to encryption, hashing, or migration logic should be coordinated with these files to ensure security and prevent regressions.

No code changes were made during this audit; this was a purely investigative step to inform future implementation and risk prevention.

### Objective
Enhance the security and privacy of RiskRadar users by encrypting email addresses and securely hashing passwords in the database, following best practices and compliance requirements.

---


### 1. Analysis & Preparation
**Assigned:** Noah Benoit (Security Lead), Rebecca Gautreaux (Database Administrator)
- **Review SecurityDocs:** Analyze recommendations, compliance requirements (GDPR, CCPA), and encryption standards from `/SecurityDocs`. *(Noah)*
- **Audit Codebase:** Identify all locations where user emails and passwords are stored, processed, or transmitted. *(Rebecca, Noah)*

**Reasoning:** Ensures the plan aligns with industry standards and project-specific requirements, and avoids missing any critical code paths.

---


### 2. Email Encryption Implementation
**Assigned:** Qui Huynh (Backend Developer), Noah Benoit (Security Lead), Rebecca Gautreaux (Database Administrator)
- **Encryption Method:** Use AES symmetric encryption for email addresses, with secure key management (environment variables or secrets manager). *(Qui, Noah)*
- **Key Management:** Store encryption keys securely, never hard-coded. *(Noah)*
- **Model Update:** Modify user model to store encrypted emails. *(Qui, Rebecca)*
- **Logic Update:** Implement email encryption/decryption in authentication utilities. *(Qui)*
- **Migration:** Convert existing plaintext emails to encrypted format via migration scripts. *(Rebecca, Qui)*

**Email Uniqueness Requirement:**
	- Enforce that each email is unique in the database. *(Rebecca)*
	- Only one RiskRadar account is permitted per email address. *(Qui, Rebecca)*
	- Registration and update logic must reject duplicate emails, even after encryption. *(Qui)*
	- Database schema must maintain a unique constraint on the email field (encrypted or plaintext). *(Rebecca)*

**Reasoning:** Protects personally identifiable information (PII) from exposure in case of database compromise. AES is a proven, efficient standard for symmetric encryption.

---


### 3. Password Hashing Implementation
**Assigned:** Qui Huynh (Backend Developer), Noah Benoit (Security Lead)
- **Hashing Method:** Use bcrypt or argon2 for password hashing (not reversible encryption). *(Qui, Noah)*
- **Model Update:** Ensure password field stores only hashed values. *(Qui)*
- **Logic Update:** Update registration and authentication flows to use secure hashing. *(Qui)*

**Reasoning:** Passwords must never be stored in a reversible format. Hashing with salt prevents brute-force and rainbow table attacks.

---


### 4. Integration & Testing
**Assigned:** Qui Huynh (Backend Developer), Ben Manuel (Frontend Developer), Celeste George (Frontend Developer), Rebecca Gautreaux (Database Administrator)
- **Update Tests:** Modify and add tests to validate encrypted email and hashed password handling. *(Qui, Ben, Celeste)*
- **Run Full Suite:** Ensure all backend/frontend tests pass, confirming no regressions or conflicts. *(Qui, Ben, Celeste, Rebecca)*
- **Frontend Validation:** Ensure decrypted emails are displayed securely where needed. *(Ben, Celeste)*

**Reasoning:** Maintains project integrity and functionality, preventing disruption to existing features.

---


### 5. Compliance & Further Considerations
**Assigned:** Noah Benoit (Security Lead), Rebecca Gautreaux (Database Administrator)
- **Compliance:** Ensure GDPR/CCPA requirements are met (right to erasure, data minimization, etc.). *(Noah)*
- **Email Search:** Note that encrypted emails cannot be searched directly; consider deterministic encryption if search is required. *(Noah, Rebecca)*
- **Key Rotation:** Plan for periodic key rotation and secure backup. *(Noah, Rebecca)*

**Reasoning:** Legal compliance and operational security are critical for user trust and project longevity.

---

### How This Improves RiskRadar
- **Protects User Privacy:** Encrypts sensitive data, reducing risk of exposure.
- **Mitigates Breach Impact:** Compromised database yields unusable data without keys.
- **Strengthens Authentication:** Secure password storage prevents account takeover.
- **Ensures Compliance:** Aligns with legal and industry standards.
- **Preserves Functionality:** Careful integration avoids breaking existing features or tests.


## Precautions & Risk Prevention Strategies

To ensure the integrity of the codebase and minimize risks during implementation, follow these additional precautions:


1. **Backup All Data** *(Rebecca Gautreaux)*
	- Create a full backup of the database before migration.
	- Test restoring from backup to ensure recovery is possible.

2. **Incremental Migration** *(Rebecca Gautreaux, Qui Huynh)*
	- Migrate emails and passwords in small batches.
	- Validate each batch before proceeding.

3. **Comprehensive Testing** *(Qui Huynh, Ben Manuel, Celeste George)*
	- Expand test coverage for user registration, login, retrieval, and update flows.
	- Add tests for edge cases and run tests after every change.

4. **Staging Environment** *(Rebecca Gautreaux, Noah Benoit)*
	- Apply changes in a staging/test environment before production.
	- Use real or anonymized data to simulate migration and usage.

5. **Code Reviews** *(Noah Benoit, Qui Huynh, Rebecca Gautreaux)*
	- Have multiple team members review migration scripts and code changes.
	- Use automated linting and static analysis tools.

6. **Key Management** *(Noah Benoit)*
	- Store encryption keys securely (environment variables, secrets manager).
	- Never hard-code keys or commit them to version control.
	- Document key rotation and recovery procedures.

7. **Migration Logging** *(Rebecca Gautreaux)*
	- Log all migration actions and errors for traceability.
	- Alert on any failed or partial migrations.

8. **User Communication** *(Noah Benoit)*
	- Inform users of upcoming changes and provide support for post-migration issues.

9. **Rollback Plan** *(Rebecca Gautreaux)*
	- Prepare scripts and procedures to revert changes if needed.
	- Test rollback in staging before production.

10. **Monitor Post-Deployment** *(Rebecca Gautreaux, Noah Benoit)*
	 - Monitor logs and user activity for anomalies after deployment.
	 - Respond quickly to any issues.

### Risk Prevention Summary Table

| Risk Factor                | Prevention Strategy                |
|----------------------------|------------------------------------|
| Data loss/corruption       | Backup, incremental migration, rollback plan |
| Code integration bugs      | Staging environment, code reviews, comprehensive testing |
| Key management mistakes    | Secure storage, documented procedures, never hard-code |
| Undetected regressions     | Expanded test coverage, frequent test runs |
| User disruption            | User communication, support, monitoring |

By following these strategies, the team can avoid common pitfalls and ensure a smooth, secure transition to encrypted email and hashed password storage.
### Summary
This plan provides a clear, actionable roadmap to secure user emails and passwords in RiskRadar, leveraging best practices and compliance insights from `/SecurityDocs`. It ensures user safety, privacy, and project integrity without disrupting current functionality.
