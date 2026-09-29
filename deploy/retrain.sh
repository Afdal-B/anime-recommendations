#!/usr/bin/env bash
# Lance un entraînement du modèle sur Azure ML (à faire quand de nouvelles notes sont arrivées).
# L'application charge le nouveau modèle d'elle-même (vérification toutes les heures) ;
# ce script redémarre aussi l'application pour qu'il soit pris en compte tout de suite.
set -euo pipefail

RG="${RG:-anime-reco-rg}"
ML_WORKSPACE="${ML_WORKSPACE:-anime-reco-ml}"
APP_NAME="${APP_NAME:-anime-reco}"

cd "$(dirname "$0")/.."

echo ">>> Entraînement sur Azure ML (logs en direct)"
az ml job create -g "$RG" -w "$ML_WORKSPACE" -f server/ml/train-pipeline.yml --stream

echo ">>> Redémarrage de l'application pour charger le nouveau modèle"
REVISION=$(az containerapp show -g "$RG" -n "$APP_NAME" --query properties.latestRevisionName -o tsv)
az containerapp revision restart -g "$RG" -n "$APP_NAME" --revision "$REVISION" -o none
echo ">>> Fait. Version du modèle servie : voir /api/health"
