#!/usr/bin/env python3
"""
Script pour récupérer les données de production photovoltaïque depuis l'API SolarEdge
et les sauvegarder dans un format compatible avec le dashboard existant.
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import argparse

# Configuration par défaut
DEFAULT_CONFIG = {
    "api_key": "api_key",
    "site_id": "site_id",
    "data_dir": "data/",
    "days_to_fetch": 7
}

CONFIG_FILE = "solaredge_config.json"

def load_config():
    """Charge la configuration depuis un fichier JSON ou utilise les valeurs par défaut"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Fusionner avec la configuration par défaut
                default_config = DEFAULT_CONFIG.copy()
                default_config.update(config)
                return default_config
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de configuration: {e}")
            print("Utilisation de la configuration par défaut")
            return DEFAULT_CONFIG
    else:
        # Créer un fichier de configuration par défaut
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(f"Fichier de configuration créé: {CONFIG_FILE}")
        print("Veuillez éditer ce fichier avec vos informations SolarEdge avant de continuer")
        return DEFAULT_CONFIG

def get_solaredge_energy_data(api_key, site_id, start_date, end_date):
    """Récupère les données d'énergie depuis l'API SolarEdge"""
    base_url = "https://monitoringapi.solaredge.com"
    
    # Convertir les dates au format requis (YYYY-MM-DD)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # URL de l'API pour les données d'énergie
    url = f"{base_url}/site/{site_id}/energy?api_key={api_key}&startDate={start_date_str}&endDate={end_date_str}&timeUnit=DAY"
    
    try:
        print(f"Récupération des données depuis {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if 'energy' not in data or 'values' not in data['energy']:
            print("Aucune donnée disponible pour la période spécifiée")
            return None
            
        # Convertir en DataFrame pandas
        df = pd.DataFrame(data['energy']['values'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Renommer les colonnes pour plus de clarté
        df = df.rename(columns={
            'date': 'Date',
            'value': 'Production_kWh'
        })
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à l'API SolarEdge: {e}")
        return None
    except Exception as e:
        print(f"Erreur lors du traitement des données: {e}")
        return None

def get_solaredge_power_data(api_key, site_id, start_date, end_date):
    """Récupère les données de puissance en temps réel depuis l'API SolarEdge"""
    base_url = "https://monitoringapi.solaredge.com"
    
    # Convertir les dates au format requis
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    # URL de l'API pour les données de puissance (15 minutes d'intervalle)
    url = f"{base_url}/site/{site_id}/power?api_key={api_key}&startTime={start_date_str}&endTime={end_date_str}"
    
    try:
        print(f"Récupération des données de puissance depuis {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if 'power' not in data or 'values' not in data['power']:
            print("Aucune donnée de puissance disponible")
            return None
            
        # Convertir en DataFrame pandas
        df = pd.DataFrame(data['power']['values'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Renommer les colonnes
        df = df.rename(columns={
            'date': 'Time',
            'value': 'Production_W'
        })
        
        # Convertir les watts en kilowatts
        df['Production_kW'] = df['Production_W'] / 1000
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à l'API SolarEdge: {e}")
        return None
    except Exception as e:
        print(f"Erreur lors du traitement des données de puissance: {e}")
        return None

def save_data_to_csv(df, filename, data_dir):
    """Sauvegarde les données dans un fichier CSV"""
    try:
        # Créer le répertoire s'il n'existe pas
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Données sauvegardées dans {filepath}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier: {e}")
        return False

def create_daily_summary(df_power, date):
    """Crée un résumé quotidien des données de puissance"""
    if df_power is None or df_power.empty:
        return None
    
    # Filtrer pour la date spécifique
    date_str = date.strftime("%Y-%m-%d")
    daily_data = df_power[df_power['Time'].dt.date == pd.to_datetime(date_str).date()]
    
    if daily_data.empty:
        return None
    
    # Calculer les statistiques quotidiennes
    production_total = daily_data['Production_kW'].sum()  # Total en kWh
    production_max = daily_data['Production_kW'].max()
    production_mean = daily_data['Production_kW'].mean()
    
    # Créer un DataFrame de résumé
    summary = pd.DataFrame({
        'Date': [date_str],
        'Production_Totale_kWh': [production_total],
        'Production_Max_kW': [production_max],
        'Production_Moyenne_kW': [production_mean],
        'Nombre_Points': [len(daily_data)]
    })
    
    return summary

def main():
    """Fonction principale"""
    # Charger la configuration
    config = load_config()
    
    # Vérifier si la configuration contient des valeurs par défaut
    if config['api_key'] == DEFAULT_CONFIG['api_key'] or config['site_id'] == DEFAULT_CONFIG['site_id']:
        print("⚠️  Veuillez configurer votre clé API et ID de site dans solaredge_config.json avant de continuer")
        return
    
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Récupère les données SolarEdge')
    parser.add_argument('--days', type=int, default=config['days_to_fetch'], 
                       help='Nombre de jours de données à récupérer')
    parser.add_argument('--output', type=str, default=config['data_dir'], 
                       help='Répertoire de sortie pour les fichiers CSV')
    
    args = parser.parse_args()
    
    # Mettre à jour la configuration avec les arguments
    config['days_to_fetch'] = args.days
    config['data_dir'] = args.output
    
    print(f"🌞 Récupération des données SolarEdge pour les {config['days_to_fetch']} derniers jours")
    
    # Calculer les dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=config['days_to_fetch'])
    
    # Récupérer les données d'énergie (quotidienne)
    print("\n📊 Récupération des données d'énergie quotidienne...")
    energy_data = get_solaredge_energy_data(config['api_key'], config['site_id'], start_date, end_date)
    
    if energy_data is not None:
        # Sauvegarder les données d'énergie
        energy_filename = f"solaredge_energy_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
        save_data_to_csv(energy_data, energy_filename, config['data_dir'])
    
    # Récupérer les données de puissance (détaillées)
    print("\n⚡ Récupération des données de puissance détaillées...")
    power_data = get_solaredge_power_data(config['api_key'], config['site_id'], start_date, end_date)
    
    if power_data is not None:
        # Sauvegarder les données de puissance complètes
        power_filename = f"solaredge_power_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
        save_data_to_csv(power_data, power_filename, config['data_dir'])
        
        # Créer des résumés quotidiens
        print("\n📈 Création des résumés quotidiens...")
        current_date = start_date
        
        while current_date <= end_date:
            daily_summary = create_daily_summary(power_data, current_date)
            
            if daily_summary is not None:
                date_str = current_date.strftime("%Y%m%d")
                summary_filename = f"solaredge_daily_{date_str}.csv"
                save_data_to_csv(daily_summary, summary_filename, config['data_dir'])
            
            current_date += timedelta(days=1)
    
    print("\n✅ Opération terminée!")
    print(f"Les données ont été sauvegardées dans le répertoire: {os.path.abspath(config['data_dir'])}")

if __name__ == "__main__":
    main()
