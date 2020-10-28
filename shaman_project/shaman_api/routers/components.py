"""Rest API endpoints for components are defined in this module."""
from typing import Dict
from .component_router import ComponentRouter
from shaman_core.models.component_model import (
    TunableComponentsModel,
    TunableParameter,
)

router = ComponentRouter()


@router.post(
    "/",
    summary="Replace the components collection by the new component in input",
    description="Replace the component collection by the post data",
    response_description="Successfully replaced components",
    status_code=202,
)
async def install_component(component: TunableComponentsModel) -> Dict:
    """Receive experiment data inside POST request and store experiment inside
    SHAMAN MongoDB database."""
    result = await router.db.update_components(component.dict())
    return {"id": str(result.upserted_id)}


@router.get(
    "/",
    summary="Get the data associated with the components,"
    "with the right format for SHAMAn.",
    description="List the different available components,"
    "with the right format for SHAMAn.",
    response_description="Successfully listed components",
    status_code=202,
)
async def list_component() -> TunableComponentsModel:
    """Get the data corresponding to the parameters."""
    components = await router.db.get_components()
    return components[0]


@router.get("/parameters")
async def components_parameters() -> Dict[str, Dict[str, TunableParameter]]:
    """Receive the parameters and their components, with the format:

    {"component_name": dict of parameters}
    """
    return await router.db.get_components_parameters()
