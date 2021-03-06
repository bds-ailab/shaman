"""This module contains functions to perform the parsing of a slurm output
generated by the OSU benchmark.
"""
from pathlib import Path


def parse_osu_output(job_id: str, path: Path = Path.cwd()) -> float:
    """Performs the parsing of the file slurm-{job_id}.out by returning
    the sums of the elapsed time multiplied by the size of the messages.

    Args:
        out_file (str): The job slurm output file path to parse.
        path (Path): The path where to look for the slurm output.
            Defaults to the current working directory.

    Returns:
        float: The time elapsed by the application, in milliseconds.
    """
    elapsed_time = 0
    out_file = path / f"slurm-{job_id}.out"
    try:
        with open(out_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.split()
                if split_line:
                    try:
                        size, latency = float(
                            split_line[0]), float(
                            split_line[1])
                        elapsed_time += size * latency
                    except ValueError:
                        continue
            return elapsed_time
    except FileNotFoundError:
        raise FileNotFoundError("Slurm output was not generated.")


def parse_osu_output_1024(job_id: str, path: Path = Path.cwd()) -> float:
    """Performs the parsing of the file slurm-{job_id}.out by returning
    the elapsed time.

    Args:
        out_file (str): The job slurm output file path to parse.
        path (Path): The path where to look for the slurm output.
            Defaults to the current working directory.

    Returns:
        float: The time elapsed by the application, in milliseconds.
    """
    elapsed_time = 0
    out_file = path / f"slurm-{job_id}.out"
    try:
        with open(out_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.split()
                if split_line:
                    try:
                        size, latency = float(
                            split_line[0]), float(
                            split_line[1])
                        if size == 1024:
                            return latency
                    except ValueError:
                        continue
            return elapsed_time
    except FileNotFoundError:
        raise FileNotFoundError("Slurm output was not generated.")


def parse_osu_output_8(job_id: str, path: Path = Path.cwd()) -> float:
    """Performs the parsing of the file slurm-{job_id}.out by returning
    the elapsed time.

    Args:
        out_file (str): The job slurm output file path to parse.
        path (Path): The path where to look for the slurm output.
            Defaults to the current working directory.

    Returns:
        float: The time elapsed by the application, in milliseconds.
    """
    elapsed_time = 0
    out_file = path / f"slurm-{job_id}.out"
    try:
        with open(out_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.split()
                if split_line:
                    try:
                        size, latency = float(
                            split_line[0]), float(
                            split_line[1])
                        if size == 8:
                            return latency
                    except ValueError:
                        continue
            return elapsed_time
    except FileNotFoundError:
        raise FileNotFoundError("Slurm output was not generated.")


def parse_osu_output_1048576(job_id: str, path: Path = Path.cwd()) -> float:
    """Performs the parsing of the file slurm-{job_id}.out by returning
    the elapsed time.

    Args:
        out_file (str): The job slurm output file path to parse.
        path (Path): The path where to look for the slurm output.
            Defaults to the current working directory.

    Returns:
        float: The time elapsed by the application, in milliseconds.
    """
    elapsed_time = 0
    out_file = path / f"slurm-{job_id}.out"
    try:
        with open(out_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.split()
                if split_line:
                    try:
                        size, latency = float(
                            split_line[0]), float(
                            split_line[1])
                        if size == 1048576:
                            return latency
                    except ValueError:
                        continue
            return elapsed_time
    except FileNotFoundError:
        raise FileNotFoundError("Slurm output was not generated.")
