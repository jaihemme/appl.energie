# 📊 Dashboard Énergétique - Documentation

## 🎯 Description

Dashboard Flask pour visualiser graphiquement les données de consommation (Pi) et production (Po) énergétique jour par jour. Ce tableau de bord permet une analyse visuelle des données avec navigation entre les différents jours disponibles.

## 🚀 Installation et Exécution

### Prérequis

Assurez-vous d'avoir Python 3.x installé ainsi que les dépendances suivantes :

```bash
pip install flask pandas plotly
```

### Lancement du Dashboard

1. **Lancer le serveur Flask** :
```bash
python3 dashboard.py
```

2. **Accéder au dashboard** dans votre navigateur :
```
http://localhost:5000
```

## 📈 Fonctionnalités

### Visualisation Graphique

- **Courbes de consommation (Pi)** : Ligne bleue avec remplissage
- **Courbes de production (Po)** : Ligne rouge avec remplissage (valeurs négatives)
- **Ligne de zéro** : Séparation claire entre consommation et production
- **Échelle temporelle** : Heures de la journée sur l'axe X
- **Échelle de puissance** : kW sur l'axe Y

### Navigation entre les Jours

- **← Précédent** : Passer au jour précédent
- **→ Suivant** : Passer au jour suivant  
- **🏠 Aujourd'hui** : Revenir à la date la plus récente
- **Désactivation automatique** des boutons aux limites

### Statistiques Complètes

Le dashboard affiche pour chaque jour :

- **Pi Moyenne** : Consommation moyenne en kW
- **Po Moyenne** : Production moyenne en kW
- **Pi Maximum** : Pic de consommation en kW
- **Po Maximum** : Pic de production en kW
- **Bilan Net** : Différence moyenne (Pi - Po) en kW
- **Nombre d'enregistrements** : Total des mesures pour la journée

## 📁 Structure des Données

### Format des Fichiers

Les données sont lues depuis des fichiers CSV dans le répertoire `data/` avec le format :
```
ts_summary_YYYYMMDD.csv
```

Exemple : `ts_summary_20260128.csv` pour le 28 janvier 2026

### Colonnes Utilisées

- **Time** : Timestamp au format `YYYY-MM-DDTHH:MM:SS`
- **Pi** : Puissance instantanée (consommation) en kW
- **Po** : Puissance de sortie (production) en kW

## 🎨 Interface Utilisateur

### Capture d'écran (Description)

<img width="1223" height="948" alt="dashboard" src="https://github.com/user-attachments/assets/158436e7-ec69-4ec0-86ba-a28d89a7d36c" />


## 🔧 Configuration

### Répertoire des Données

Par défaut, le dashboard lit les fichiers depuis `data/`. Vous pouvez modifier cette configuration en changeant la variable :

```python
DATA_DIR = "data/"
```

### Port du Serveur

Le serveur Flask écoute sur le port 5000. Pour changer le port :

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changer 8080 par le port souhaité
```

## 📱 Fonctionnalités Avancées

### Graphiques Interactifs

Les graphiques sont créés avec Plotly et offrent :

- **Zoom** : Sélectionnez une zone pour zoomer
- **Pan** : Déplacez le graphique en cliquant-glissant
- **Hover** : Survolez les courbes pour voir les valeurs exactes
- **Reset** : Double-cliquez pour réinitialiser la vue
- **Légende interactive** : Cliquez sur les noms pour masquer/afficher les courbes

### Responsive Design

L'interface s'adapte automatiquement à la taille de l'écran :

- **Grand écran** : Affichage optimal avec toutes les statistiques
- **Tablette** : Adaptation de la mise en page
- **Mobile** : Version simplifiée et tactile

## 💡 Conseils d'Utilisation

### Analyse des Données

1. **Identifiez les pics** : Repérez les heures de forte consommation
2. **Comparez les jours** : Utilisez la navigation pour analyser les tendances
3. **Surveillez le bilan** : Le bilan net montre l'équilibre consommation/production
4. **Exportez les données** : Les valeurs exactes sont disponibles dans le tableau

### Dépannage

- **Aucune donnée affichée** : Vérifiez que les fichiers CSV existent dans `data/`
- **Erreur de chargement** : Assurez-vous que le format des fichiers est correct
- **Problème d'affichage** : Vérifiez que Plotly est bien installé

## 📋 Exemple de Données

```csv
Time,TS,NS,Pi,Po,B1,B2,E1,E2,P1i,P2i,P3i,P1o,P2o,P3o,I1,I2,I3,U1,U2,U3
2026-01-28T00:01:29,260128000141W,353234363435,6.309,0.0,10410.023,12324.35,15414.49,78.406,2.689,2.642,0.98,0.0,0.0,0.0,11.0,11.0,4.0,228.0,227.7,229.6
2026-01-28T00:06:29,260128000641W,353234363435,4.652,0.0,10410.023,12324.779,15414.49,78.406,2.588,1.05,0.997,0.0,0.0,0.0,11.0,4.0,5.0,228.6,230.7,231.5
```

## 🔄 Mises à Jour

### Version 1.0 (Actuelle)

- Visualisation avec lignes et remplissage
- Pi en positif, Po en négatif
- Dates en français
- Navigation entre les jours
- Statistiques complètes
- Interface responsive

### Version 2.0 (Prévue)

- Sélection de plage de dates
- Export des graphiques en PNG
- Comparaison entre plusieurs jours
- Alertes pour valeurs anormales
- Historique et tendances

## 📚 Dépendances

- **Flask** : Framework web pour l'interface
- **Pandas** : Manipulation des données CSV
- **Plotly** : Création des graphiques interactifs

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commitez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier LICENCE pour plus de détails.

## 🙏 Remerciements

- À tous les contributeurs qui améliorent ce projet
- À la communauté open-source pour les outils utilisés
- Aux utilisateurs qui testent et donnent leur feedback

---

**Note** : Ce dashboard est conçu pour une utilisation locale. Pour un déploiement en production, des modifications de sécurité supplémentaires seraient nécessaires.

**Auteur** : mistral-vibe
**Version** : 1.0
**Date** : 28 janvier 2026
