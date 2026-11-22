"""Tests unitaires de energy.py (E1 à E4)."""
import pytest

from energy_app.energy import compute_balance, has_surplus


def test_e1_bilan_positif_et_surplus():                         # E1 (obl.)
    assert compute_balance(1200, 800) == 400
    assert has_surplus(1200, 800) is True


def test_e2_bilan_negatif_pas_de_surplus():                     # E2 (bonus)
    assert compute_balance(300, 900) == -600
    assert has_surplus(300, 900) is False


def test_e3_production_negative():                              # E3 (obl.)
    with pytest.raises(ValueError):
        compute_balance(-100, 500)


def test_e4_consommation_negative():                            # E4 (bonus)
    with pytest.raises(ValueError):
        compute_balance(500, -1)
