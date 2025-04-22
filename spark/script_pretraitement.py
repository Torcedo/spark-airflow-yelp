import json
import os
import sys
import random

input_path = "data/yelp_academic_dataset_checkin.json"
output_path = "data/yelp_academic_dataset_checkin_opti.json"
sample_ratio = 0.05

# Vérifie si le fichier d'entrée existe
if not os.path.isfile(input_path):
    print(f"Fichier d'entrée non trouvé : {input_path}")
    sys.exit(1)

# Supprime le fichier de sortie s’il existe
if os.path.isfile(output_path):
    print(f"Fichier de sortie existant supprimé : {output_path}")
    os.remove(output_path)



try:
    kept_lines = 0
    total_lines = 0

    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            total_lines += 1
            if random.random() <= sample_ratio:
                obj = json.loads(line)
                business_id = obj.get("business_id")
                date_str = obj.get("date", "")
                if business_id and date_str:
                    for d in date_str.split(","):
                        d = d.strip()
                        if d:
                            json.dump({"business_id": business_id, "timestamp": d}, outfile)
                            outfile.write("\n")
                    kept_lines += 1
                    
    print("Fichier aplati avec succès.")
except Exception as e:
    print(f"Erreur pendant le traitement : {e}")
    sys.exit(1)
