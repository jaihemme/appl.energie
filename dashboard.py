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

def create_plot(df, date):
    """Crée un graphique Plotly avec les données Pi et Po sur le même graphique"""
    if df is None or df.empty:
        return None
    
    # Créer un graphique simple
    fig = go.Figure()
    
    # Ajouter la ligne Pi (positive)
    fig.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Pi'],
        name='Pi (kW)',
        line=dict(color='royalblue', width=2),
        fill='tozeroy',
        fillcolor='rgba(65, 105, 225, 0.3)',
        hovertemplate='<b>Pi</b>: %{y:.3f} kW<br><extra></extra>'
    ))
    
    # Ajouter la ligne Po (négative)
    fig.add_trace(go.Scatter(
        x=df['Time'],
        y=[-x for x in df['Po']],  # Po en négatif
        name='Po (kW)',
        line=dict(color='firebrick', width=2),
        fill='tozeroy',
        fillcolor='rgba(178, 34, 34, 0.3)',
        hovertemplate='<b>Po</b>: %{y:.3f} kW<br><extra></extra>'
    ))
    
    # Ajouter une ligne à zéro pour séparer Pi et Po
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
        )
    )
    
    # Ajouter des annotations avec les statistiques
    pi_mean = df['Pi'].mean()
    po_mean = df['Po'].mean()
    pi_max = df['Pi'].max()
    po_max = df['Po'].max()
    net_energy = pi_mean - po_mean
    
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        text=f"<b>Statistiques</b><br>Pi: Moyenne={pi_mean:.2f} kW, Max={pi_max:.2f} kW<br>Po: Moyenne={po_mean:.2f} kW, Max={po_max:.2f} kW<br>Bilan: {net_energy:.2f} kW",
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
            <h3>📈 Statistiques du {{ date_str }}</h3>
            <div class="stats-content">
                <div class="stat-item">
                    <div class="stat-value">{{ pi_mean }}</div>
                    <div class="stat-label">Pi Moyenne (kW)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ po_mean }}</div>
                    <div class="stat-label">Po Moyenne (kW)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ pi_max }}</div>
                    <div class="stat-label">Pi Maximum (kW)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ po_max }}</div>
                    <div class="stat-label">Po Maximum (kW)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ net_energy }}</div>
                    <div class="stat-label">Bilan Net (kW)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ record_count }}</div>
                    <div class="stat-label">Enregistrements</div>
                </div>
            </div>
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
    
    # Créer le graphique
    fig = create_plot(df, current_date)
    plot_html = fig.to_html(full_html=False)
    
    # Calculer les statistiques
    pi_mean = df['Pi'].mean()
    po_mean = df['Po'].mean()
    pi_max = df['Pi'].max()
    po_max = df['Po'].max()
    record_count = len(df)
    net_energy = pi_mean - po_mean
    
    # Déterminer si les boutons précédent/suivant doivent être activés
    current_index = available_dates.index(current_date)
    has_prev = current_index > 0
    has_next = current_index < len(available_dates) - 1
    
    return render_template_string(
        HTML_TEMPLATE,
        date_str=format_french_date(current_date),
        current_date_str=current_date.strftime('%Y-%m-%d'),
        plot_html=plot_html,
        pi_mean=f"{pi_mean:.3f}",
        po_mean=f"{po_mean:.3f}",
        pi_max=f"{pi_max:.3f}",
        po_max=f"{po_max:.3f}",
        net_energy=f"{net_energy:.3f}",
        record_count=record_count,
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