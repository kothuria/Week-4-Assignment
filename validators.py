import pandas as pd
import re

IATA_RE = re.compile(r"^[A-Z]{3}$")

def validate_reservations(df: pd.DataFrame):
    """Return (valid_df, invalid_df) with reason column for invalid."""
    df = df.copy()
    reasons = []

    # Vectorized checks
    is_blank_passenger = df["Passenger"].fillna("").str.len() == 0
    invalid_origin = ~df["Origin"].fillna("").str.match(IATA_RE)
    invalid_dest = ~df["Destination"].fillna("").str.match(IATA_RE)
    same_airport = df["Origin"] == df["Destination"]
    negative_fare = df["Fare"].fillna(-1) < 0
    invalid_status = ~df["Status"].isin(["CONFIRMED","CANCELLED","PENDING"])

    reason_series = (
        is_blank_passenger.map({True: "blank Passenger", False:""}) + "|" +
        invalid_origin.map({True: "invalid Origin", False:""}) + "|" +
        invalid_dest.map({True: "invalid Destination", False:""}) + "|" +
        same_airport.map({True: "same Origin/Destination", False:""}) + "|" +
        negative_fare.map({True: "negative Fare", False:""}) + "|" +
        invalid_status.map({True: "invalid Status", False:""})
    ).str.strip("|").str.replace(r"\|{2,}", "|", regex=True)

    df["Reason"] = reason_series.replace("", pd.NA)
    invalid_df = df[df["Reason"].notna()].copy()
    valid_df = df[df["Reason"].isna()].copy().drop(columns=["Reason"], errors="ignore")
    invalid_df = invalid_df.reset_index(drop=True)
    valid_df = valid_df.reset_index(drop=True)
    return valid_df, invalid_df
