import os
from google.cloud import storage

def upload_folder_to_gcs(local_folder, bucket_name, destination_folder=""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    uploaded = 0
    skipped = 0

    print(f"\n📁 Dossier local : {os.path.abspath(local_folder)}")
    print(f"☁️  Bucket cible : gs://{bucket_name}/{destination_folder}\n")

    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            blob_path = os.path.join(destination_folder, relative_path).replace("\\", "/")

            blob = bucket.blob(blob_path)

            if blob.exists():
                print(f"⚠️  Ignoré (existe déjà) : {blob_path}")
                skipped += 1
                continue

            print(f"⬆️  Upload : {blob_path}")
            blob.upload_from_filename(local_path)
            uploaded += 1

    print("\n✅ Upload terminé.")
    print(f"🟢 {uploaded} fichiers uploadés")
    print(f"🟡 {skipped} fichiers déjà présents ignorés")

if __name__ == "__main__":
    upload_folder_to_gcs(
        local_folder="data",                        # dossier local
        bucket_name="datasparkyelp-yelp-raw",       # bucket GCS
        destination_folder="json_file"              # préfixe dans le bucket
    )
    upload_folder_to_gcs(
        local_folder="spark",                       # transformation
        bucket_name="datasparkyelp-spark-scripts",       # bucket GCS
        destination_folder=""              # préfixe dans le bucket
    )
