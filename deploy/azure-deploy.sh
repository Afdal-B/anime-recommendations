#!/usr/bin/env bash
# Déploie le projet complet sur Azure :
#   - Azure SQL (offre gratuite)               données de l'application
#   - Blob Storage                             notes d'entraînement + modèles
#   - Container Registry + Container Apps      application (React + FastAPI)
#   - Azure Machine Learning                   entraînement du modèle
# Prérequis : Azure CLI connecté (az login). Aucun Docker local requis (build dans ACR).
#
# Usage :
#   SQL_ADMIN_PASSWORD='...' ./deploy/azure-deploy.sh
#
# Au premier déploiement, les notes de départ sont lues dans server/data/user-filtered.csv
# (jeu Kaggle "dbdmobile/myanimelist-dataset", non versionné) ; autre chemin : KAGGLE_RATINGS_CSV.
set -euo pipefail

LOCATION="${LOCATION:-francecentral}"
RG="${RG:-anime-reco-rg}"
SUFFIX="${SUFFIX:-$(az account show --query id -o tsv | cut -c1-6)}"
ACR="${ACR:-animereco${SUFFIX}}"
STORAGE="${STORAGE:-animereco${SUFFIX}}"
SQL_SERVER="${SQL_SERVER:-anime-reco-sql-${SUFFIX}}"
SQL_DB="${SQL_DB:-anime-reco}"
SQL_ADMIN="${SQL_ADMIN:-animeadmin}"
ENV_NAME="${ENV_NAME:-anime-reco-env}"
APP_NAME="${APP_NAME:-anime-reco}"
ML_WORKSPACE="${ML_WORKSPACE:-anime-reco-ml}"
ML_COMPUTE="train-cluster"
# Tag unique à chaque déploiement : garantit une nouvelle révision de l'application
IMAGE="${ACR}.azurecr.io/anime-reco:$(git rev-parse --short HEAD)-$(date +%Y%m%d%H%M%S)"
PYTHON="${PYTHON:-.venv/bin/python}"
KAGGLE_RATINGS_CSV="${KAGGLE_RATINGS_CSV:-server/data/user-filtered.csv}"
: "${SQL_ADMIN_PASSWORD:?Définir SQL_ADMIN_PASSWORD}"

cd "$(dirname "$0")/.."

echo ">>> Extensions et providers"
az extension add --name containerapp --upgrade --only-show-errors
az extension add --name ml --upgrade --only-show-errors
for ns in Microsoft.App Microsoft.OperationalInsights Microsoft.ContainerRegistry Microsoft.Sql \
          Microsoft.Storage Microsoft.MachineLearningServices Microsoft.KeyVault Microsoft.Insights; do
  az provider register --namespace "$ns" --wait
done

echo ">>> Groupe de ressources"
az group create -n "$RG" -l "$LOCATION" -o none

# ---------------------------------------------------------------- Azure SQL
echo ">>> Azure SQL (serverless, offre gratuite)"
az sql server show -g "$RG" -n "$SQL_SERVER" -o none 2>/dev/null || \
  az sql server create -g "$RG" -n "$SQL_SERVER" -l "$LOCATION" \
    -u "$SQL_ADMIN" -p "$SQL_ADMIN_PASSWORD" -o none
# Autoriser les services Azure (Container Apps) à se connecter
az sql server firewall-rule create -g "$RG" -s "$SQL_SERVER" -n AllowAzureServices \
  --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0 -o none
az sql db show -g "$RG" -s "$SQL_SERVER" -n "$SQL_DB" -o none 2>/dev/null || \
  az sql db create -g "$RG" -s "$SQL_SERVER" -n "$SQL_DB" \
    -e GeneralPurpose -f Gen5 -c 2 --compute-model Serverless \
    --use-free-limit --free-limit-exhaustion-behavior AutoPause -o none

DB_CONN="Driver={ODBC Driver 18 for SQL Server};Server=tcp:${SQL_SERVER}.database.windows.net,1433;Database=${SQL_DB};Uid=${SQL_ADMIN};Pwd=${SQL_ADMIN_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"

# ------------------------------------------------------------- Blob Storage
echo ">>> Blob Storage (notes d'entraînement et modèles)"
az storage account show -g "$RG" -n "$STORAGE" -o none 2>/dev/null || \
  az storage account create -g "$RG" -n "$STORAGE" -l "$LOCATION" \
    --sku Standard_LRS --kind StorageV2 --min-tls-version TLS1_2 \
    --allow-blob-public-access false -o none
STORAGE_ID=$(az storage account show -g "$RG" -n "$STORAGE" --query id -o tsv)
STORAGE_KEY=$(az storage account keys list -g "$RG" -n "$STORAGE" --query "[0].value" -o tsv)
STORAGE_CONN=$(az storage account show-connection-string -g "$RG" -n "$STORAGE" -o tsv)
blob() { az storage "$@" --account-name "$STORAGE" --account-key "$STORAGE_KEY" --only-show-errors; }

blob container create -n data -o none
blob container create -n models -o none

# Modèle de départ (celui du dépôt), pour que l'application et le pipeline partent d'une version connue
if [ "$(blob blob exists -c models -n als_model/initial/_READY --query exists -o tsv)" != "true" ]; then
  blob blob upload-batch -d models --destination-path als_model/initial \
    -s server/models/unzipped/als_model.zip -o none
  # Marqueur envoyé en dernier : l'API ne charge que les modèles complets
  READY_FILE=$(mktemp) && printf 'ok\n' > "$READY_FILE"
  blob blob upload -c models -n als_model/initial/_READY -f "$READY_FILE" -o none
  rm -f "$READY_FILE"
fi

# Notes de départ (jeu MyAnimeList)
if [ "$(blob blob exists -c data -n ratings.csv --query exists -o tsv)" != "true" ]; then
  if [ -f "$KAGGLE_RATINGS_CSV" ]; then
    RATINGS_FILE="$(mktemp -d)/ratings.csv"
    "$PYTHON" server/ml/prepare_ratings.py "$KAGGLE_RATINGS_CSV" "$RATINGS_FILE"
    blob blob upload -c data -n ratings.csv -f "$RATINGS_FILE" -o none
  else
    echo "!!! $KAGGLE_RATINGS_CSV introuvable : data/ratings.csv n'est pas envoyé, l'entraînement échouera."
  fi
fi

# ------------------------------------------------- Registry + Container Apps
echo ">>> Registre de conteneurs + build de l'image dans Azure"
az acr show -g "$RG" -n "$ACR" -o none 2>/dev/null || \
  az acr create -g "$RG" -n "$ACR" --sku Basic -l "$LOCATION" -o none
az acr build -r "$ACR" -t "$IMAGE" --platform linux/amd64 .

echo ">>> Environnement Container Apps"
# Mode standard (WorkloadProfiles, profil Consumption) : certaines versions de l'extension
# créent sinon un environnement "Express", qui refuse l'identité managée pour le registre.
ENV_MODE_ARGS=()
if az containerapp env create --help 2>/dev/null | grep -q -- "--environment-mode"; then
  ENV_MODE_ARGS=(--environment-mode WorkloadProfiles)
fi
ENV_MODE=$(az containerapp env show -g "$RG" -n "$ENV_NAME" --query properties.environmentMode -o tsv 2>/dev/null || true)
if [ -z "$ENV_MODE" ]; then
  az containerapp env create -g "$RG" -n "$ENV_NAME" -l "$LOCATION" "${ENV_MODE_ARGS[@]}" -o none
elif [ "$ENV_MODE" = "Express" ]; then
  echo "!!! L'environnement $ENV_NAME est en mode Express (non compatible). Supprimez-le puis relancez :"
  echo "    az containerapp env delete -g $RG -n $ENV_NAME --yes"
  exit 1
fi

SECRETS=("db-conn=${DB_CONN}" "storage-conn=${STORAGE_CONN}")
ENV_VARS=("AZURE_DATABASE_CONNECTION_STRING=secretref:db-conn" "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn")

echo ">>> Container App"
if az containerapp show -g "$RG" -n "$APP_NAME" -o none 2>/dev/null; then
  az containerapp secret set -g "$RG" -n "$APP_NAME" --secrets "${SECRETS[@]}" -o none
  az containerapp update -g "$RG" -n "$APP_NAME" --image "$IMAGE" --set-env-vars "${ENV_VARS[@]}" -o none
else
  az containerapp create -g "$RG" -n "$APP_NAME" --environment "$ENV_NAME" \
    --image "$IMAGE" --registry-server "${ACR}.azurecr.io" --registry-identity system \
    --target-port 8000 --ingress external \
    --cpu 0.5 --memory 1.0Gi --min-replicas 0 --max-replicas 2 \
    --secrets "${SECRETS[@]}" --env-vars "${ENV_VARS[@]}" -o none
fi

echo ">>> Initialisation de la base (schéma + catalogue d'animés)"
JOB="${APP_NAME}-seed"
if ! az containerapp job show -g "$RG" -n "$JOB" -o none 2>/dev/null; then
  # Création avec une image publique : l'identité du job doit d'abord exister
  # pour recevoir le droit de lire le registre
  az containerapp job create -g "$RG" -n "$JOB" --environment "$ENV_NAME" \
    --trigger-type Manual --replica-timeout 1800 --mi-system-assigned \
    --image mcr.microsoft.com/k8se/quickstart:latest \
    --cpu 0.5 --memory 1.0Gi \
    --secrets "db-conn=${DB_CONN}" \
    --env-vars "AZURE_DATABASE_CONNECTION_STRING=secretref:db-conn" \
    --command "python" --args "/srv/server/seed_db.py" -o none
  JOB_PRINCIPAL=$(az containerapp job show -g "$RG" -n "$JOB" --query identity.principalId -o tsv)
  az role assignment create --assignee-object-id "$JOB_PRINCIPAL" --assignee-principal-type ServicePrincipal \
    --role AcrPull --scope "$(az acr show -n "$ACR" --query id -o tsv)" -o none
fi
# Le droit AcrPull peut mettre quelques minutes à se propager : on réessaie
for attempt in $(seq 1 10); do
  if az containerapp job registry set -g "$RG" -n "$JOB" --server "${ACR}.azurecr.io" --identity system -o none 2>/dev/null \
     && az containerapp job update -g "$RG" -n "$JOB" --image "$IMAGE" -o none 2>/dev/null; then
    break
  fi
  [ "$attempt" = 10 ] && { echo "!!! Impossible de configurer le job $JOB avec l'image $IMAGE"; exit 1; }
  echo "    droits sur le registre pas encore actifs, nouvel essai dans 30 s…"
  sleep 30
done
az containerapp job start -g "$RG" -n "$JOB" -o none

# ----------------------------------------------------- Azure Machine Learning
echo ">>> Azure Machine Learning (workspace, accès au stockage, cluster, planification)"
ML=(-g "$RG" -w "$ML_WORKSPACE")
az ml workspace show -g "$RG" -n "$ML_WORKSPACE" -o none 2>/dev/null || \
  az ml workspace create -g "$RG" -n "$ML_WORKSPACE" -l "$LOCATION" -o none

# Datastores sans clé : l'accès passe par l'identité managée du cluster
for ds in anime_data anime_models; do
  az ml datastore create "${ML[@]}" -f "server/ml/datastores/${ds}.yml" \
    --set account_name="$STORAGE" -o none
done

# Cluster à 0 nœud au repos : on ne paie que pendant l'entraînement
az ml compute show "${ML[@]}" -n "$ML_COMPUTE" -o none 2>/dev/null || \
  az ml compute create "${ML[@]}" -n "$ML_COMPUTE" --type AmlCompute \
    --size "${ML_VM_SIZE:-Standard_DS3_v2}" --min-instances 0 --max-instances 1 \
    --idle-time-before-scale-down 300 --identity-type SystemAssigned -o none
COMPUTE_PRINCIPAL=$(az ml compute show "${ML[@]}" -n "$ML_COMPUTE" --query identity.principal_id -o tsv)
az role assignment create --assignee-object-id "$COMPUTE_PRINCIPAL" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" --scope "$STORAGE_ID" -o none

# Réentraînement planifié : désactivé par défaut (on réentraîne à la demande avec retrain.sh).
# Pour l'activer : TRAINING_SCHEDULE=1 ./deploy/azure-deploy.sh (fréquence dans server/ml/schedule.yml)
if [ "${TRAINING_SCHEDULE:-0}" = "1" ]; then
  if az ml schedule show "${ML[@]}" -n anime-reco-weekly-training -o none 2>/dev/null; then
    az ml schedule update "${ML[@]}" -f server/ml/schedule.yml -o none
    az ml schedule enable "${ML[@]}" -n anime-reco-weekly-training -o none
  else
    az ml schedule create "${ML[@]}" -f server/ml/schedule.yml -o none
  fi
fi

URL="https://$(az containerapp show -g "$RG" -n "$APP_NAME" --query properties.configuration.ingress.fqdn -o tsv)"
echo ">>> Déployé : $URL (santé et version du modèle : $URL/api/health)"
echo ">>> Lancer un entraînement maintenant : ./deploy/retrain.sh"
