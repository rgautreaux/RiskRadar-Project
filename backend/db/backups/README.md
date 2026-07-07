# Database Backup & Restore Procedures

This directory is for storing database backup files and documenting backup/restore steps for the RiskRadar MySQL/MariaDB system.

## Backup Steps
1. Use `mysqldump` to export the database:
   ```
   mysqldump -u <username> -p riskradar_db > riskradar_db_backup.sql
   ```
2. Save the backup file in this directory.

## Restore Steps
1. Use the backup file to restore the database:
   ```
   mysql -u <username> -p riskradar_db < riskradar_db_backup.sql
   ```
2. Verify all tables and data are intact.

## Notes
- Test backup and restore in a staging environment before production.
- Document each backup with date and purpose.
- Never commit sensitive backup files to version control.
