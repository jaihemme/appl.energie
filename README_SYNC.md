# Synchronisation des fichiers CSV avec rsync

Ce document explique comment synchroniser les fichiers CSV du Raspberry Pi `pi0.local` vers le répertoire local `/home/yogi/appl.energie/data/`.

## Prérequis

1. **rsync installé** : Doit être installé sur les deux machines
   ```bash
   sudo apt install rsync
   ```

2. **Accès SSH configuré** : La machine locale doit pouvoir se connecter à pi0.local via SSH
   ```bash
   ssh-copy-id pi@pi0.local
   ```

3. **Répertoire de destination** : Le répertoire `/home/yogi/appl.energie/data/` doit exister localement
   ```bash
   mkdir -p /home/yogi/appl.energie/data/
   ```

## Utilisation du script

### Exécution manuelle
```bash
cd /home/yogi/appl.energie/
./sync_csv_files.sh
```

### Exécution automatique (cron)

Pour automatiser la synchronisation, ajoutez une entrée cron :

1. Éditez le crontab :
   ```bash
   crontab -e
   ```

2. Ajoutez une ligne pour exécuter le script régulièrement (ex: toutes les heures) :
   ```bash
   # Synchronisation des fichiers CSV toutes les heures
   0 * * * * /home/yogi/appl.energie/sync_csv_files.sh >> /home/yogi/appl.energie/sync_log.txt 2>&1
   ```

## Options rsync utilisées

- `-a` : Mode archive (préserve les permissions, propriétaires, timestamps)
- `-v` : Mode verbose (affiche les fichiers transférés)
- `-z` : Compression pendant le transfert
- `--progress` : Affiche la progression
- `--partial` : Garde les fichiers partiellement transférés
- `--delete` : Supprime les fichiers de destination qui n'existent plus à la source
- `--include='*.csv'` : Inclut uniquement les fichiers CSV
- `--exclude='*'` : Exclut tous les autres fichiers

## Vérification

Pour vérifier que la synchronisation a fonctionné :

```bash
# Vérifier les fichiers locaux synchronisés
ls -la /home/yogi/appl.energie/data/*.csv

# Vérifier le journal de synchronisation
cat /home/yogi/appl.energie/sync_log.txt

# Comparer avec les fichiers source sur le Raspberry Pi
ssh pi@pi0.local "ls -la scripts/*.csv"
```

## Dépannage

### Problèmes de connexion SSH

Si vous avez des problèmes de connexion :

1. Vérifiez que pi0.local est accessible :
   ```bash
   ping pi0.local
   ```

2. Testez la connexion SSH :
   ```bash
   ssh pi@pi0.local
   ```

3. Vérifiez que l'authentification par clé est configurée :
   ```bash
   ssh-copy-id pi@pi0.local
   ```

### Problèmes de permissions

Assurez-vous que :
- Le répertoire source sur le Raspberry Pi est accessible en lecture
- Le répertoire de destination local est accessible en écriture
- L'utilisateur local a les droits nécessaires sur `/home/yogi/appl.energie/data/`

### Vérification de la synchronisation

Pour voir quels fichiers seraient synchronisés sans faire le transfert :
```bash
rsync -avn --include='*.csv' --exclude='*' pi@pi0.local:scripts/ /home/yogi/appl.energie/data/
```

## Sécurité

- Le script utilise SSH pour le transfert, ce qui est sécurisé
- Les données sont compressées pendant le transfert
- Aucune donnée sensible n'est stockée dans le script
- Le transfert se fait du Raspberry Pi vers la machine locale

## Cas d'utilisation

Ce script est particulièrement utile pour :

1. **Centralisation des données** : Récupérer les données CSV générées sur le Raspberry Pi
2. **Sauvegarde** : Créer une copie locale des fichiers importants
3. **Traitement supplémentaire** : Avoir les données localement pour analyse
4. **Archivage** : Conserver un historique des données énergétiques

## Historique des modifications

- 1.0 : Création initiale du script de synchronisation (sens inversé)
- 1.1 : Ajout de la documentation et des options de vérification
- 2.0 : Inversion du sens de synchronisation (pi0.local -> local)
