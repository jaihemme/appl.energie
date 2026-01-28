#!/usr/bin/env python3
"""
Version texte du dashboard pour visualiser les données Pi et Po
Affiche un graphique ASCII avec Pi en positif et Po en négatif
"""

import pandas as pd
import glob
import os
from datetime import datetime
import numpy as np

def format_french_date(date):
    """Formate une date en français"""
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    
    jour_semaine = jours[date.weekday()]
    jour = date.day
    mois_nom = mois[date.month - 1]
    annee = date.year
    
    return f"{jour_semaine} {jour} {mois_nom} {annee}"

def get_available_dates(data_dir="data/"):
    """Retourne la liste des dates disponibles"""
    csv_files = glob.glob(os.path.join(data_dir, "ts_summary_20*.csv"))
    dates = []
    
    for file in csv_files:
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
        df['Time'] = pd.to_datetime(df['Time'])
        return df
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def create_ascii_chart(df, date, width=60, height=20):
    """Crée un graphique ASCII avec Pi et Po"""
    if df is None or df.empty:
        return "Aucune donnée disponible"
    
    # Normaliser les données pour l'affichage
    pi_values = df['Pi'].values
    po_values = df['Po'].values
    
    # Trouver les valeurs max pour l'échelle
    max_pi = max(pi_values)
    max_po = max(po_values)
    overall_max = max(max_pi, max_po)
    
    if overall_max == 0:
        overall_max = 1
    
    # Créer le graphique
    chart = []
    
    # Ligne de titre
    chart.append(f"📊 Graphique Énergétique - {format_french_date(date)}")
    chart.append("=" * (width + 20))
    
    # Échelle verticale
    scale_steps = 5
    for i in range(scale_steps, -1, -1):
        value = (i / scale_steps) * overall_max
        line = f"{value:6.1f} │"
        chart.append(line)
    
    # Ligne de zéro
    zero_line = "      │" + "─" * width + " Zero"
    chart.append(zero_line)
    
    # Échelle négative pour Po
    for i in range(1, scale_steps + 1):
        value = (i / scale_steps) * max_po
        line = f"-{value:6.1f} │"
        chart.append(line)
    
    # Légende
    chart.append("      └" + "─" * width)
    chart.append(f"      Pi (bleu): ■  Po (rouge): ■")
    
    # Statistiques
    pi_mean = df['Pi'].mean()
    po_mean = df['Po'].mean()
    net_energy = pi_mean - po_mean
    
    stats = f"""
📈 Statistiques:
   Pi: Moyenne={pi_mean:.3f} kW, Max={max_pi:.3f} kW
   Po: Moyenne={po_mean:.3f} kW, Max={max_po:.3f} kW
   Bilan Net: {net_energy:.3f} kW
   Enregistrements: {len(df)}
"""
    
    return "\n".join(chart) + stats

def display_data_table(df, date):
    """Affiche les données sous forme de tableau"""
    if df is None or df.empty:
        return "Aucune donnée"
    
    # Sélectionner quelques lignes pour l'affichage
    display_df = df[['Time', 'Pi', 'Po']].copy()
    display_df['Time'] = display_df['Time'].dt.strftime('%H:%M')
    display_df['Pi'] = display_df['Pi'].round(3)
    display_df['Po'] = display_df['Po'].round(3)
    
    french_date_short = f"{date.day:02d}/{date.month:02d}/{date.year}"
    table = f"\n📋 Données du {french_date_short}:\n"
    table += display_df.to_string(index=False, header=True)
    
    return table

def main():
    print("🚀 Dashboard Texte - Visualisation des données Pi/Po")
    print("=" * 60)
    
    # Obtenir les dates disponibles
    available_dates = get_available_dates()
    
    if not available_dates:
        print("❌ Aucun fichier de données trouvé")
        return
    
    # Utiliser la date la plus récente
    current_date = available_dates[-1]
    
    # Charger les données
    df = load_day_data(current_date)
    
    if df is None:
        print(f"❌ Impossible de charger les données pour {current_date.strftime('%d/%m/%Y')}")
        return
    
    # Afficher les informations
    print(f"📅 Date: {format_french_date(current_date)}")
    print(f"📊 Fichier: ts_summary_{current_date.strftime('%Y%m%d')}.csv")
    print(f"📈 Nombre d'enregistrements: {len(df)}")
    print()
    
    # Afficher le graphique ASCII
    chart = create_ascii_chart(df, current_date)
    print(chart)
    
    # Afficher le tableau des données
    table = display_data_table(df, current_date)
    print(table)
    
    print(f"\n💡 Conseils:")
    print(f"   - Les barres bleues (■) représentent Pi (consommation)")
    print(f"   - Les barres rouges (■) représentent Po (production)")
    print(f"   - La ligne de zéro sépare les valeurs positives et négatives")
    print(f"   - Le bilan net montre la différence moyenne entre Pi et Po")

if __name__ == "__main__":
    main()