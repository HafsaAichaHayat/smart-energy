"""Outil enseignant : regénère energy_app/data/sensors.json.

Le registre ne contient que l'empreinte SHA-256 (sel + identifiant) de chaque
capteur, jamais l'identifiant en clair.
Usage : python scripts/generate_registry.py
"""
import hashlib
import json
from pathlib import Path

SALT = "smart-energy-2026"
SENSORS = {"S1": "production", "S2": "consumption", "S3": "battery"}

registry = {
    "algorithm": "sha256",
    "salt": SALT,
    "sensors": {
        hashlib.sha256((SALT + sensor_id).encode("utf-8")).hexdigest(): metric
        for sensor_id, metric in SENSORS.items()
    },
}

out = Path(__file__).resolve().parent.parent / "energy_app" / "data" / "sensors.json"
out.write_text(json.dumps(registry, indent=2), encoding="utf-8")
print(f"Registre écrit dans {out}")
