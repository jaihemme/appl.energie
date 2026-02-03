#!/usr/bin/env python3
"""
Dashboard amélioré pour visualiser les données Pi et Po jour par jour
Avec formatage de date et barres visuelles
"""

import os
import glob
import pandas as pd
from datetime import datetime, timedelta

def get_available_dates(data_dir="data/"):
    """Retourne la liste des dates disponibles sous forme de datetime"""
    csv_files = glob.glob(os.path.join(data_dir, "ts_summary_20*.csv"))
    dates = []
    
    for file in csv_files:
        # Extraire la date du nom de fichier ts_summary_YYYYMMDD.csv
        filename = os.path.basename(file)
        date_str = filename.replace("ts_summary_", "").replace(".csv", "")
        try:
            date = datetime.strptime(date_str, "%Y%m%d")
            dates.append(date)
        except ValueError:
            continue
    
    return sorted(dates)

def load_day_data(date, data_dir="data/"):
    """Charge les données pour une date donnée"""
    date_str = date.strftime("%Y%m%d")
    filename = os.path.join(data_dir, f"ts_summary_{date_str}.csv")
    
    if not os.path.exists(filename):
        return None
    
    try:
        df = pd.read_csv(filename)
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {filename}: {e}")
        return None

def format_time(time_str):
    """Formate la date au format jj.mm.aaaa hh:mm"""
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return time_str

def create_pi_bar(pi_value, max_value=12.0):
    """Crée une barre visuelle pour la valeur Pi"""
    if pd.isna(pi_value) or pi_value <= 0:
        return ""
    
    # Calculer la longueur proportionnelle (max 50 caractères)
    ratio = min(pi_value / max_value, 1.0)
    bar_length = int(ratio * 50)
    return "=" * bar_length

def display_day_data(date, df):
    """Affiche les données Pi et Po pour un jour donné"""
    if df is None or df.empty:
        print(f"\n📅 {date.strftime('%A %d %B %Y')}")
        print("❌ Aucune donnée disponible pour ce jour")
        return
    
    print(f"\n📅 {date.strftime('%A %d %B %Y')}")
    print("=" * 100)
    
    # Calculer les statistiques pour la journée
    pi_mean = df['Pi'].mean()
    po_mean = df['Po'].mean()
    pi_max = df['Pi'].max()
    po_max = df['Po'].max()
    pi_min = df['Pi'].min()
    po_min = df['Po'].min()
    
    print(f"📊 Statistiques pour le {date.strftime('%d/%m/%Y')}")
    print(f"   Pi - Moyenne: {pi_mean:.3f} kW | Max: {pi_max:.3f} kW | Min: {pi_min:.3f} kW")
    print(f"   Po - Moyenne: {po_mean:.3f} kW | Max: {po_max:.3f} kW | Min: {po_min:.3f} kW")
    print(f"   Nombre d'enregistrements: {len(df)}")
    print("-" * 100)
    
    # Afficher toutes les données avec formatage et barres visuelles
    print(f"\n📈 Toutes les données du jour:")
    print(f"{'Time':<17} {'Pi':>8} {'Po':>8} {'Pi Bar (max 12.0 kW)':<55}")
    print("-" * 100)
    
    for index, row in df.iterrows():
        formatted_time = format_time(row['Time'])
        pi_value = row['Pi']
        po_value = row['Po']
        pi_bar = create_pi_bar(pi_value)
        print(f"{formatted_time:<17} {pi_value:>8.3f} {po_value:>8.3f} [{pi_bar:<50}] {pi_value:.3f}")

def main():
    print("🚀 Dashboard de données Pi/Po - Version Améliorée")
    print("Commandes: p (précédent), n (suivant), q (quitter)")
    
    # Obtenir les dates disponibles
    available_dates = get_available_dates()
    
    if not available_dates:
        print("❌ Aucun fichier de données trouvé dans le répertoire 'data/'")
        return
    
    # Commencer avec la date la plus récente
    current_date = available_dates[-1]
    current_index = len(available_dates) - 1
    
    while True:
        # Effacer l'écran
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Charger les données pour la date actuelle
        df = load_day_data(current_date)
        
        # Afficher les données
        display_day_data(current_date, df)
        
        # Afficher les instructions de navigation
        print(f"\n🎮 Navigation: p (précédent), n (suivant), q (quitter)")
        print(f"📍 Position: {current_index + 1}/{len(available_dates)} jours disponibles")
        print(f"📅 Date actuelle: {current_date.strftime('%d/%m/%Y')}")
        
        # Attendre l'entrée utilisateur
        choice = input("\nVotre choix: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Au revoir !")
            break
        elif choice == 'p':  # Précédent
            if current_index > 0:
                current_index -= 1
                current_date = available_dates[current_index]
        elif choice == 'n':  # Suivant
            if current_index < len(available_dates) - 1:
                current_index += 1
                current_date = available_dates[current_index]
        elif choice == '':  # Entrée vide, rafraîchir
            continue
        else:
            print(f"Commande inconnue: {choice}")
            input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()