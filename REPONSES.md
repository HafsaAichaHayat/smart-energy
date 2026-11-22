# Réponses écrites du TP

## 4.1 Rôle des modules
- **sensors.py** : reçoit le message IoT, vérifie l'identifiant (haché), la mesure autorisée et la valeur, puis renvoie `{sensor_id, metric, value, timestamp}`.
- **energy.py** : reçoit production et consommation (W) venant de `sensors.py` et renvoie le bilan (production − consommation) et l'existence d'un surplus.
- **battery.py** : reçoit le niveau (%) venant de S3 et le bilan venant de `energy.py`, valide la plage 0–100 %, détecte « batterie faible » et calcule le nouveau niveau.
- **alerts.py** : reçoit le niveau de batterie (ou une erreur de `sensors.py`) et produit une alerte `BATTERIE_FAIBLE` ou `MESURE_INVALIDE`.

Flux : `sensors → energy → battery → alerts` (et `sensors → alerts` en cas d'erreur).

## 4.3 Méthodes d'intégration
- I1, I2 : **ascendante** (modules réels assemblés de proche en proche : sensors→energy, energy→battery).
- I3, I4 : **descendante** (on part du scénario complet « message → alerte » ; les modules non concernés, par exemple energy, ne sont pas nécessaires/simulés).

## 4.4 Tableau de sécurité
| Menace | Entrée malveillante et résultat attendu (test) | La règle suffit-elle ? Pourquoi ? |
|---|---|---|
| Identifiant falsifié | Message du capteur `S99` → `UnknownSensorError` | Oui contre un identifiant inventé, mais pas contre un attaquant qui connaît un vrai identifiant (S1) : il faut en plus une authentification (clé secrète, signature). |
| Usurpation | `S1` envoie `battery` → `SensorMismatchError` | Partiellement : empêche d'envoyer la mauvaise mesure, mais S1 peut toujours envoyer de fausses valeurs de `production` si son identifiant fuit. |
| Mesure manipulée | `battery = 120` puis `-5` → `ValueError` | Non : bloque seulement les valeurs hors plage ; une fausse valeur plausible (ex. 85 au lieu de 15) passe. Il faut de la cohérence temporelle/croisée (variation maximale, comparaison avec le bilan). |
| Rejeu | Même horodatage deux fois, puis plus ancien → `ReplayError` | Partiellement : l'horodatage peut être falsifié ; il faut un horodatage signé, un nonce ou un compteur. |
| Fichier JSON lu par un attaquant | Le texte de `sensors.json` ne contient aucun identifiant en clair | Non suffisant si les identifiants sont courts (voir ci-dessous). |

## Question sur le registre haché
- Un attaquant qui lit `sensors.json` ne voit que des empreintes SHA-256 : il ne peut pas « inverser » le hash directement.
- Mais `S1`, `S2`, `S3` sont courts et prévisibles, et le sel est lui aussi dans le fichier : l'attaquant essaie `S1`, `S2`, `S3`, `S4`... (attaque par dictionnaire/force brute) et retrouve les identifiants en quelques millisecondes. Le sel empêche seulement les tables précalculées (rainbow tables), pas cette attaque.
- À changer : identifiants **longs et aléatoires** (ex. 128 bits générés avec `secrets.token_hex(16)`), un hash lent (PBKDF2, scrypt, Argon2) ou un HMAC avec une **clé secrète** stockée hors du fichier (variable d'environnement, coffre de secrets), et idéalement une authentification par signature des messages.

## 9. Question finale
Parce que les décisions énergétiques (charger/décharger la batterie, couper une charge, déclencher une alerte) s'appuient directement sur ces mesures. Un capteur falsifié ou usurpé, ou une valeur incohérente, peut faire vider ou surcharger la batterie, masquer une vraie panne, déclencher de fausses alertes, ou servir de point d'entrée à une attaque. Vérifier l'identité (qui parle ?) et la cohérence (la valeur est-elle plausible, récente, de la bonne nature ?) garantit l'intégrité des données avant toute action : on ne fait pas confiance à une donnée tant qu'elle n'est pas validée.
