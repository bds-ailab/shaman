"""
Entrypoint for the ARQ worker
"""
from arq import run_worker
from .settings import WorkerSettings


def main():
    run_worker(WorkerSettings)
