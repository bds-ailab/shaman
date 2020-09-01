# Lors de la création de l'expérience, j'écris le Experiment dans la base
# Puis, à chaque pas, j'écris ce qu'il s'y passe
# Puis, à la fin j'écris les résultats finaux
from httpx import Client


API_BASE_URL = "http://localhost:5000"


class SHAManExperiment:
    def __init__(self):
        # super().__init__()
        self.api_client = Client(base_url=API_BASE_URL)
        self.experiment_id = "toto"

    def start_experiment(self):
        experiment = {"experiment_name": "tutu"}
        self.api_client.post("experiments", data=experiment)
        # requests.post(url=f"{API_URL}/experiments", json=experiment)

    def compute_step(self):
        for ix in range(10):
            experiment_step = {"perf": ix, "val": ix * 10}
            self.api_client.post(
                f"experiments/{self.experiment_id}/update", data=experiment_step
            )
            # requests.post(url=f"{API_URL}/experiments/{self.experiment_id}/update", json=experiment_step)

    def finalize_step(self):
        final_data = {"experiment_name": "tutu", "jobids": [10, 15]}
        self.api_client.post(
            f"experiments/{self.experiment_id}/update", data=final_data
        )
        # requests.post(url=f"{API_URL}/experiments/{self.experiment_id}/finish", json=final_data)
