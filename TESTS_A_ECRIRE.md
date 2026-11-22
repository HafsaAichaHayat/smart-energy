# Liste des tests à écrire

Les fichiers de `tests/` sont **vides** : c'est à vous de les écrire.
Cette liste est la même que celle de la fiche de TP (section « Liste détaillée des tests »).
**obl.** = obligatoire (13 tests), **bonus** = pour aller plus loin (31 tests proposés au total).

**Sécurité des identifiants :** les identifiants des capteurs ne sont pas stockés en clair. `energy_app/data/sensors.json` contient uniquement leur empreinte SHA-256 (sel + identifiant). `hash_sensor_id(sensor_id, salt)` calcule l'empreinte et `load_registry()` lit le fichier.

## Tests unitaires

### `tests/test_sensors.py` : `parse_measurement`, `hash_sensor_id`
| N° | Situation | Résultat attendu | Niveau |
|---|---|---|---|
| S1 | S3 envoie `battery` = 15 | mesure retournée (`metric` = battery, `value` = 15) | obl. |
| S2 | S1 envoie `production` = 1200 | `metric` = production, `value` = 1200 | bonus |
| S3 | identifiant inconnu `S99` | `UnknownSensorError` | obl. |
| S4 | message sans `timestamp` | `InvalidMeasurement` | bonus |
| S5 | valeur non numérique (`"abc"`) | `InvalidMeasurement` | bonus |
| S6 | deux mesures dans le même message | `InvalidMeasurement` | bonus |
| S7 | `hash_sensor_id` pour S1 (deux appels) puis pour S2 | empreinte de 64 caractères, différente de `S1`, identique entre les deux appels, différente pour S2 | bonus |

### `tests/test_energy.py` : `compute_balance`, `has_surplus`
| N° | Situation | Résultat attendu | Niveau |
|---|---|---|---|
| E1 | production 1200 W, consommation 800 W | bilan = 400, surplus vrai | obl. |
| E2 | production 300 W, consommation 900 W | bilan = -600, surplus faux | bonus |
| E3 | production négative (-100) | `ValueError` | obl. |
| E4 | consommation négative (-1) | `ValueError` | bonus |

### `tests/test_battery.py` : `validate_level`, `is_low`, `update_level`
| N° | Situation | Résultat attendu | Niveau |
|---|---|---|---|
| B1 | niveau 15 % | `is_low` vrai | obl. |
| B2 | niveau 50 %, puis 20 % (limite) | `is_low` faux dans les deux cas | bonus |
| B3 | niveau 120 %, puis -5 | `ValueError` | obl. |
| B4 | niveau 50 %, bilan +500 W pendant 1 h (capacité 5000 Wh) | nouveau niveau = 60 | bonus |
| B5 | niveau 99 %, bilan +5000 W pendant 1 h | niveau plafonné à 100 | bonus |
| B6 | niveau 5 %, bilan -2000 W pendant 1 h | niveau plancher à 0 | bonus |

### `tests/test_alerts.py` : `battery_alert`, `invalid_measurement_alert`
| N° | Situation | Résultat attendu | Niveau |
|---|---|---|---|
| A1 | niveau 15 % | alerte de type `BATTERIE_FAIBLE` | obl. |
| A2 | niveau 80 % | aucune alerte (`None`) | bonus |
| A3 | niveau 120 % | `ValueError` | obl. |
| A4 | erreur « capteur inconnu » | alerte de type `MESURE_INVALIDE` | bonus |

## Tests d'intégration : `tests/test_integration.py`
| N° | Scénario | Résultat attendu | Méthode, niveau |
|---|---|---|---|
| I1 | messages S1 (production 1200) et S2 (consommation 800) → bilan | bilan = 400 W | ascendante, obl. |
| I2 | bilan +500 W, batterie à 50 % → mise à jour du niveau | niveau = 60 | ascendante, bonus |
| I3 | message S3 avec `battery` = 15 → lecture → alerte | alerte `BATTERIE_FAIBLE` | descendante, obl. |
| I4 | message de S99 → erreur → alerte | alerte `MESURE_INVALIDE` | descendante, bonus |

## Tests de sécurité : `tests/test_security.py` (X1 à X3 obligatoires, X4 à X6 bonus)
| N° | Entrée malveillante | Résultat attendu | Niveau |
|---|---|---|---|
| X1 | identifiant falsifié : capteur `S99` | `UnknownSensorError` | obl. |
| X2 | usurpation : S1 envoie une mesure `battery` | `SensorMismatchError` | obl. |
| X3 | mesure manipulée : `battery` = 120, puis -5 | `ValueError` | obl. |
| X4 | rejeu : `ReplayGuard.check` appelé deux fois avec le même horodatage, puis avec un plus ancien | `ReplayError` | bonus |
| X5 | le hash de S3 est envoyé à la place de l'identifiant | `UnknownSensorError` | bonus |
| X6 | lecture du texte de `sensors.json` | aucun identifiant en clair (`S1`, `S2`, `S3`) | bonus |

Indice X5 : `registry = load_registry()` puis `hash_sensor_id("S3", registry["salt"])`. Indice X6 : `REGISTRY_PATH.read_text()`.

**Question de réflexion :** un attaquant qui lit `sensors.json` peut-il retrouver `S1` ? Que se passe-t-il si les identifiants sont courts et faciles à deviner ? Que faudrait-il changer (identifiants longs et aléatoires, clé secrète) ?

Pour chaque test de sécurité, écrivez en docstring : (1) la situation malveillante,
(2) le comportement attendu, (3) le résultat qui valide le test.

## Code à compléter avant certains tests

- B4 à B6 et I2 : compléter `update_level` (`battery.py`).
- A1, I3 et I4 : compléter `battery_alert` (`alerts.py`).
- X2 : ajouter la vérification capteur / mesure dans `parse_measurement` (`sensors.py`).
- X4 : compléter `ReplayGuard.check` (`sensors.py`).

Un test de sécurité qui échoue au départ est normal : il révèle une faille à corriger.

## Rappel

`pytest -v` retourne le code 5 (« aucun test collecté ») tant que les tests ne sont pas écrits.
