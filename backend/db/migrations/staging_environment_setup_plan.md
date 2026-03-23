# Staging Environment Setup & Testing Plan: Email Encryption Migration

## Objective
Prepare a staging environment for safe testing of email encryption migration, rollback, and monitoring procedures using dummy or anonymized data.


## Reproducible Staging Environment Setup
1. **Clone Schema Only**
	- Use mysqldump or equivalent to export schema only (no data):
	  ```sh
	  mysqldump -u <user> -p --no-data riskradar_db > schema_only.sql
	  ```
	- Create a new staging DB and import schema:
	  ```sh
	  mysql -u <user> -p -e "CREATE DATABASE riskradar_staging;"
	  mysql -u <user> -p riskradar_staging < schema_only.sql
	  ```

2. **Populate with Anonymized/Dummy Data**
	- Generate fake users using scripts or tools (e.g., Faker for Python).
	- If using a copy of production data, run an anonymization script to replace emails, names, and sensitive fields with random values.
	- Validate that no real user data remains in staging.

3. **Apply Planned Schema Changes**
	- Run migration scripts to add encrypted_email, email_iv, migration_log, etc.
	- Confirm new columns and tables exist in staging DB.

4. **Dry-Run Migration & Rollback**
	- Run migration script on staging DB; verify encrypted_email and email_iv are populated for all users.
	- Run rollback script; verify original email field is restored and encrypted columns are removed (if part of rollback).
	- Ensure both scripts are idempotent and can be safely re-run.

5. **Validate Logging & Monitoring**
	- Confirm migration_log is populated with all actions and errors.
	- Run monitoring queries and check dashboard/alerting setup.

6. **Document Test Results & Issues**
	- Record all test runs, outcomes, and any issues found in a shared doc or log file.
	- Note any edge cases, failures, or unexpected behaviors for review.

## Documentation Procedures
- Keep a step-by-step log of all staging setup actions, including commands used and outputs.
- Save anonymization scripts and test data generators in version control (if safe).
- Update this plan with any new steps or lessons learned after each dry run.
- Review all documentation with backend/security leads before production migration.

## Testing Checklist
- Migration script encrypts emails and enforces uniqueness.
- Rollback script restores original email field and removes encrypted columns.
- Migration logging records all actions and errors.
- Monitoring tools detect errors and alert as expected.
- No sensitive data is exposed in logs or test outputs.

## Notes
- Do not use real user data in staging unless anonymized.
- Review staging setup and test results with backend team before production.
- Document all procedures for future maintainers.
