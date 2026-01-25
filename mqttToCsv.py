import json
import csv
import paho.mqtt.client as mqtt
from datetime import datetime
from collections import defaultdict
import threading
import logging
import time
import sys
import argparse


# Configuration MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "tele/tasmota_EB7D9F/SENSOR"
MQTT_CLIENT = "tasmota_EB7D9F"
MQTT_USER = "DVES_USER"
MQTT_PASSWORD = ""
MQTT_TIMEOUT = 10

# Fichiers de sortie
DATE = datetime.now().strftime('%Y%m%d')
TS_CSV_FILE = f"ts_summary_{DATE}.csv"  # Pour les résumés TS toutes les 5 minutes
AGGREGATE_CSV_FILE = f"energie_{DATE}.csv"  # Pour les données agrégées par seconde
# flag pour plus de sorties à la console
VERBOSE = False

# Structure pour agréger les données par seconde
aggregation = defaultdict(list)

# Flag pour signaler l'arrêt du programme
stop_program = False


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    if VERBOSE: print(f"{msg.topic}: {str(msg.payload)}")

    payload = json.loads(msg.payload.decode())
    if VERBOSE: print(f"Received data: {payload}")

    try:
        time_str = payload.get("Time", "")
        z_data = payload.get("z", {})

        # Vérifier si c'est un message TS (résumé 5 minutes)
        if "TS" in z_data:
            # Traiter comme résumé TS
            process_ts_summary(time_str, z_data)
        else:
            # Traiter comme données individuelles à agréger par seconde
            process_single_data(time_str, z_data)

    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")


def process_ts_summary(time_str, z_data):
    """Traite les résumés TS et les écrit dans le fichier CSV dédié."""
    if VERBOSE: print(f"process_ts_summary: {time_str} - {z_data}")
    ts_data = {
        "Time": time_str,
        "TS": z_data.get("TS"),
        "NS": z_data.get("NS"),
        "Pi": z_data.get("Pi"),
        "Po": z_data.get("Po"),
        "B1": z_data.get("B1"),
        "B2": z_data.get("B2"),
        "E1": z_data.get("E1"),
        "E2": z_data.get("E2"),
        "P1i": z_data.get("P1i"),
        "P2i": z_data.get("P2i"),
        "P3i": z_data.get("P3i"),
        "P1o": z_data.get("P1o"),
        "P2o": z_data.get("P2o"),
        "P3o": z_data.get("P3o"),
        "I1": z_data.get("I1"),
        "I2": z_data.get("I2"),
        "I3": z_data.get("I3"),
        "U1": z_data.get("U1"),
        "U2": z_data.get("U2"),
        "U3": z_data.get("U3")
    }

    # Écrire dans le fichier CSV des résumés TS
    write_ts_to_csv(ts_data)


def process_single_data(time_str, z_data):
    """ cumule les données pendant la même seconde pour condenser les sorties """
    if VERBOSE: print(f"process_single_data: {time_str} - {z_data}")
    # nouvelle seconde, il n'y a pas encore d'entrées 
    if aggregation[time_str] == []:
        aggregation[time_str] = z_data  
    # même seconde: mise à jour de l'élément 
    else:
        aggregation[time_str].update(z_data)


def write_ts_to_csv(data):
    """Écrit les résumés TS dans le fichier CSV dédié."""
    headers = [
        "Time", "TS", "NS", "Pi", "Po",
        "B1", "B2", "E1", "E2",
        "P1i", "P2i", "P3i", "P1o", "P2o", "P3o",
        "I1", "I2", "I3", "U1", "U2", "U3"
    ]

    try:
        with open(TS_CSV_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if file.tell() == 0:
                if VERBOSE: print('Ecris les entêtes')
                writer.writeheader()
            writer.writerow(data)
    except Exception as e:
        print(f"Erreur lors de l'écriture dans {TS_CSV_FILE}: {e}")

    if VERBOSE: print(f"Résumé TS enregistré: {data}")


def write_aggregation_to_csv():
    """Écrit les données agrégées par seconde dans le fichier CSV."""
    if VERBOSE: print('write_aggregation_to_csv')
    if VERBOSE: print(aggregation)
    headers = [
        "Time", "Pi", "Po",
        "B1", "B2", "E1", "E2",
        "P1i", "P2i", "P3i", "P1o", "P2o", "P3o",
        "I1", "I2", "I3", "U1", "U2", "U3",
        "count"  # Nombre de mesures dans cette seconde
    ]

    try:
        with open(AGGREGATE_CSV_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if file.tell() == 0:
                if VERBOSE: print('writer.writeheader')
                writer.writeheader()

            # Pour chaque seconde, calculer les moyennes et écrire
            for time_key, data_list in aggregation.items():
                if VERBOSE: print(f"key: {time_key} - {data_list}")
                if data_list:  # Vérifier qu'il y a des données
                    data_list.update({'Time': time_key.replace('T',' ')})
                    count = len(data_list)
                    writer.writerow(data_list)
                    if VERBOSE: print(f"Agrégation seconde écrite pour {time_key}: {count} mesures")

        # Réinitialiser l'agrégation après écriture
        aggregation.clear()

    except Exception as e:
        print(f"Erreur lors de l'écriture dans {AGGREGATE_CSV_FILE}: {e}")


def periodic_write():
    """Fonction qui écrit périodiquement les données agrégées."""
    global stop_program
    if VERBOSE: print('periodic_write()')
    while True:
        time.sleep(60)  # Écrire toutes les minutes
        if aggregation:
            if VERBOSE: print("Écriture périodique des données agrégées par seconde...")
            write_aggregation_to_csv()
        
        # Vérifier si la date a changé
        current_date = datetime.now().strftime('%Y%m%d')
        if current_date != DATE:
            print("Fin de journée, arrêt de script")
            stop_program = True
            break


def parse_arguments():
    """Parse les arguments de la ligne de commande"""
    parser = argparse.ArgumentParser(description='MQTT to CSV Converter')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Active le mode verbose pour plus de sorties console')
    return parser.parse_args()


def main():
    # Parser les arguments de la ligne de commande
    args = parse_arguments()
    global VERBOSE
    VERBOSE = args.verbose
    
    # Initialiser le client MQTT avec la nouvelle API
    logging.basicConfig(level=logging.INFO)
    if VERBOSE: logging.basicConfig(level=logging.DEBUG)

    client = mqtt.Client(
        client_id=MQTT_CLIENT,   # 👈 ID unique
        clean_session=True,      # 👈 Session propre (recommandé en dev)
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.enable_logger()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    # Se connecter au broker
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_TIMEOUT)

    # Démarrer la boucle MQTT
    try:
        client.loop_start()
        print('Script is looping now ... put it in background')
        # Démarrer le thread d'écriture périodique
        write_thread = threading.Thread(target=periodic_write, daemon=True)
        write_thread.start()

        # Laisser tourner indéfiniment
        while not stop_program:
            time.sleep(1)

        # Arrêt programmé (fin de journée)
        print("Arrêt programmé du client MQTT...")
        # Écrire les données agrégées restantes avant de quitter
        if aggregation:
            write_aggregation_to_csv()
        client.loop_stop()
        client.disconnect()
        sys.exit(0)

    except KeyboardInterrupt:
        print("Arrêt du client MQTT...")
        # Écrire les données agrégées restantes avant de quitter
        if aggregation:
            write_aggregation_to_csv()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

###
