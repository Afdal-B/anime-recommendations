-- Schéma de la base Azure SQL utilisée par l'API
-- Les utilisateurs de l'application commencent à 10 000 000 pour ne pas se mélanger,
-- au réentraînement, avec ceux du jeu MyAnimeList (0 à 30 000).
CREATE TABLE users (
    user_id  INT IDENTITY(10000000, 1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL
);
-- Un pseudo = un profil (comparaison insensible à la casse avec la collation par défaut)
CREATE UNIQUE INDEX ux_users_username ON users (username);

CREATE TABLE animes (
    anime_id  INT PRIMARY KEY,
    name      NVARCHAR(500) NOT NULL,
    image_url NVARCHAR(1000),
    synopsis  NVARCHAR(MAX),
    genres    NVARCHAR(500),
    score     FLOAT
);
CREATE INDEX ix_animes_score ON animes (score DESC);

CREATE TABLE ratings (
    rating_id  INT IDENTITY(1, 1) PRIMARY KEY,
    user_id    INT NOT NULL,
    anime_id   INT NOT NULL,
    rating     INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE recommendations (
    recommendation_id INT IDENTITY(1, 1) PRIMARY KEY,
    user_id           INT NOT NULL,
    anime_id          INT NOT NULL,
    created_at        DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
