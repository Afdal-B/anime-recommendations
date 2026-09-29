import asyncio
import os
import shutil
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from model_store import download_model, latest_model_version
from recommender import ALSRecommender, DEFAULT_MODEL_PATH
from routes import router

# Dossier du build React (servi par l'API en production)
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(__file__), "static"))
# Fréquence de vérification d'un nouveau modèle dans Blob Storage
MODEL_REFRESH_SECONDS = int(os.getenv("MODEL_REFRESH_SECONDS", 3600))


def load_latest_model(app: FastAPI):
    """Charge le dernier modèle de Blob Storage s'il a changé.

    Sans Blob Storage (ou en cas d'erreur), on garde le modèle actuel, et au
    démarrage on se rabat sur le modèle intégré à l'image.
    """
    try:
        version = latest_model_version()
        if version and version != getattr(app.state, "model_version", None):
            path = download_model(version)
            app.state.recommender = ALSRecommender(path)
            shutil.rmtree(path, ignore_errors=True)  # Les facteurs sont en mémoire
            app.state.model_version = version
            print(f"Modèle chargé depuis Blob Storage : {version}")
    except Exception as e:
        print(f"Impossible de charger le modèle depuis Blob Storage : {e}")

    if not hasattr(app.state, "recommender"):
        app.state.recommender = ALSRecommender(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
        app.state.model_version = "image"
        print("Modèle intégré à l'image chargé.")


async def refresh_model_periodically(app: FastAPI):
    while True:
        await asyncio.sleep(MODEL_REFRESH_SECONDS)
        await asyncio.to_thread(load_latest_model, app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_latest_model(app)
    refresh_task = asyncio.create_task(refresh_model_periodically(app))
    yield
    refresh_task.cancel()
    with suppress(asyncio.CancelledError):
        await refresh_task


app = FastAPI(lifespan=lifespan)

# CORS utile uniquement si le front est servi depuis une autre origine
allowed_origins = [o for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclure les routes
app.include_router(router)

# Servir le front React : fichiers statiques puis index.html pour les routes du client
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=os.path.join(STATIC_DIR, "static")), name="static")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        static_root = os.path.realpath(STATIC_DIR)
        file_path = os.path.realpath(os.path.join(static_root, full_path))
        if file_path.startswith(static_root + os.sep) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# Commande pour lancer FastAPI (uvicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
