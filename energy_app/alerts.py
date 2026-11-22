"""Génération des alertes (module partiellement implémenté)."""

from energy_app.battery import LOW_THRESHOLD, validate_level


def battery_alert(level):
    """Retourne une alerte (dict) si la batterie est faible, sinon None.

    Format attendu de l'alerte :
        {"type": "BATTERIE_FAIBLE", "message": "Batterie faible : 15 %"}
    """
    validate_level(level)
    if level < LOW_THRESHOLD:
        return {"type": "BATTERIE_FAIBLE", "message": f"Batterie faible : {level} %"}
    return None


def invalid_measurement_alert(error):
    """Alerte générée lorsqu'une mesure reçue est invalide (fourni)."""
    return {"type": "MESURE_INVALIDE", "message": str(error)}
