from fastapi import FastAPI
from .routers import experiment_router, component_router

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="SHAMan API",
    version="1.0.2",
    description="A REST API to interact with SHAMan Optimization Engine",
)


app.include_router(experiment_router, prefix="/experiments", tags=["Experiments"])
app.include_router(component_router, prefix="/components", tags=["Components"])

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origin_regex="http?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
