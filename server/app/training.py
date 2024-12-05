from azureml.core import Workspace
from azureml.core import Experiment
from azureml.core import ScriptRunConfig

def trigger_training():
    # Connexion à l'espace de travail Azure ML
    workspace = Workspace(subscription_id="179eb1ef-d1c6-4004-b3d9-4d1270fa28c5",resource_group="Final_Project",workspace_name="Anime_recommendation")  # Assurez-vous d'avoir un fichier config.json ou d'utiliser les paramètres appropriés

    # Créer un nouvel essai
    experiment = Experiment(workspace, "anime_recommendation_experiment")

    # Configuration du script d'entraînement
    config = ScriptRunConfig(source_directory='Users/bouraima1u/recommendation_nb/train_als.py',  # Chemin vers votre script d'entraînement
                             script='train_als.py',  # Nom de votre script d'entraînement
                             compute_target='bouraima1u1')  # Nom de votre cible de calcul

    # Soumettre l'essai
    run = experiment.submit(config)
    run.wait_for_completion(show_output=True)

#trigger_training()