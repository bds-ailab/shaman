from multiprocessing import Process
from subprocess import run, PIPE
from time import sleep
import pytest
from typer.testing import CliRunner
import httpx

from shaman_api import cli


runner = CliRunner()


@pytest.fixture
def run_dev_server():
    """
    This function is not considered by coverage. We cannot achieve 100% covergae until this is resolved.
    It seems quite tricky. See https://coverage.readthedocs.io/en/coverage-5.0.4/subprocess.html#signal-handlers-and-atexit
    """
    PORT = str(9999)
    # Create process that will run dev command with a custom port
    proc = Process(
        target=runner.invoke, args=(cli, ["dev", "--port", PORT]), daemon=False
    )
    # Start process
    proc.start()
    # Wait for FastAPI server to start
    sleep(1)
    # At this point tests will be run
    yield
    # Once test is finished, kill process
    while proc.is_alive():
        proc.kill()
    # And close process
    proc.close()
    # The above command does not kill child processes so we must do it manually
    # First run lsof command to find PID of listenning process
    lsof_process = run(["lsof", "-i", f":{PORT}"], stdout=PIPE)
    # Then parse output of command
    output_dict = dict(
        list(zip(*[line.split() for line in lsof_process.stdout.decode().splitlines()]))
    )
    # And kill process with SIGKILL signal
    run(["kill", "-9", output_dict["PID"]])


@pytest.fixture
def run_prod_server():
    """
    This function is not considered by coverage. We cannot achieve 100% covergae until this is resolved.
    It seems quite tricky. See https://coverage.readthedocs.io/en/coverage-5.0.4/subprocess.html#signal-handlers-and-atexit
    """
    PORT = str(9998)
    WORKERS = str(4)
    # Create process that will run dev command with a custom port
    proc = Process(
        target=runner.invoke,
        args=(cli, ["prod", "--port", PORT, "--workers", WORKERS]),
        daemon=False,
    )
    # Start process
    proc.start()
    # Wait for FastAPI server to start
    sleep(2)
    # At this point tests will be run
    yield
    # Once test is finished, kill process
    while proc.is_alive():
        proc.kill()
    # And close process
    proc.close()
    # The above command does not kill child processes so we must do it manually
    # First run lsof command to find PID of listenning process
    lsof_process = run(["lsof", "-i", f":{PORT}"], stdout=PIPE)
    # Then parse output of command
    output = lsof_process.stdout.decode().splitlines()
    # This is a little different from above because we start the appplication with 2 workers
    # So we get 3 lines: 1 header line and 2 lines with pids
    # Let's get the header first
    header = output.pop(0)
    # And then parse the PIDs
    pids = [dict(list(zip(header.split(), line.split())))["PID"] for line in output]
    # Ensure that we get two PIDs
    assert len(pids) == int(WORKERS)
    # And kill process with SIGKILL signal
    for pid in pids:
        run(["kill", "-9", pid])


def test_dev_command_help():
    result = runner.invoke(cli, ["dev", "--help"])
    assert result.exit_code == 0
    assert "Run the application in development mode." in result.stdout


def test_dev_command(run_dev_server):
    response = httpx.get("http://localhost:9999/openapi.json")
    assert response.status_code == 200


def test_prod_command_help():
    result = runner.invoke(cli, ["prod", "--help"])
    assert result.exit_code == 0
    assert "Run the application in production mode." in result.stdout


def test_prod_command(run_prod_server):
    response = httpx.get("http://localhost:9998/openapi.json")
    assert response.status_code == 200
