# smart-energy : TP « Les tests continus dans DevOps »

Squelette du projet de gestion intelligente de l'énergie solaire.
Votre travail : **écrire les tests** (les fichiers de `tests/` sont vides),
**compléter le code marqué `TODO`** et **terminer le workflow** GitHub Actions.
Le guide `TESTS_A_ECRIRE.md` liste les 31 tests proposés (13 obligatoires, 18 bonus). La fiche du TP est dans `docs/`.

## Installation et exécution

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Ce qui est fourni / à faire

| Fichier | État | À faire |
|---|---|---|
| `energy_app/energy.py` | complet | rien (sert d'exemple) |
| `energy_app/data/sensors.json` | fourni | registre des capteurs : identifiants **hachés** (SHA-256 + sel), jamais en clair |
| `energy_app/sensors.py` | partiel | vérification d'usurpation, `ReplayGuard.check` |
| `energy_app/battery.py` | partiel | `update_level` |
| `energy_app/alerts.py` | partiel | `battery_alert` |
| `tests/test_*.py` | **vides** | écrire les tests (voir `TESTS_A_ECRIRE.md`) |
| `tests/test_security.py` | **vide** | au moins 3 tests de sécurité |
| `.github/workflows/tests.yml` | partiel | 4 `TODO` |

## Méthode conseillée

1. Lisez `TESTS_A_ECRIRE.md` et le code de `energy_app/`.
2. Écrivez un test, lancez `pytest -v`.
3. S'il échoue (par exemple usurpation, rejeu), corrigez le code correspondant.
4. Poussez sur GitHub et vérifiez le résultat du workflow dans l'onglet *Actions*.
