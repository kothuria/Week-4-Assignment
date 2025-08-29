import pandas as pd
from src.validators import validate_reservations

def test_validate_reservations():
    df = pd.DataFrame([
        {"PNR":"ABC123","Passenger":"John","Origin":"DEL","Destination":"BOM","Fare":100.0,"Status":"CONFIRMED"},
        {"PNR":"XYZ789","Passenger":"","Origin":"DEL","Destination":"DEL","Fare":-5,"Status":"BAD"},
    ])
    valid, invalid = validate_reservations(df)
    assert len(valid) == 1
    assert len(invalid) == 1
    assert "blank Passenger" in invalid.loc[0,"Reason"] or "same Origin/Destination" in invalid.loc[0,"Reason"]
