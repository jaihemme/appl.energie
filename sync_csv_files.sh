#!/bin/bash

# Script de synchronisation des fichiers CSV de pi0.local vers appl.energie
# Ce script utilise rsync pour copier uniquement les fichiers CSV du Raspberry Pi vers le répertoire local data

# Définir explicitement le PATH pour cron
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=fr_CH.utf8
export TZ=Europe/Zurich

# Configuration
# Utiliser l'adresse IP directement pour éviter les problèmes de résolution DNS
SOURCE_HOST="pi@192.168.0.200"
SOURCE_DIR="scripts/data/"
SOURCE_PATH="${SOURCE_HOST}:${SOURCE_DIR}"
DEST_DIR="/home/yogi/appl.energie/data/"
LOG_FILE="/home/yogi/appl.energie/sync_log.txt"

# Options rsync
RSYNC_OPTS="-avz --progress --partial --delete"

# Filtre pour les fichiers CSV uniquement
RSYNC_FILTER="--include='*.csv' --exclude='*'"

# Chemin vers la clé SSH spécifique pour cron
SSH_KEY="/home/yogi/.ssh/id_rsa_cron"

echo "[$(date)] Début de la synchronisation des fichiers CSV..." >> "${LOG_FILE}"
echo "[$(date)] Source: ${SOURCE_PATH}" >> "${LOG_FILE}"
echo "[$(date)] Destination: ${DEST_DIR}" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

# Vérifier que la clé SSH existe
if [ ! -f "${SSH_KEY}" ]; then
    echo "[$(date)] ERREUR: Clé SSH ${SSH_KEY} non trouvée, utilisation de l'authentification par défaut" >> "${LOG_FILE}"
    # Continuer avec l'authentification par défaut
    rsync ${RSYNC_OPTS} ${RSYNC_FILTER} "${SOURCE_PATH}" "${DEST_DIR}" >> "${LOG_FILE}" 2>&1
else
    # Exécuter rsync avec la clé SSH spécifique
    rsync -e "ssh -i ${SSH_KEY}" ${RSYNC_OPTS} ${RSYNC_FILTER} "${SOURCE_PATH}" "${DEST_DIR}" >> "${LOG_FILE}" 2>&1
fi

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo "" >> "${LOG_FILE}"
    echo "[$(date)] Synchronisation terminée avec succès !" >> "${LOG_FILE}"
else
    echo "" >> "${LOG_FILE}"
    echo "[$(date)] ERREUR: Échec de la synchronisation" >> "${LOG_FILE}"
    exit 1
fi
