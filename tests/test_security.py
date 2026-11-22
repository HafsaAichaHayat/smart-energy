"""Tests de sécurité (X1 à X6)."""
import json

import pytest

from energy_app.battery import validate_level
from energy_app.sensors import (
    REGISTRY_PATH,
    ReplayError,
    ReplayGuard,
    SensorMismatchError,
    UnknownSensorError,
    hash_sensor_id,
    load_registry,
    parse_measurement,
)


def test_x1_identifiant_falsifie():                             # X1 (obl.)
    with pytest.raises(UnknownSensorError):
        parse_measurement({"sensor_id": "S99", "battery": 50, "timestamp": 1})


def test_x2_usurpation_s1_envoie_battery():                     # X2 (obl.)
    with pytest.raises(SensorMismatchError):
        parse_measurement({"sensor_id": "S1", "battery": 50, "timestamp": 1})


@pytest.mark.parametrize("level", [120, -5])                    # X3 (obl.)
def test_x3_mesure_manipulee(level):
    with pytest.raises(ValueError):
        validate_level(level)


def test_x4_rejeu():                                            # X4 (bonus)
    guard = ReplayGuard()
    guard.check("S3", 100)                       # premier message : accepté
    with pytest.raises(ReplayError):
        guard.check("S3", 100)                   # même horodatage : rejoué
    with pytest.raises(ReplayError):
        guard.check("S3", 50)                    # horodatage plus ancien


def test_x5_hash_envoye_a_la_place_de_l_identifiant():          # X5 (bonus)
    salt = load_registry()["salt"]
    digest_s3 = hash_sensor_id("S3", salt)
    with pytest.raises(UnknownSensorError):
        parse_measurement({"sensor_id": digest_s3, "battery": 50, "timestamp": 1})


def test_x6_aucun_identifiant_en_clair_dans_le_json():          # X6 (bonus)
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    for sensor_id in ("S1", "S2", "S3"):
        assert f'"{sensor_id}"' not in text
    json.loads(text)                             # le fichier reste du JSON valide
