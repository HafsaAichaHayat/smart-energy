"""Calcul production / consommation (module fourni complet comme exemple)."""


def validate_power(value, name="puissance"):
    """Une puissance (W) est un nombre positif ou nul."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} doit être un nombre")
    if value < 0:
        raise ValueError(f"{name} ne peut pas être négative : {value}")
    return value


def compute_balance(production, consumption):
    """Bilan énergétique en watts : production - consommation."""
    validate_power(production, "production")
    validate_power(consumption, "consommation")
    return production - consumption


def has_surplus(production, consumption):
    """Vrai si la production dépasse la consommation (surplus -> batterie)."""
    return compute_balance(production, consumption) > 0
