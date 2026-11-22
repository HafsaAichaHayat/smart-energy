"""Tests unitaires de sensors.py (S1 à S7)."""
import pytest

from energy_app.sensors import (
    InvalidMeasurement,
    UnknownSensorError,
    hash_sensor_id,
    load_registry,
    parse_measurement,
)


def test_s1_capteur_connu_mesure_valide():                      # S1 (obl.)
    result = parse_measurement({"sensor_id": "S3", "battery": 15, "timestamp": 1718000000})
    assert result["metric"] == "battery"
    assert result["value"] == 15


def test_s2_production_valide():                                # S2 (bonus)
    result = parse_measurement({"sensor_id": "S1", "production": 1200, "timestamp": 1})
    assert result["metric"] == "production"
    assert result["value"] == 1200


def test_s3_identifiant_inconnu():                              # S3 (obl.)
    with pytest.raises(UnknownSensorError):
        parse_measurement({"sensor_id": "S99", "battery": 15, "timestamp": 1})


def test_s4_timestamp_manquant():                               # S4 (bonus)
    with pytest.raises(InvalidMeasurement):
        parse_measurement({"sensor_id": "S3", "battery": 15})


def test_s5_valeur_non_numerique():                             # S5 (bonus)
    with pytest.raises(InvalidMeasurement):
        parse_measurement({"sensor_id": "S3", "battery": "abc", "timestamp": 1})


def test_s6_deux_mesures_dans_un_message():                     # S6 (bonus)
    with pytest.raises(InvalidMeasurement):
        parse_measurement(
            {"sensor_id": "S1", "production": 100, "consumption": 50, "timestamp": 1}
        )


def test_s7_hachage():                                          # S7 (bonus)
    salt = load_registry()["salt"]
    h1a = hash_sensor_id("S1", salt)
    h1b = hash_sensor_id("S1", salt)
    h2 = hash_sensor_id("S2", salt)
    assert len(h1a) == 64
    assert h1a == h1b          # déterministe
    assert h1a != h2           # deux capteurs -> deux empreintes
