# Explication des En-têtes CSV

Ce document explique la signification de chaque colonne dans les fichiers CSV générés par le système de traitement MQTT.

## Fichier : ts_summary.csv

| En-tête | Description | Unité | Exemple |
|----------|-------------|-------|---------|
| `timestamp` | Date et heure du message au format ISO 8601 | - | `2026-01-14T10:09:40` |
| `TS` | Timestamp du résumé (format Tasmota) | - | `260114100949W` |
| `NS` | Timestamp en nanosecondes | - | `353234363435` |
| `Pi` | Puissance instantanée entrée (Input) | Watts | `0.0` |
| `Po` | Puissance instantanée sortie (Output) | Watts | `1.411` |
| `B1` | Compteur d'énergie phase 1 (B1) | kWh | `10017.763` |
| `B2` | Compteur d'énergie phase 2 (B2) | kWh | `11931.218` |
| `E1` | Énergie totale phase 1 (E1) | kWh | `15397.878` |
| `E2` | Énergie totale phase 2 (E2) | kWh | `34.25` |
| `P1i` | Puissance phase 1 entrée | Watts | `1.062` |
| `P2i` | Puissance phase 2 entrée | Watts | `0.0` |
| `P3i` | Puissance phase 3 entrée | Watts | `0.0` |
| `P1o` | Puissance phase 1 sortie | Watts | `0.0` |
| `P2o` | Puissance phase 2 sortie | Watts | `0.963` |
| `P3o` | Puissance phase 3 sortie | Watts | `0.922` |
| `I1` | Courant phase 1 | Ampères | `2.0` |
| `I2` | Courant phase 2 | Ampères | `4.0` |
| `I3` | Courant phase 3 | Ampères | `3.0` |
| `U1` | Tension phase 1 | Volts | `233.4` |
| `U2` | Tension phase 2 | Volts | `236.8` |
| `U3` | Tension phase 3 | Volts | `232.9` |

## Fichier : energie.csv

| En-tête | Description | Unité | Exemple |
|----------|-------------|-------|---------|
| `timestamp` | Date et heure arrondie à la seconde | - | `2026-01-14 10:09:41` |
| `Pi` | Moyenne de la puissance entrée pour cette seconde | Watts | `0.15` |
| `Po` | Moyenne de la puissance sortie pour cette seconde | Watts | `1.45` |
| `B1` | Moyenne du compteur B1 pour cette seconde | kWh | `10018.25` |
| `B2` | Moyenne du compteur B2 pour cette seconde | kWh | `11932.25` |
| `E1` | Moyenne de l'énergie E1 pour cette seconde | kWh | `15398.25` |
| `E2` | Moyenne de l'énergie E2 pour cette seconde | kWh | `34.35` |
| `P1i` | Moyenne de la puissance phase 1 entrée | Watts | `1.15` |
| `P2i` | Moyenne de la puissance phase 2 entrée | Watts | `0.15` |
| `P3i` | Moyenne de la puissance phase 3 entrée | Watts | `0.05` |
| `P1o` | Moyenne de la puissance phase 1 sortie | Watts | `0.05` |
| `P2o` | Moyenne de la puissance phase 2 sortie | Watts | `0.95` |
| `P3o` | Moyenne de la puissance phase 3 sortie | Watts | `0.95` |
| `I1` | Moyenne du courant phase 1 | Ampères | `2.15` |
| `I2` | Moyenne du courant phase 2 | Ampères | `4.15` |
| `I3` | Moyenne du courant phase 3 | Ampères | `3.15` |
| `U1` | Moyenne de la tension phase 1 | Volts | `233.55` |
| `U2` | Moyenne de la tension phase 2 | Volts | `236.95` |
| `U3` | Moyenne de la tension phase 3 | Volts | `233.05` |
| `count` | Nombre de mesures agrégées pour cette seconde | - | `2` |

## Légende des Abréviations

- **TS** : Timestamp (horodatage Tasmota)
- **NS** : Timestamp en nanosecondes
- **Pi** : Power Input (puissance entrée)
- **Po** : Power Output (puissance sortie)
- **B1/B2** : Compteurs d'énergie par phase
- **E1/E2** : Énergie totale par phase
- **P1i/P2i/P3i** : Puissance entrée par phase (1, 2, 3)
- **P1o/P2o/P3o** : Puissance sortie par phase (1, 2, 3)
- **I1/I2/I3** : Courant par phase (1, 2, 3)
- **U1/U2/U3** : Tension par phase (1, 2, 3)

## Notes Importantes

1. **ts_summary.csv** : Contient les valeurs brutes des résumés TS (toutes les 5 minutes)
2. **senergie.csv** : Contient les moyennes calculées pour chaque seconde
3. Le champ `count` dans second_aggregation.csv indique combien de mesures ont été agrégées
4. Toutes les valeurs numériques sont des moyennes sauf `timestamp` et `count`
5. Les valeurs manquantes ou nulles sont traitées comme 0 dans les calculs de moyenne
