# Script de Récupération des Données SolarEdge

Ce script permet de récupérer les données de production photovoltaïque depuis l'API SolarEdge et de les sauvegarder dans un format compatible avec votre dashboard existant.

## Prérequis

Avant d'utiliser ce script, assurez-vous d'avoir installé les dépendances nécessaires :

```bash
pip install requests pandas
```

## Configuration

1. **Obtenez vos informations d'API SolarEdge** :
   - Connectez-vous à votre compte sur [https://monitoring.solaredge.com](https://monitoring.solaredge.com)
   - Allez dans "Admin" > "Site Access" > "API Access"
   - Générez une clé API et notez votre ID de site

2. **Configurez le script** :
   - Un fichier `solaredge_config.json` a été créé automatiquement
   - Éditez ce fichier avec vos informations :
     ```json
     {
         "api_key": "VOTRE_CLE_API_SOLAREDGE",
         "site_id": "VOTRE_ID_DE_SITE",
         "data_dir": "data/",
         "days_to_fetch": 7
     }
     ```

## Utilisation

### Exécution basique

```bash
python solaredge_fetcher.py
```

Cela récupérera les données des 7 derniers jours (configurable) et les sauvegardera dans le répertoire `data/`.

### Options avancées

```bash
# Récupérer les données des 30 derniers jours
python solaredge_fetcher.py --days 30

# Spécifier un répertoire de sortie différent
python solaredge_fetcher.py --output ./mes_donnees/

# Combiner les options
python solaredge_fetcher.py --days 15 --output ./solar_data/
```

## Fichiers Générés

Le script génère plusieurs types de fichiers :

1. **Données d'énergie quotidienne** :
   - Format: `solaredge_energy_YYYYMMDD_to_YYYYMMDD.csv`
   - Contient la production totale par jour en kWh

2. **Données de puissance détaillées** :
   - Format: `solaredge_power_YYYYMMDD_to_YYYYMMDD.csv`
   - Contient les données de puissance en watts et kilowatts avec un intervalle de 15 minutes

3. **Résumé quotidien** :
   - Format: `solaredge_daily_YYYYMMDD.csv`
   - Contient un résumé quotidien avec la production totale, maximale et moyenne

## Structure des Données

### Fichier d'énergie quotidienne
```
Date,Production_kWh
2023-01-01,15.25
2023-01-02,18.75
...
```

### Fichier de puissance détaillée
```
Time,Production_W,Production_kW
2023-01-01 08:00:00,1200,1.2
2023-01-01 08:15:00,1800,1.8
...
```

### Fichier de résumé quotidien
```
Date,Production_Totale_kWh,Production_Max_kW,Production_Moyenne_kW,Nombre_Points
2023-01-01,15.25,4.2,0.635,24
```

## Intégration avec le Dashboard

Pour intégrer ces données avec votre dashboard existant, vous pouvez :

1. **Modifier le dashboard** pour lire les fichiers SolarEdge
2. **Créer un script de fusion** qui combine les données existantes avec les données SolarEdge
3. **Ajouter des visualisations spécifiques** pour la production photovoltaïque

## Résolution des Problèmes

### Erreur de connexion API
- Vérifiez que votre clé API est correcte
- Assurez-vous que votre ID de site est valide
- Vérifiez votre connexion Internet

### Aucune donnée disponible
- Vérifiez que la période demandée a des données disponibles
- Assurez-vous que votre installation SolarEdge est correctement configurée

### Problèmes de permissions
- Assurez-vous que le script a les permissions d'écriture dans le répertoire de sortie
- Créez manuellement le répertoire si nécessaire

## Exemple de Planification

Pour exécuter ce script automatiquement chaque jour, vous pouvez utiliser cron (Linux/macOS) :

```bash
# Éditez votre crontab
crontab -e

# Ajoutez cette ligne pour exécuter le script tous les jours à 20h
0 20 * * * /chemin/vers/venv/bin/python /chemin/vers/solaredge_fetcher.py --days 1
```

## Support

Pour plus d'informations sur l'API SolarEdge, consultez la documentation officielle :
[https://monitoringapi.solaredge.com](https://monitoringapi.solaredge.com)