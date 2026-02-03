#!/usr/bin/env python3
"""
Dashboard Flask pour visualiser graphiquement les données Pi et Po jour par jour
Avec navigation entre les jours disponibles
"""

from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob
from datetime import datetime

app = Flask(__name__)

# Configuration
DATA_DIR = "data/"

def get_available_dates():
    """Retourne la liste des dates disponibles sous forme de datetime"""
    csv_files = glob.glob(os.path.join(DATA_DIR, "ts_summary_20*.csv"))
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

def load_day_data(date):
    """Charge les données pour une date donnée"""
    date_str = date.strftime("%Y%m%d")
    filename = os.path.join(DATA_DIR, f"ts_summary_{date_str}.csv")
    
    if not os.path.exists(filename):
        return None
    
    try:
        df = pd.read_csv(filename)
        # Convertir la colonne Time en datetime pour un meilleur affichage
        df['Time'] = pd.to_datetime(df['Time'])
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {filename}: {e}")
        return None

def load_solaredge_data(date):
    """Charge les données SolarEdge pour une date donnée"""
    date_str = date.strftime("%Y%m%d")
    filename = os.path.join(DATA_DIR, f"solaredge_power_{date_str}.csv")
    
    # Essayer aussi le format de fichier alternatif
    if not os.path.exists(filename):
        filename = os.path.join(DATA_DIR, f"solaredge_daily_{date_str}.csv")
    
    if not os.path.exists(filename):
        # Essayer de trouver un fichier qui contient cette date
        pattern = os.path.join(DATA_DIR, f"solaredge_power_*{date_str}*")
        files = glob.glob(pattern)
        if files:
            filename = files[0]
        else:
            return None
    
    try:
        df = pd.read_csv(filename)
        
        # Vérifier si le fichier contient les bonnes colonnes
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'])
        elif 'Date' in df.columns:
            df['Time'] = pd.to_datetime(df['Date'])
            # Si c'est un fichier quotidien, créer des intervalles de 15 minutes
            if len(df) == 1:
                # Créer un DataFrame avec des intervalles de 15 minutes
                full_day = pd.date_range(
                    start=df['Time'].iloc[0].replace(hour=0, minute=0, second=0),
                    end=df['Time'].iloc[0].replace(hour=23, minute=45, second=0),
                    freq='15min'
                )
                df_full = pd.DataFrame({'Time': full_day})
                
                # Remplir avec la production moyenne (approximation)
                total_production = df['Production_kWh'].iloc[0] if 'Production_kWh' in df.columns else 0
                avg_power = total_production / 24  # Approximation
                df_full['Production_kW'] = avg_power
                df_full['Production_W'] = avg_power * 1000
                return df_full
        
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier SolarEdge {filename}: {e}")
        return None

def merge_data_with_solaredge(main_df, solaredge_df):
    """Fusionne les données principales avec les données SolarEdge"""
    if solaredge_df is None or solaredge_df.empty:
        return main_df
    
    # Assurer que les deux DataFrames ont des colonnes Time compatibles
    if 'Time' not in solaredge_df.columns:
        return main_df
    
    # Fusionner les données sur la colonne Time (la plus proche)
    merged_df = pd.merge_asof(
        main_df.sort_values('Time'),
        solaredge_df.sort_values('Time'),
        on='Time',
        direction='nearest',
        tolerance=pd.Timedelta('15min')
    )
    
    return merged_df

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

def create_plot(df, date, has_solaredge=False):
    """Crée un graphique Plotly avec les flux énergétiques détaillés"""
    if df is None or df.empty:
        return None
    
    # Créer un graphique simple
    fig = go.Figure()
    
    # Si des données SolarEdge sont disponibles, afficher les flux énergétiques détaillés
    if has_solaredge and 'Production_kW' in df.columns and 'Po' in df.columns:
        # Calculer les différents flux
        df['PV_to_grid'] = df['Po']  # Vers le réseau
        df['PV_to_home'] = df['Production_kW'] - df['Po']  # Vers la maison
        df['Grid_to_home'] = df['Pi']  # Depuis le réseau
        
        # Partie POSITIVE (Production)
        # 1. Production PV totale
        fig.add_trace(go.Bar(
            x=df['Time'],
            y=df['Production_kW'],
            name='Production PV Totale',
            marker_color='gold',
            hovertemplate='<b>Production PV</b>: %{y:.3f} kW<br><extra></extra>',
            opacity=0.7
        ))
        
        # 2. Vers le réseau (Po)
        fig.add_trace(go.Bar(
            x=df['Time'],
            y=df['PV_to_grid'],
            name='PV → Réseau',
            marker_color='lightgreen',
            hovertemplate='<b>PV → Réseau</b>: %{y:.3f} kW<br><extra></extra>',
            opacity=0.9
        ))
        
        # 3. Vers la maison
        fig.add_trace(go.Bar(
            x=df['Time'],
            y=df['PV_to_home'],
            name='PV → Maison',
            marker_color='orange',
            hovertemplate='<b>PV → Maison</b>: %{y:.3f} kW<br><extra></extra>',
            opacity=0.9
        ))
        
        # Partie NÉGATIVE (Consommation)
        # 4. Depuis le réseau (Pi)
        fig.add_trace(go.Bar(
            x=df['Time'],
            y=[-x for x in df['Grid_to_home']],
            name='Réseau → Maison',
            marker_color='royalblue',
            hovertemplate='<b>Réseau → Maison</b>: %{y:.3f} kW<br><extra></extra>',
            opacity=0.9
        ))
        
        # 5. Depuis le PV (autoconsommation)
        fig.add_trace(go.Bar(
            x=df['Time'],
            y=[-x for x in df['PV_to_home']],
            name='PV → Maison (auto)',
            marker_color='orange',
            hovertemplate='<b>PV → Maison</b>: %{y:.3f} kW<br><extra></extra>',
            opacity=0.5,
            showlegend=False  # Ne pas montrer deux fois dans la légende
        ))
        
    else:
        # Mode classique sans données solaires
        # Ajouter les barres Pi en négatif (consommation)
        fig.add_trace(go.Bar(
            x=df['Time'],
            y=[-x for x in df['Pi']],  # Pi en négatif pour représenter la consommation
            name='Consommation (kW)',
            marker_color='royalblue',
            hovertemplate='<b>Consommation</b>: %{y:.3f} kW<br><extra></extra>'
        ))
        
        # Ajouter les barres Po (négatives) - injection si applicable
        if 'Po' in df.columns:
            fig.add_trace(go.Bar(
                x=df['Time'],
                y=[-x for x in df['Po']],  # Po en négatif
                name='Injection (kW)',
                marker_color='lightgreen',
                hovertemplate='<b>Injection</b>: %{y:.3f} kW<br><extra></extra>'
            ))
    
    # Ajouter une ligne à zéro pour séparer production et consommation
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Zéro")
    
    # Mise en forme des axes
    fig.update_xaxes(
        title_text="Heure",
        tickformat="%H:%M",
        showgrid=True,
        gridcolor='lightgray'
    )
    
    fig.update_yaxes(
        title_text="Puissance (kW)",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=True,
        zerolinecolor='gray',
        zerolinewidth=2
    )
    
    # Mise en page globale
    fig.update_layout(
        height=700,
        title_text=f"Bilan Énergétique - {format_french_date(date)}",
        showlegend=True,
        template="plotly_white",
        hovermode="x unified",
        plot_bgcolor='rgba(240,240,240,0.5)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        barmode='group'  # Mode de regroupement des barres
    )
    
    # Ajouter des annotations avec les statistiques
    e1_last = df['E1'].iloc[-1] if 'E1' in df.columns else 0
    e2_last = df['E2'].iloc[-1] if 'E2' in df.columns else 0
    e_total = e1_last + e2_last
    
    # Statistiques de production solaire si disponible
    if has_solaredge and 'Production_kW' in df.columns and 'Po' in df.columns:
        solar_production = df['Production_kW'].sum()
        solar_max = df['Production_kW'].max()
        
        # Calculer les flux énergétiques
        pv_to_grid = df['Po'].sum()  # Énergie injectée dans le réseau
        pv_to_home = (df['Production_kW'] - df['Po']).sum()  # Autoconsommation
        grid_to_home = df['Pi'].sum()  # Consommation depuis le réseau
        
        # Taux d'autoconsommation
        autoconsumption_rate = (pv_to_home / solar_production * 100) if solar_production > 0 else 0
        
        stats_text = (
            f"<b>🔋 Bilan Énergétique Complet</b><br>"
            f"🌞 Production PV: {solar_production:.2f} kWh (Max: {solar_max:.3f} kW)<br>"
            f"⚡ Consommation Totale: {grid_to_home + pv_to_home:.2f} kWh<br>"
            f"📊 Équilibre: {solar_production - (grid_to_home + pv_to_home):.2f} kWh<br><br>"
            f"<b>🔄 Flux Énergétiques</b><br>"
            f"🟢 PV → Réseau: {pv_to_grid:.2f} kWh ({pv_to_grid/solar_production*100:.1f}%)<br>"
            f"🟠 PV → Maison: {pv_to_home:.2f} kWh ({autoconsumption_rate:.1f}%)<br>"
            f"🟦 Réseau → Maison: {grid_to_home:.2f} kWh<br>"
            f"🏡 Taux autoconsommation: {autoconsumption_rate:.1f}%"
        )
    else:
        stats_text = f"<b>Énergie Consommée</b><br>Haut tarif (E1): {e1_last:.2f} kWh<br>Bas tarif (E2): {e2_last:.2f} kWh<br>Total: {e_total:.2f} kWh"
    
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        text=stats_text,
        showarrow=False,
        align="center",
        bordercolor="#c9c9c9",
        borderwidth=1,
        borderpad=4,
        bgcolor="#f9f9f9"
    )
    
    return fig

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Énergétique - {{ date_str }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }
        .title {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }
        .nav-buttons {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }
        .btn-primary {
            background-color: #3498db;
            color: white;
        }
        .btn-primary:hover {
            background-color: #2980b9;
        }
        .btn-success {
            background-color: #2ecc71;
            color: white;
        }
        .btn-success:hover {
            background-color: #27ae60;
        }
        .btn-danger {
            background-color: #e74c3c;
            color: white;
        }
        .btn-danger:hover {
            background-color: #c0392b;
        }
        .btn:disabled {
            background-color: #95a5a6;
            cursor: not-allowed;
        }
        .stats {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }
        .stats h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .stats-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat-item {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
        }
        .file-info {
            text-align: center;
            margin-top: 20px;
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">📊 Dashboard Énergétique</div>
            <div class="nav-buttons">
                <button class="btn btn-primary" onclick="window.location.href='/prev?current_date={{ current_date_str }}'" {% if not has_prev %}disabled{% endif %}>← Précédent</button>
                <button class="btn btn-success" onclick="window.location.href='/'">🏠 Aujourd'hui</button>
                <button class="btn btn-primary" onclick="window.location.href='/next?current_date={{ current_date_str }}'" {% if not has_next %}disabled{% endif %}>Suivant →</button>
            </div>
        </div>
        
        <div class="stats">
            {% if has_solaredge %}
            <h3>🔋 Bilan Énergétique - {{ date_str }}</h3>
            <div class="stats-content">
                <div class="stat-item">
                    <div class="stat-value">{{ solar_production }}</div>
                    <div class="stat-label">🌞 Production PV (kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ "%.3f"|format((grid_to_home|float + pv_to_home|float)) }}</div>
                    <div class="stat-label">⚡ Consommation Totale (kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ "%.3f"|format((solar_production|float - (grid_to_home|float + pv_to_home|float))) }}</div>
                    <div class="stat-label">📊 Équilibre (kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ "%.1f"|format(autoconsumption_rate|float) }}</div>
                    <div class="stat-label">🏡 Taux Autoconsommation (%)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ solar_max }}</div>
                    <div class="stat-label">🌞 Production Max (kW)</div>
                </div>
            </div>
            
            <h3 style="margin-top: 15px;">🔄 Flux Énergétiques</h3>
            <div class="stats-content">
                <div class="stat-item">
                    <div class="stat-value">{{ pv_to_grid }}</div>
                    <div class="stat-label">🟢 PV → Réseau (kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ pv_to_home }}</div>
                    <div class="stat-label">🟠 PV → Maison (kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ grid_to_home }}</div>
                    <div class="stat-label">🟦 Réseau → Maison (kWh)</div>
                </div>
            </div>
            {% else %}
            <h3>📊 Énergie Consommée - {{ date_str }}</h3>
            <div class="stats-content">
                <div class="stat-item">
                    <div class="stat-value">{{ e1_last }}</div>
                    <div class="stat-label">Haut tarif (E1) kWh</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ e2_last }}</div>
                    <div class="stat-label">Bas tarif (E2) kWh</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ e_total }}</div>
                    <div class="stat-label">Total kWh</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ pi_max }}</div>
                    <div class="stat-label">Pi Maximum (kW)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ po_max }}</div>
                    <div class="stat-label">Po Maximum (kW)</div>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div id="plot">{{ plot_html|safe }}</div>
        
        <div class="file-info">
            Fichier: {{ filename }} | {{ record_count }} enregistrements
        </div>
    </div>
    
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    """Page principale - affiche la date la plus récente"""
    available_dates = get_available_dates()
    if not available_dates:
        return "Aucun fichier de données trouvé"
    
    # Commencer avec la date la plus récente
    current_date = available_dates[-1]
    return show_date(current_date, available_dates)

@app.route('/date/<date_str>')
def show_specific_date(date_str):
    """Affiche une date spécifique"""
    try:
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return redirect(url_for('index'))
    
    available_dates = get_available_dates()
    if current_date not in available_dates:
        return redirect(url_for('index'))
    
    return show_date(current_date, available_dates)

@app.route('/prev')
def prev_day():
    """Affiche le jour précédent"""
    available_dates = get_available_dates()
    if not available_dates:
        return redirect(url_for('index'))
    
    # Trouver la date actuelle (dernière visite ou date par défaut)
    current_date = request.args.get('current_date')
    if current_date:
        try:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")
        except:
            current_date = available_dates[-1]
    else:
        current_date = available_dates[-1]
    
    # Trouver l'index de la date actuelle
    try:
        current_index = available_dates.index(current_date)
    except ValueError:
        current_index = len(available_dates) - 1
    
    # Aller au jour précédent
    if current_index > 0:
        new_date = available_dates[current_index - 1]
    else:
        new_date = available_dates[0]
    
    return redirect(url_for('show_specific_date', date_str=new_date.strftime("%Y-%m-%d")))

@app.route('/next')
def next_day():
    """Affiche le jour suivant"""
    available_dates = get_available_dates()
    if not available_dates:
        return redirect(url_for('index'))
    
    # Trouver la date actuelle
    current_date = request.args.get('current_date')
    if current_date:
        try:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")
        except:
            current_date = available_dates[-1]
    else:
        current_date = available_dates[-1]
    
    # Trouver l'index de la date actuelle
    try:
        current_index = available_dates.index(current_date)
    except ValueError:
        current_index = len(available_dates) - 1
    
    # Aller au jour suivant
    if current_index < len(available_dates) - 1:
        new_date = available_dates[current_index + 1]
    else:
        new_date = available_dates[-1]
    
    return redirect(url_for('show_specific_date', date_str=new_date.strftime("%Y-%m-%d")))

def show_date(current_date, available_dates):
    """Affiche les données pour une date donnée"""
    df = load_day_data(current_date)
    
    if df is None or df.empty:
        return f"Aucune donnée disponible pour le {current_date.strftime('%d/%m/%Y')}"
    
    # Charger les données SolarEdge
    solaredge_df = load_solaredge_data(current_date)
    
    # Fusionner les données si des données SolarEdge sont disponibles
    if solaredge_df is not None and not solaredge_df.empty:
        df = merge_data_with_solaredge(df, solaredge_df)
        has_solaredge = True
    else:
        has_solaredge = False
    
    # Créer le graphique
    fig = create_plot(df, current_date, has_solaredge)
    plot_html = fig.to_html(full_html=False)
    
    # Calculer les statistiques
    pi_max = df['Pi'].max()
    po_max = df['Po'].max()
    
    # Calculer l'énergie consommée (dernières valeurs de E1 et E2)
    e1_last = df['E1'].iloc[-1] if 'E1' in df.columns else 0
    e2_last = df['E2'].iloc[-1] if 'E2' in df.columns else 0
    e_total = e1_last + e2_last
    
    # Calculer la production solaire et les flux énergétiques si disponible
    if has_solaredge and 'Production_kW' in df.columns and 'Po' in df.columns:
        solar_production = df['Production_kW'].sum()  # Total en kWh
        solar_max = df['Production_kW'].max()
        
        # Calculer les flux énergétiques
        pv_to_grid = df['Po'].sum()  # Énergie injectée dans le réseau
        pv_to_home = (df['Production_kW'] - df['Po']).sum()  # Autoconsommation
        grid_to_home = df['Pi'].sum()  # Consommation depuis le réseau
        
        # Taux d'autoconsommation
        autoconsumption_rate = (pv_to_home / solar_production * 100) if solar_production > 0 else 0
    else:
        solar_production = 0
        solar_max = 0
        pv_to_grid = 0
        pv_to_home = 0
        grid_to_home = 0
        autoconsumption_rate = 0
    
    # Déterminer si les boutons précédent/suivant doivent être activés
    current_index = available_dates.index(current_date)
    has_prev = current_index > 0
    has_next = current_index < len(available_dates) - 1
    
    return render_template_string(
        HTML_TEMPLATE,
        date_str=format_french_date(current_date),
        current_date_str=current_date.strftime('%Y-%m-%d'),
        plot_html=plot_html,
        e1_last=f"{e1_last:.3f}",
        e2_last=f"{e2_last:.3f}",
        e_total=f"{e_total:.3f}",
        solar_production=f"{solar_production:.3f}",
        solar_max=f"{solar_max:.3f}",
        pv_to_grid=f"{pv_to_grid:.3f}",
        pv_to_home=f"{pv_to_home:.3f}",
        grid_to_home=f"{grid_to_home:.3f}",
        autoconsumption_rate=f"{autoconsumption_rate:.1f}",
        pi_max=f"{pi_max:.3f}",
        po_max=f"{po_max:.3f}",
        has_solaredge=has_solaredge,
        filename=f"ts_summary_{current_date.strftime('%Y%m%d')}.csv",
        has_prev=has_prev,
        has_next=has_next
    )

if __name__ == '__main__':
    print("🚀 Dashboard Flask démarré...")
    print("📊 Accédez à http://localhost:5000 pour visualiser les données")
    print("🎮 Navigation: Utilisez les boutons Précédent/Suivant pour changer de jour")
    
    # Démarrer le serveur Flask
    app.run(debug=True, host='0.0.0.0', port=5000)