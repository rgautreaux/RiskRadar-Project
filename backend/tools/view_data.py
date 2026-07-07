"""View all scraped data in the database.

Run from the backend directory:
    python view_data.py
    python view_data.py --source nws
    python view_data.py --source epa
    python view_data.py --source usgs_earthquakes
    python view_data.py --full
"""

import argparse
import json

from db.database import SessionLocal
from db.models import Alert, Summary, ScrapeLog


def view_alerts(db, source_filter=None, show_full=False):
    query = db.query(Alert).order_by(Alert.created_at.desc())
    if source_filter:
        query = query.filter(Alert.source == source_filter)

    alerts = query.all()
    print(f"\n{'='*70}")
    print(f"  ALERTS ({len(alerts)} total)")
    print(f"{'='*70}")

    if not alerts:
        print("  No alerts found.")
        return

    # Group by source
    sources = {}
    for a in alerts:
        sources.setdefault(a.source, []).append(a)

    for source, items in sources.items():
        print(f"\n  --- {source.upper()} ({len(items)} alerts) ---")
        for a in items:
            print(f"  [{a.severity.upper():10s}] {a.title[:65]}")
            if show_full:
                print(f"    ID:          {a.id}")
                print(f"    Source ID:   {a.source_id}")
                print(f"    Type:        {a.alert_type}")
                if a.description:
                    print(f"    Description: {a.description[:120]}")
                if a.location_name:
                    print(f"    Location:    {a.location_name}")
                if a.latitude and a.longitude:
                    print(f"    Coords:      {a.latitude}, {a.longitude}")
                if a.event_start:
                    print(f"    Start:       {a.event_start}")
                if a.event_end:
                    print(f"    End:         {a.event_end}")
                print(f"    Fetched:     {a.fetched_at}")
                print()


def view_summaries(db):
    summaries = db.query(Summary).order_by(Summary.created_at.desc()).all()
    print(f"\n{'='*70}")
    print(f"  SUMMARIES ({len(summaries)} total)")
    print(f"{'='*70}")

    if not summaries:
        print("  No summaries generated yet.")
        return

    for s in summaries:
        print(f"\n  [{s.summary_type.upper()}] {s.title}")
        print(f"  Model: {s.model_used} | Tokens: {s.token_count} | Generated: {s.generated_at or s.created_at}")
        print(f"  {'-'*60}")
        print(f"  {s.content[:500]}")
        if len(s.content) > 500:
            print(f"  ... ({len(s.content)} chars total)")
        print()


def view_scrape_logs(db):
    logs = db.query(ScrapeLog).order_by(ScrapeLog.completed_at.desc()).limit(20).all()
    print(f"\n{'='*70}")
    print(f"  SCRAPE LOG (last 20 runs)")
    print(f"{'='*70}")

    if not logs:
        print("  No scrape logs yet.")
        return

    print(f"  {'Source':<20s} {'Status':<10s} {'Fetched':>8s} {'New':>5s} {'Time':>8s} {'When'}")
    print(f"  {'-'*80}")
    for log in logs:
        duration = f"{log.duration_ms}ms" if log.duration_ms else "?"
        print(f"  {log.source:<20s} {log.status:<10s} {log.alerts_fetched:>8d} {log.alerts_new:>5d} {duration:>8s} {log.completed_at}")
        if log.error_message:
            print(f"    ERROR: {log.error_message[:80]}")


def view_stats(db):
    alerts = db.query(Alert).all()
    print(f"\n{'='*70}")
    print(f"  DATABASE STATS")
    print(f"{'='*70}")

    # By source
    by_source = {}
    for a in alerts:
        by_source.setdefault(a.source, 0)
        by_source[a.source] += 1
    print(f"\n  Alerts by source:")
    for source, count in sorted(by_source.items()):
        print(f"    {source:<25s} {count:>5d}")

    # By severity
    by_severity = {}
    for a in alerts:
        by_severity.setdefault(a.severity, 0)
        by_severity[a.severity] += 1
    print(f"\n  Alerts by severity:")
    for sev in ["critical", "high", "moderate", "low"]:
        if sev in by_severity:
            print(f"    {sev:<25s} {by_severity[sev]:>5d}")

    # By type
    by_type = {}
    for a in alerts:
        by_type.setdefault(a.alert_type, 0)
        by_type[a.alert_type] += 1
    print(f"\n  Alerts by type:")
    for atype, count in sorted(by_type.items()):
        print(f"    {atype:<25s} {count:>5d}")

    summaries = db.query(Summary).count()
    logs = db.query(ScrapeLog).count()
    print(f"\n  Total alerts:    {len(alerts)}")
    print(f"  Total summaries: {summaries}")
    print(f"  Total scrape runs: {logs}")


def main():
    parser = argparse.ArgumentParser(description="View RiskRadar scraped data")
    parser.add_argument("--source", help="Filter alerts by source (e.g., nws, epa, usgs_earthquakes)")
    parser.add_argument("--full", action="store_true", help="Show full alert details")
    parser.add_argument("--section", choices=["alerts", "summaries", "logs", "stats", "all"],
                        default="all", help="Which section to show (default: all)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.section in ("stats", "all"):
            view_stats(db)
        if args.section in ("alerts", "all"):
            view_alerts(db, source_filter=args.source, show_full=args.full)
        if args.section in ("summaries", "all"):
            view_summaries(db)
        if args.section in ("logs", "all"):
            view_scrape_logs(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
