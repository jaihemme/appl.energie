# Système de Traitement MQTT pour Données Énergétiques

Ce projet implémente un système de traitement des données MQTT provenant d'un capteur Tasmota, avec deux traitements séparés :

## Fonctionnalités

### 1. Traitement des Résumés TS (Toutes les 5 minutes)
- **Fichier de sortie** : `ts_summary_<aaaammjj>_<hhmm>.csv`
- **Contenu** : Messages contenant l'attribut `TS` dans `z_data`
- **Format** : Toutes les valeurs brutes du message
- **Fréquence** : Écriture immédiate à la réception

### 2. Agrégation des Données par Seconde
- **Fichier de sortie** : `energie_<aaaammjj>_<hhmm>.csv`
- **Contenu** : Messages individuels (sans attribut `TS`)
- **Format** : Les valeurs sont cumulés dans une ligne par seconde + compteur
- **Fréquence** : Écriture périodique toutes les minutes + à l'arrêt

## Structure des Fichiers CSV

Le timestamp `<aaaammjj>` correspond au lancement du script.

### `ts_summary_<aaaammjj>.csv`
```
Time,TS,NS,Pi,Po,B1,B2,E1,E2,P1i,P2i,P3i,P1o,P2o,P3o,I1,I2,I3,U1,U2,U3
```

### `energie_<aaaammjj>.csv`
```
Time,Pi,Po,B1,B2,E1,E2,P1i,P2i,P3i,P1o,P2o,P3o,I1,I2,I3,U1,U2,U3,count
```

## Installation

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install paho-mqtt
```

## Utilisation

### Lancer le traitement MQTT
```bash
# Mode normal
nohup python mqttToCsv.py &

# Mode verbose (pour le debug)
nohup python mqttToCsv.py -v &
```

### Arrêt du programme
Le programme s'arrête automatiquement au changement de jour. L'idée est de le relancer en boucle ce qui va créer à chaque fois deux nouveaux fichiers.

### Arrêter le programme
Appuyez sur `Ctrl+C` pour arrêter proprement ou 'killall mqttToCsv.py' si le script a été lancé avec nohup.
Les données agrégées restantes seront écrites avant l'arrêt.

## Configuration

Modifiez les paramètres dans `mqttToCsv.py` :

```python
# Configuration MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "tele/tasmota_EB7D9F/SENSOR"
MQTT_USER = "DVES_USER"
MQTT_PASSWORD = ""

# Fichiers de sortie
TS_CSV_FILE = "ts_summary.csv"
AGGREGATION_CSV_FILE = "energie.csv"
```

# Debug

Le programme supporte maintenant un mode verbose qui peut être activé via la ligne de commande :

```bash
python mqttToCsv.py -v
# ou
python mqttToCsv.py --verbose
```

Vous pouvez aussi obtenir de l'aide sur les options disponibles :

```bash
python mqttToCsv.py --help
```

Cela affichera toutes les options disponibles avec leur description.

## Exemples de Données

### Message TS (Résumé 5 minutes)
```json
{
  "Time": "2026-01-14T10:09:40",
  "z": {
    "TS": "260114100949W",
    "NS": 353234363435,
    "Pi": 0.0,
    "Po": 1.411,
    "B1": 10017.763,
    "B2": 11931.218,
    "E1": 15397.878,
    "E2": 34.25,
    "P1i": 1.062,
    "P2i": 0.0,
    "P3i": 0.0,
    "P1o": 0.0,
    "P2o": 0.963,
    "P3o": 0.922,
    "I1": 2.0,
    "I2": 4.0,
    "I3": 3.0,
    "U1": 233.4,
    "U2": 236.8,
    "U3": 232.9
  }
}
```

### Message Individuel (À cumuler par seconde)
```json
{
  "Time": "2026-01-14T10:09:41",
  "z": {
    "attribut": valeur
  }
}
```
Les attributs sont les mêmes que ceux livrés par "TS", mais toujours envoyés un par un.
## Tests

Un script de test est disponible pour vérifier le fonctionnement :

```bash
python test_data_processing.py
```

Ce script génère :
- `test_ts_summary.csv` - Exemple de résumé TS
- `test_second_aggregation.csv` - Exemple d'agrégation par seconde

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   MQTT Broker                   │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│               mqttToCsv.py                      │
│                                                 │
│  ┌─────────────────┐       ┌─────────────────┐  │
│  │  TS Detection   │       │  Cumuls par     │  │
│  │  (TS in z_data) │       │  seconde        │  │
│  └─────────────────┘       └─────────────────┘  │
│           │                         │           │
│           ▼                         ▼           │
│  ┌─────────────────┐       ┌─────────────────┐  │
│  │  Write to       │       │  Aggregate by   │  │
│  │  ts_summary.csv │       │  time_key       │  │
│  └─────────────────┘       └─────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│               CSV Files                         │
│                                                 │
│  ts_summary.csv               energie.csv       │
└─────────────────────────────────────────────────┘
```

## Dépendances

- Python 3.7+
- paho-mqtt
- datetime
- csv
- threading

## Auteur

Ce système a été développé pour traiter les données énergétiques provenant de capteurs Tasmota via MQTT, avec une séparation claire entre les résumés périodiques et les données temps réel cumulés par seconde.
