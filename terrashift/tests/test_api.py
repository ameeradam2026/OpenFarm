from datetime import date
import pytest
from terrashift.services.nasa_power import fetch_daily

def test_invalid_coordinates_rejected_before_network():
    with pytest.raises(ValueError):
        fetch_daily(91, 0, date(2025,1,1), date(2025,1,2))

def test_invalid_date_range_rejected_before_network():
    with pytest.raises(ValueError):
        fetch_daily(0, 0, date(2025,1,2), date(2025,1,1))
