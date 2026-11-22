"""Réception et vérification des mesures IoT.

Format d'un message IoT (dictionnaire Python) :
    {"sensor_id": "S3", "battery": 15, "timestamp": 1718000000}

Un message contient l'identifiant du capteur, un horodatage et UNE seule
mesure parmi : "production" (W), "consumption" (W), "battery" (%).

Sécurité : les identifiants des capteurs ne sont PAS stockés en clair.
Le registre `data/sensors.json` ne contient que leur empreinte
SHA-256 (sel + identifiant), associée à la mesure que le capteur a le droit d'envoyer.
L'application hache l'identifiant reçu puis cherche l'empreinte dans le registre.
"""
import hashlib
import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parent / "data" / "sensors.json"

METRICS = ("production", "consumption", "battery")


class InvalidMeasurement(ValueError):
    """Mesure ou message invalide."""


class UnknownSensorError(InvalidMeasurement):
    """Identifiant de capteur inconnu."""


class SensorMismatchError(InvalidMeasurement):
    """Le capteur envoie une mesure qui n'est pas la sienne (usurpation)."""


class ReplayError(InvalidMeasurement):
    """Message ancien ou rejoué."""


def load_registry(path=REGISTRY_PATH):
    """Charge le registre JSON : {"algorithm", "salt", "sensors": {empreinte: mesure}}."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def hash_sensor_id(sensor_id, salt):
    """Retourne l'empreinte SHA-256 (hexadécimale) de salt + sensor_id."""
    return hashlib.sha256((salt + sensor_id).encode("utf-8")).hexdigest()


def expected_metric(sensor_id, registry=None):
    """Retourne la mesure autorisée pour ce capteur, ou lève UnknownSensorError."""
    if registry is None:
        registry = load_registry()
    if not isinstance(sensor_id, str):
        raise UnknownSensorError(f"Capteur inconnu : {sensor_id!r}")
    digest = hash_sensor_id(sensor_id, registry["salt"])
    metric = registry["sensors"].get(digest)
    if metric is None:
        raise UnknownSensorError("Capteur inconnu : empreinte absente du registre")
    return metric


def validate_sensor_id(sensor_id, registry=None):
    """Vérifie que l'identifiant est connu. Retourne l'identifiant."""
    expected_metric(sensor_id, registry)
    return sensor_id


def parse_measurement(message, registry=None):
    """Vérifie un message IoT et retourne un dictionnaire normalisé :
    {"sensor_id": ..., "metric": ..., "value": ..., "timestamp": ...}
    """
    if not isinstance(message, dict):
        raise InvalidMeasurement("Le message doit être un dictionnaire")

    sensor_id = message.get("sensor_id")
    allowed_metric = expected_metric(sensor_id, registry)   # UnknownSensorError si inconnu

    if "timestamp" not in message:
        raise InvalidMeasurement("Horodatage manquant")

    found = [m for m in METRICS if m in message]
    if len(found) != 1:
        raise InvalidMeasurement("Le message doit contenir exactement une mesure")
    metric = found[0]

    # Anti-usurpation : le capteur ne peut envoyer que SA mesure (d'après le registre).
    if metric != allowed_metric:
        raise SensorMismatchError(
            f"Le capteur {sensor_id} n'est autorisé à envoyer que "
            f"'{allowed_metric}', pas '{metric}'"
        )

    value = message[metric]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidMeasurement(f"Valeur non numérique : {value!r}")

    return {
        "sensor_id": sensor_id,
        "metric": metric,
        "value": value,
        "timestamp": message["timestamp"],
    }


class ReplayGuard:
    """Détecte le rejeu d'anciens messages (un horodatage par capteur)."""

    def __init__(self):
        self._last_timestamp = {}

    def check(self, sensor_id, timestamp):
        """Accepte le message ou lève ReplayError s'il est rejoué."""
        last = self._last_timestamp.get(sensor_id)
        if last is not None and timestamp <= last:
            raise ReplayError(
                f"Message rejoué ou ancien pour {sensor_id} : {timestamp} <= {last}"
            )
        self._last_timestamp[sensor_id] = timestamp
