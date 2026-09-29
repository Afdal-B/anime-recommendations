import os
import tempfile

MODELS_CONTAINER = "models"
MODELS_PREFIX = "als_model/"


def _container():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        return None
    from azure.storage.blob import ContainerClient

    return ContainerClient.from_connection_string(connection_string, MODELS_CONTAINER)


def latest_model_version():
    """Nom du dossier du modèle le plus récent dans Blob Storage (als_model/<version>/), ou None.

    Chaque entraînement Azure ML écrit dans son propre dossier ; un modèle n'est
    retenu que s'il est complet (marqueur _READY écrit en dernier).
    """
    container = _container()
    if container is None:
        return None
    completed = {}
    for blob in container.list_blobs(name_starts_with=MODELS_PREFIX):
        parts = blob.name[len(MODELS_PREFIX):].split("/")
        if len(parts) == 2 and parts[1] == "_READY":
            completed[parts[0]] = blob.last_modified
    return max(completed, key=completed.get) if completed else None


def download_model(version):
    """Télécharge als_model/<version>/ dans un dossier temporaire et renvoie son chemin."""
    container = _container()
    prefix = f"{MODELS_PREFIX}{version}/"
    target = tempfile.mkdtemp(prefix="als_model_")
    for blob in container.list_blobs(name_starts_with=prefix):
        relative = blob.name[len(prefix):]
        # Seuls les facteurs et le nombre de notes par anime servent à l'API
        needed = relative.startswith(("userFactors/", "itemFactors/")) or relative == "item_counts.csv"
        if not needed or relative.endswith("/"):
            continue
        path = os.path.join(target, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            container.download_blob(blob.name).readinto(f)
    return target
