"""This module sends data read from an input YAML file to a POST endpoint /components, which creates
a collection containing the available components.
"""
from httpx import Client
import typer import Typer
import Option

from .component_model import TunableComponentsModel


cli = Typer(add_completion=False)


@cli.command()
def install_component(component_file: str = Option(..., help="The path to the component file containing the data"),
                      api_host: str = Option(..., help="The host of the API"),
                      api_port: str = Option(..., help="The port of the API")):
    """
    Function to install a component:
        - Takes as input a YAML file
        - Parses it as a dictionary through the Pydantic model TunableComponentsModel
        - Send it as a POST request to /components
    """
    api_client = Client(base_url=f"{api_host}:{api_port}", proxies={})
    component = TunableComponentModel.from_yaml(component_file)
    request = api_client.post("components", json=component.dict())
    if not 200 <= request.status_code < 400:
        raise Exception(
            f"Could not create component with status code {request.status_code}")


if __name__ == "__main__":
    cli()
