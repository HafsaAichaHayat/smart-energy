"""Tests unitaires de battery.py (B1 à B6)."""
import pytest

from energy_app.battery import is_low, update_level, validate_level


def test_b1_niveau_15_est_faible():                             # B1 (obl.)
    assert is_low(15) is True


@pytest.mark.parametrize("level", [50, 20])                     # B2 (bonus)
def test_b2_niveau_50_et_limite_20_non_faibles(level):
    assert is_low(level) is False


@pytest.mark.parametrize("level", [120, -5])                    # B3 (obl.)
def test_b3_niveau_hors_limites(level):
    with pytest.raises(ValueError):
        validate_level(level)


def test_b4_charge_normale():                                   # B4 (bonus)
    # +500 W pendant 1 h = 500 Wh = 10 % de 5000 Wh
    assert update_level(50, 500, duration_h=1, capacity_wh=5000) == pytest.approx(60)


def test_b5_plafond_100():                                      # B5 (bonus)
    assert update_level(99, 5000, duration_h=1, capacity_wh=5000) == 100


def test_b6_plancher_0():                                       # B6 (bonus)
    assert update_level(5, -2000, duration_h=1, capacity_wh=5000) == 0
