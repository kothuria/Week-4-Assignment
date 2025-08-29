import pandas as pd
from pathlib import Path

def load_reservations(csv_path: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")
    df = pd.read_csv(path, dtype={
        "PNR": "string",
        "Passenger": "string",
        "Origin": "string",
        "Destination": "string",
        "Fare": "float64",
        "Status": "string"
    })
    # Normalize columns
    expected = ["PNR","Passenger","Origin","Destination","Fare","Status"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Strip whitespace, uppercase codes
    for col in ["PNR","Passenger","Origin","Destination","Status"]:
        df[col] = df[col].astype("string").fillna("").str.strip()
    df["Origin"] = df["Origin"].str.upper()
    df["Destination"] = df["Destination"].str.upper()
    df["Status"] = df["Status"].str.upper()

    # Drop total-blank rows
    df = df.dropna(how="all")

    # De-duplicate by PNR, keep last seen
    df = df.drop_duplicates(subset=["PNR"], keep="last").reset_index(drop=True)

    return df
