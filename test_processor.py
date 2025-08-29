import pandas as pd
from src.processor import process_reservations

def test_process_reservations():
    df = pd.DataFrame([
        {"PNR":"ABC123","Passenger":"John","Origin":"DEL","Destination":"BOM","Fare":100.0,"Status":"CONFIRMED"},
    ])
    out = process_reservations(df)
    assert "Tax" in out.columns and "Total" in out.columns
    assert round(float(out.loc[0,"Tax"]), 2) == 8.00
    assert round(float(out.loc[0,"Total"]), 2) == 108.00
    assert out.loc[0,"Status"] == "CONFIRMED"
