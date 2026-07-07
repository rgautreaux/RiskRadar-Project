# Schema Design Plan: Encrypted Email & Unique Constraints

## Objective
Update the `users` table to store encrypted email addresses and enforce uniqueness, supporting AES-256-GCM encryption and migration from plaintext.

## Current Schema (users table)
- id: Integer, primary key
- device_token: Text
- display_name: Text
- email: Text, unique
- password_hash: Text
- zip_code: Text
- latitude: Float

## Proposed Changes
1. **Encrypted Email Field**
   - Store encrypted email as binary or base64-encoded text.
   - Add a field for the initialization vector (IV) used in AES-GCM.
   - Example:
     - encrypted_email: Text or Binary
     - email_iv: Text or Binary

2. **Unique Constraint**
   - Enforce uniqueness on the encrypted_email field.
   - If deterministic encryption is used, uniqueness is straightforward.
   - If non-deterministic, consider storing a hash of the email for uniqueness checking.

3. **Migration Plan**
   - Add new fields to the table.
   - Migrate existing plaintext emails to encrypted format in batches.
   - Validate uniqueness and integrity after migration.

## Example Table Definition (SQLAlchemy)
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ...existing code...
    encrypted_email = Column(Text, unique=True)
    email_iv = Column(Text)
    ...existing code...
```

## Notes
- Do not remove the old email field until migration is complete and validated.
- Document the encryption and migration logic for maintainers.
- Coordinate with backend developers for integration.

## Next Steps
- Review with backend team before implementation.
- Draft migration scripts for schema changes.
- Plan for rollback and backup before migration.
