import pandas as pd

def process_reservations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorized enrichment:
      - Compute taxes (8%)
      - Compute total (fare + tax)
      - MAP: PENDING -> "PENDING", CANCELLED -> "CANCELLED", CONFIRMED -> "CONFIRMED" (normalized)
    """
    df = df.copy()

    # Ensure correct dtypes
    df["Fare"] = pd.to_numeric(df["Fare"], errors="coerce").fillna(0.0)

    tax_rate = 0.08
    df["Tax"] = (df["Fare"] * tax_rate).round(2)
    df["Total"] = (df["Fare"] + df["Tax"]).round(2)

    # Normalize status (already uppercased in loader)
    df["Status"] = df["Status"].where(df["Status"].isin(["CONFIRMED","CANCELLED","PENDING"]), "PENDING")

    return df
