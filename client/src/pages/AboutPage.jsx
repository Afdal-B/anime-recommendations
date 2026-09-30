import React from "react";

// --- Diagramme d'architecture -------------------------------------------------

const Node = ({ title, detail }) => (
  <div className="w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 lg:w-auto lg:flex-1">
    <p className="text-sm font-medium text-white">{title}</p>
    {detail && <p className="mt-0.5 text-xs text-slate-400">{detail}</p>}
  </div>
);

// Flèche verticale sur mobile, horizontale sur grand écran
const Arrow = () => (
  <div className="flex shrink-0 justify-center py-1 text-slate-600 lg:w-8 lg:py-0">
    <span className="lg:hidden">↓</span>
    <span className="hidden lg:inline">→</span>
  </div>
);

const Flow = ({ label, steps }) => (
  <div>
    <p className="mb-2 text-sm text-slate-400">{label}</p>
    <div className="flex flex-col lg:flex-row lg:items-stretch">
      {steps.map(([title, detail], index) => (
        <React.Fragment key={title + index}>
          {index > 0 && <Arrow />}
          <Node title={title} detail={detail} />
        </React.Fragment>
      ))}
    </div>
  </div>
);

// --- Page ----------------------------------------------------------------------

const H2 = ({ children }) => <h2 className="mb-3 mt-12 text-xl font-semibold text-white">{children}</h2>;

const AboutPage = () => (
  <article className="mx-auto max-w-3xl leading-relaxed text-slate-300">
    <h1 className="text-3xl font-bold text-white">À propos du projet</h1>
    <p className="mt-4">
      AnimeReco est un projet que nous avons réalisé pour mettre en pratique le filtrage
      collaboratif et le déploiement d'une application sur Azure. Le principe est simple : vous
      notez quelques animés que vous avez vus, et l'application vous propose ceux que vous
      devriez aimer. Vous pouvez aussi partir d'un seul anime pour trouver ceux qui plaisent aux
      mêmes spectateurs.
    </p>

    <H2>Architecture</H2>
    <div className="space-y-6 rounded-2xl bg-slate-900/40 p-5 ring-1 ring-white/5">
      <Flow
        label="Quand vous utilisez le site"
        steps={[
          ["Navigateur"],
          ["Azure Container Apps", "React + FastAPI + modèle ALS"],
          ["Azure SQL Database", "catalogue, utilisateurs, notes"],
        ]}
      />
      <Flow
        label="Quand on réentraîne le modèle"
        steps={[
          ["Vos notes", "copiées dans Blob Storage"],
          ["Azure Machine Learning", "entraînement PySpark"],
          ["Blob Storage", "nouvelle version du modèle"],
          ["Container Apps", "rechargé automatiquement"],
        ]}
      />
    </div>
    <p className="mt-4">
      Tout tourne dans un seul conteneur : l'interface React, l'API FastAPI et le modèle, gardé
      en mémoire. Les données de l'application sont dans une base Azure SQL. Vos notes sont aussi
      ajoutées au jeu d'entraînement : quand assez de nouvelles notes sont arrivées, on relance
      l'entraînement sur Azure Machine Learning, et l'application charge la nouvelle version
      d'elle-même, sans redéploiement.
    </p>

    <H2>Les services Azure</H2>
    <dl className="space-y-3">
      {[
        ["Container Apps", "héberge l'application. Le conteneur s'arrête quand il n'y a pas de trafic, ce qui limite les coûts."],
        ["Container Registry", "stocke l'image Docker de l'application."],
        ["SQL Database", "contient le catalogue d'animés, les comptes et les notes."],
        ["Blob Storage", "garde les notes utilisées pour l'entraînement et chaque version du modèle."],
        ["Machine Learning", "exécute l'entraînement sur un cluster qui ne démarre que pour l'occasion."],
      ].map(([name, role]) => (
        <div key={name}>
          <dt className="inline font-medium text-white">{name}</dt>
          <dd className="inline"> : {role}</dd>
        </div>
      ))}
    </dl>

    <H2>Le modèle</H2>
    <p>
      Nous sommes partis du jeu de données MyAnimeList publié sur Kaggle en 2023, en nous
      limitant aux 30&nbsp;000 premiers utilisateurs. Nous avons retiré les notes à -1, qui
      signifient qu'un utilisateur a vu l'anime sans le noter.
    </p>
    <p className="mt-4">
      Le modèle est un ALS (Alternating Least Squares) entraîné avec PySpark. Il apprend, pour
      chaque utilisateur et chaque anime, un vecteur de 10 nombres, de façon à ce que leur
      produit se rapproche de la note donnée. Ces vecteurs ne viennent que des notes : le modèle
      ne lit ni les genres ni les synopsis. Au final, il couvre 27&nbsp;612 utilisateurs et 17&nbsp;554
      animés.
    </p>
    <p className="mt-4">
      Pour trouver les animés similaires, on compare le vecteur de l'anime choisi à celui de tous
      les autres (similarité cosinus) et on garde les plus proches.
    </p>
    <p className="mt-4">
      Pour vos recommandations personnelles, pas besoin de réentraîner le modèle : on garde les
      vecteurs des animés tels quels et on calcule le vôtre à partir de vos notes, au moment où
      vous les demandez. C'est la moitié d'une étape d'ALS, soit un petit calcul de moindres
      carrés. Nous avons vérifié que ce calcul retrouve exactement les vecteurs appris par Spark
      pour les utilisateurs du jeu de données. On vous propose ensuite les animés que ce vecteur
      prédit que vous noteriez le mieux.
    </p>
    <p className="mt-4">
      L'entraînement se fait avec Spark, mais pas le service. Notre première version chargeait
      Spark à chaque requête et n'a jamais tenu en production. Or, une fois entraîné, le modèle
      se réduit à deux tableaux de vecteurs, qu'on lit simplement avec NumPy.
    </p>

    <H2>Limites</H2>
    <p>
      Vos notes changent vos recommandations tout de suite, mais pas les vecteurs des animés :
      ceux-ci n'évoluent qu'au réentraînement, que nous lançons à la main. Avec seulement une ou
      deux notes, vos recommandations restent approximatives. Et un anime qui a reçu peu de
      notes a un vecteur moins fiable, ce qui peut donner quelques suggestions surprenantes.
    </p>

    <p className="mt-12 border-t border-white/5 pt-6 text-sm text-slate-500">
      Python, FastAPI, PySpark, NumPy, React, Tailwind CSS, Docker, Azure.
    </p>
  </article>
);

export default AboutPage;
