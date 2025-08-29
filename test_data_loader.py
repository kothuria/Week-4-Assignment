import pandas as pd
from src.data_loader import load_reservations
from pathlib import Path

def test_load_reservations(tmp_path):
    p = tmp_path / "r.csv"
    p.write_text("PNR,Passenger,Origin,Destination,Fare,Status\nABC123,John,DEL,BOM,100.0,CONFIRMED\n")
    df = load_reservations(str(p))
    assert list(df.columns) == ["PNR","Passenger","Origin","Destination","Fare","Status"]
    assert len(df) == 1
    assert df.loc[0, "Origin"] == "DEL"
    assert df.loc[0, "Status"] == "CONFIRMED"
