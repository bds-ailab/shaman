""" Tasks for shaman_worker project. """
from pathlib import Path
from shutil import rmtree

from invoke import task

PROJECT_DIR = Path(__file__).parent

SRC_DIR = PROJECT_DIR / "shaman_project"
TESTS_DIR = PROJECT_DIR / "tests"
DIST_DIR = PROJECT_DIR / "dist"


@task(
    help={
        "package": "Which package to lint. If 'all', all packages are linted, else only given package. Default to 'all'.",
        "test": "Perform linting also on test files. This is True by default. Use '--no-test' to disable this feature.",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def lint(c, package="all", test=True, dry_run=False):
    """Lint all source code or a single package."""
    if package == "all":
        cmd = f"flake8 {SRC_DIR} tasks.py"
        if test:
            cmd += f" {TESTS_DIR}"
    else:
        cmd = f"flake8 {str(SRC_DIR / package)} tasks.py"
        if test:
            cmd += f" {str(TESTS_DIR / package)}"
    if dry_run:
        print(cmd)
        return
    c.run(cmd)


@task(
    help={
        "package": "Which package to test. If 'all', all packages are tested, else only given package. Default to 'all'.",
        "coverage": "Collect test coverage and write XML, HTML and TERM reports. Use '--no-coverage' to disable this feature.'",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def test(c, package="all", coverage=True, dry_run=False):
    """Run unit tests with pytest for a single one or all packages."""
    cmd = "pytest "
    if package == "all":
        if coverage:
            cmd += (
                "--cov-report=xml:cov.xml "
                "--cov-report=html:coverage-report "
                "--cov-report=term-missing "
                "--cov-branch "
                "--cov=shaman_project "
            )
        cmd += "--ignore=tests/bb_wrapper/integration tests/"
    else:
        if coverage:
            cmd += (
                f"--cov-report=xml:{package}.cov.xml "
                f"--cov-report=html:{package}-coverage-report "
                "--cov-report=term-missing "
                "--cov-branch "
                f"--cov=shaman_project/{package} "
            )
        cmd += f"tests/{package}/unit"
    if dry_run:
        print(cmd)
        return
    c.run(cmd)


@task(
    help={
        "package": "Which package to format. If 'all', all packages are formatted, else only given package. Default to 'all'.",
        "test": "Perform formatting also on test files. This is True by default. Use '--no-test' to disable this feature.",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def format(c, package="all", test=True, dry_run=False):
    """Format all source code or a single package."""
    if package == "all":
        cmd = f"black {SRC_DIR} tasks.py"
        if test:
            cmd += f" {TESTS_DIR}"
    else:
        cmd = f"black {str(SRC_DIR / package)} tasks.py"
        if test:
            cmd += f" {str(TESTS_DIR / package)}"
    if dry_run:
        print(cmd)
        return
    c.run(cmd)


@task
def build(c):
    """Build the shaman-project python wheel."""
    c.run("poetry build")


@task
def build_ui(c):
    """Build the shaman-project user interface application."""
    with c.cd("frontend"):
        c.run("npm run build")


@task
def clean(c):
    """Clean the build artefacts."""
    rmtree(PROJECT_DIR / "dist", ignore_errors=True)
    rmtree(PROJECT_DIR / "frontend" / ".nuxt" / "dist", ignore_errors=True)


@task(
    help={
        "host": "The bind host. Default to 'localhost'.",
        "port": "The bind port. Default to '5000'.",
        "mongo-host": "The MongoDB server host. Default to 'localhost'.",
        "mongo-port": "The MongoDB server listenning port. Default to '27017'",
        "reload": (
            "Enable hot-reloading for development. "
            "This is enabled by default. Use '--no-reload' to disable this feature."
        ),
        "asyncio-debug": "Enable asyncio debug mode. See https://docs.python.org/3/library/asyncio-dev.html#debug-mode.",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def api(
    c,
    host="localhost",
    port=5000,
    mongo_host="localhost",
    mongo_port=27017,
    jaeger_host="localhost",
    reload=True,
    asyncio_debug=True,
    dry_run=False,
):
    """Start the SHAMan API in foreground. The API listens on host localhost and port 5000 with hot-reload enabled by default."""
    cmd = (
        f"PYTHONASYNCIODEBUG=1 "
        f"shaman_mongodb_host={mongo_host} "
        f"shaman_mongodb_port={mongo_port} "
        f"jaeger_host={jaeger_host} "
        f"uvicorn shaman_api:app {'--reload' if reload else ''}"
    )
    if dry_run:
        print(cmd)
        return
    c.run(cmd)


@task(
    help={
        "reload": (
            "Enable hot-reloading for development. "
            "This is enabled by default. Use '--no-reload' to disable this feature."
        ),
        "asyncio-debug": "Enable asyncio debug mode. See https://docs.python.org/3/library/asyncio-dev.html#debug-mode.",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def worker(c, watch=True, asyncio_debug=True, dry_run=False):
    """Start the SHAMan Worker in foreground with hot-reload enabled by default."""
    cmd = "PYTHONASYNCIODEBUG=1 arq "
    if watch:
        cmd += f"--watch {str(SRC_DIR / 'shaman_worker')} "
    cmd += "shaman_worker.Settings"
    if dry_run:
        print(cmd)
        return
    c.run(cmd)


@task(
    help={
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def ui(c, dry_run=False):
    """Start the SHAMan UI in foreground. The UI listens on host localhost and port 3000 with hot reloading by default."""
    cmd = "npm run dev"
    if dry_run:
        print(cmd)
        return
    with c.cd("frontend"):
        c.run("npm run dev")


@task(
    help={
        "port": "Published redis port on host network. Default to '6379'.",
        "name": "Name of redis container. Default to 'shaman-redis'.",
        "interactive": "Run the container with interactive tty. By default the container runs in detach mode.",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
    }
)
def redis(
    c,
    port=6379,
    name="shaman-redis",
    interactive=False,
    start=False,
    stop=False,
    dry_run=False,
):
    """Start a Redis server in a docker container."""
    if start:
        cmd = f"docker start {'-i' if interactive else ''}  {name}"
    elif stop:
        cmd = f"docker stop {name}"
    else:
        cmd = f"docker run --name {name} {'-it' if interactive else '-d'} -p {port}:6379 redis:latest"
    if dry_run:
        print(cmd)
        return
    c.run(cmd)


@task(
    help={
        "port": "Published MongoDB port on host network. Default to '27017'.",
        "name": "Name of MongoDB container. Default to 'shaman-mongo'.",
        "interactive": "Run the container with interactive tty. By default the container runs in detach mode.",
        "dry-run": "Use '--dry-run' to print command that would have been executed to terminal and stop the program.",
        "start": "Do not create the container but simply start it.",
        "stop": "Stop the running container.",
    }
)
def mongo(
    c,
    port=27017,
    name="shaman-mongo",
    interactive=False,
    dry_run=False,
    start=False,
    stop=False,
):
    """Create and run a MongoDB database in a docker container."""
    if start:
        cmd = f"docker start {name}"
    elif stop:
        cmd = f"docker stop {name}"
    else:
        cmd = f"docker run --name {name} {'-it' if interactive else '-d'} -p {port}:27017 mongo:latest"
    if dry_run:
        print(cmd)
        return
    c.run(cmd)
