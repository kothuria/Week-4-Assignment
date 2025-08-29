#!/usr/bin/env python3
import argparse
import random
import string
from faker import Faker
import pandas as pd
from pathlib import Path

IATA = [
    "ATL","PEK","DXB","LAX","HND","LHR","ORD","HKG","PVG","CDG",
    "DFW","AMS","FRA","CAN","IST","JFK","SIN","DEN","ICN","BKK",
    "DEL","BOM","MAA","BLR","HYD","CCU","MUC","SYD","MEL","SFO",
]

def rand_pnr(n=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def maybe_blank(value: str, rate: float) -> str:
    return "" if random.random() < rate else value

def maybe_invalid_iata(code: str, rate: float) -> str:
    if random.random() < rate:
        # produce invalid codes (lengths other than 3, or numbers)
        choices = ["XX", "123", "TOO", "LONG", "!!", "A1B"]
        return random.choice(choices)
    return code

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic flight reservations CSV.")
    parser.add_argument("rows", nargs="?", type=int, default=200, help="Number of reservations")
    parser.add_argument("--out", default="data/reservations.csv", help="Output CSV path")
    parser.add_argument("--blank-rate", type=float, default=0.03, help="Rate of blank passenger names")
    parser.add_argument("--dup-rate", type=float, default=0.02, help="Rate of duplicate PNRs")
    parser.add_argument("--invalid-iata-rate", type=float, default=0.02, help="Rate of invalid IATA codes")
    args = parser.parse_args()

    fake = Faker()
    rows = []
    pnrs = set()

    for _ in range(args.rows):
        pnr = rand_pnr()
        # Inject duplicates on purpose
        if random.random() < args.dup_rate and pnrs:
            pnr = random.choice(list(pnrs))
        pnrs.add(pnr)

        passenger = maybe_blank(fake.name(), args.blank_rate)
        origin = maybe_invalid_iata(random.choice(IATA), args.invalid_iata_rate)
        dest = maybe_invalid_iata(random.choice(IATA), args.invalid_iata_rate)
        # sometimes make origin == destination to test validation
        if random.random() < 0.02:
            dest = origin
        fare = round(random.uniform(49.0, 899.0), 2)
        status = random.choices(
            ["CONFIRMED", "CANCELLED", "PENDING"],
            weights=[0.7, 0.1, 0.2],
            k=1
        )[0]
        rows.append({
            "PNR": pnr,
            "Passenger": passenger,
            "Origin": origin,
            "Destination": dest,
            "Fare": fare,
            "Status": status
        })

    df = pd.DataFrame(rows)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")

if __name__ == "__main__":
    main()
