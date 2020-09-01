from fastapi import FastAPI
from .routers import experiment_router, ioi_router

from fastapi.middleware.cors import CORSMiddleware


# origins = [
#     "http://localhost:3000",
#     "https://localhost:3000",
# ]


app = FastAPI(
    title="SHAMan API",
    version="1.0.2",
    description="A REST API to interact with SHAMan Optimization Engine",
)


app.include_router(ioi_router, prefix="/io_durations", tags=["IO durations"])
app.include_router(experiment_router, prefix="/experiments",
                   tags=["Experiments"])

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origin_regex='http?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
