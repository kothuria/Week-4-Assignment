#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from src.logging_setup import setup_logging
from src.config import Config
from src.data_loader import load_reservations
from src.validators import validate_reservations
from src.processor import process_reservations
from src.notifier import send_confirmations
from src.metrics import timer

@timer("main_run")
def main():
    parser = argparse.ArgumentParser(description="Process flight reservations.")
    parser.add_argument("--input", default="data/reservations.csv", help="Input CSV path")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run (override .env)")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size for notifications")
    parser.add_argument("--workers", type=int, default=None, help="Parallel workers for I/O")
    args = parser.parse_args()

    setup_logging()
    cfg = Config()
    if args.dry_run:
        cfg.DRY_RUN = True
    if args.batch_size:
        cfg.BATCH_SIZE = args.batch_size
    if args.workers:
        cfg.WORKERS = args.workers

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Load
    df = load_reservations(args.input)

    # 2) Validate
    valid_df, invalid_df = validate_reservations(df)
    invalid_path = out_dir / "invalid_rows.csv"
    invalid_df.to_csv(invalid_path, index=False)
    print(f"[INFO] Saved invalid rows: {invalid_path} ({len(invalid_df)})")

    # 3) Process (vectorized enrichment, no per-row loops)
    processed_df = process_reservations(valid_df)

    processed_path = out_dir / "processed.csv"
    processed_df.to_csv(processed_path, index=False)
    print(f"[INFO] Saved processed rows: {processed_path} ({len(processed_df)})")

    # 4) Notify confirmations (batched + parallel + retry + session reuse)
    confirmations = processed_df[processed_df["Status"] == "CONFIRMED"].copy()
    send_confirmations(confirmations, out_dir=out_dir, cfg=cfg)

    print("[DONE] All stages completed successfully.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Robust top-level error capture
        import logging
        logging.exception("Fatal error in main: %s", e)
        sys.exit(1)
