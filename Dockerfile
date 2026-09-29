# --- Étape 1 : build du front React ---
FROM node:20-alpine AS client
WORKDIR /client
COPY client/package.json client/package-lock.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

# --- Étape 2 : API FastAPI + fichiers statiques ---
FROM python:3.11-slim-bookworm

# Driver ODBC Microsoft pour Azure SQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg ca-certificates \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc \
    && apt-get purge -y curl gnupg && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/server/app
COPY server/app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server/app/ ./
COPY server/models/unzipped/als_model.zip /srv/server/models/unzipped/als_model.zip
COPY --from=client /client/build ./static
# Script d'initialisation de la base (lancé une fois : python /srv/server/seed_db.py)
COPY server/seed_db.py server/schema.sql /srv/server/
COPY server/data/anime-dataset-2023.csv /srv/server/data/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
