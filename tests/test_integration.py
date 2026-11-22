"""Tests d'intégration (I1 à I4)."""
import pytest

from energy_app.alerts import battery_alert, invalid_measurement_alert
from energy_app.battery import update_level
from energy_app.energy import compute_balance
from energy_app.sensors import InvalidMeasurement, parse_measurement


def test_i1_messages_vers_bilan():
    """I1 (obl.) - ASCENDANTE : sensors -> energy."""
    prod = parse_measurement({"sensor_id": "S1", "production": 1200, "timestamp": 1})
    cons = parse_measurement({"sensor_id": "S2", "consumption": 800, "timestamp": 1})
    assert compute_balance(prod["value"], cons["value"]) == 400


def test_i2_bilan_vers_batterie():
    """I2 (bonus) - ASCENDANTE : energy -> battery."""
    balance = compute_balance(1200, 700)           # +500 W
    assert update_level(50, balance) == pytest.approx(60)


def test_i3_message_batterie_faible_vers_alerte():
    """I3 (obl.) - DESCENDANTE : scénario complet message -> lecture -> alerte."""
    message = {"sensor_id": "S3", "battery": 15, "timestamp": 1718000000}
    measure = parse_measurement(message)
    alert = battery_alert(measure["value"])
    assert alert["type"] == "BATTERIE_FAIBLE"


def test_i4_capteur_inconnu_vers_alerte():
    """I4 (bonus) - DESCENDANTE : message S99 -> erreur -> alerte."""
    try:
        parse_measurement({"sensor_id": "S99", "battery": 50, "timestamp": 1})
    except InvalidMeasurement as err:
        alert = invalid_measurement_alert(err)
    else:
        pytest.fail("Une erreur était attendue")
    assert alert["type"] == "MESURE_INVALIDE"
