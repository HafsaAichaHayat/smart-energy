"""Tests unitaires de alerts.py (A1 à A4)."""
import pytest

from energy_app.alerts import battery_alert, invalid_measurement_alert
from energy_app.sensors import UnknownSensorError


def test_a1_batterie_faible_genere_alerte():                    # A1 (obl.)
    alert = battery_alert(15)
    assert alert["type"] == "BATTERIE_FAIBLE"


def test_a2_batterie_ok_pas_d_alerte():                        # A2 (bonus)
    assert battery_alert(80) is None


def test_a3_niveau_invalide():                                  # A3 (obl.)
    with pytest.raises(ValueError):
        battery_alert(120)


def test_a4_alerte_mesure_invalide():                           # A4 (bonus)
    alert = invalid_measurement_alert(UnknownSensorError("Capteur inconnu"))
    assert alert["type"] == "MESURE_INVALIDE"
