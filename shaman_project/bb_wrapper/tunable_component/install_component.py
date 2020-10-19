"""This module sends data read from an input YAML file to a POST endpoint /components, which creates
a collection containing the available components.
"""
from httpx import Client
from typer import Typer, Argument

from shaman_core.models.component_model import TunableComponentsModel
from ..shaman_settings import SHAManSettings

cli = Typer(add_completion=False)
shaman_settings = SHAManSettings()


@cli.command()
def install_component(
    component_file: str = Argument(
        ..., help="The path to the component file containing the data"
    )
):
    """
    Function to install a component:
        - Takes as input a YAML file
        - Parses it as a dictionary through the Pydantic model TunableComponentsModel
        - Send it as a POST request to /components
    """
    api_client = Client(
        base_url=f"http://{shaman_settings.api_host}:{shaman_settings.api_port}",
        proxies={},
    )
    component = TunableComponentsModel.from_yaml(component_file)
    request = api_client.post(shaman_settings.component_endpoint, json=component.dict())
    print("Successfully registered components.")
    if not 200 <= request.status_code < 400:
        raise Exception(
            f"Could not create component with status code {request.status_code}"
        )


if __name__ == "__main__":
    cli()
