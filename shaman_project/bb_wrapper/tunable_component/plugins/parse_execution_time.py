"""
This module contains functions to perform the parsing of output files
and returns an execution time.
"""
import re
from pathlib import Path


def parse_milliseconds(string_time: str) -> float:
    """Given a string date with the format MMmSS.MSs (as returned by the
        linux time command), parses it to seconds.

        Args:
            string_time (str): The date to parse

        Returns:
            The number of elapsed seconds
        """
    minutes = int(string_time.split("m")[0])
    string_time = string_time.replace(str(minutes) + "m", "")
    seconds = int(string_time.split(".")[0])
    milliseconds_string = string_time.split(".")[1]
    milliseconds_string = milliseconds_string.replace("s", "")
    milliseconds = int(milliseconds_string)
    return minutes * 60 + seconds + milliseconds / 1000


def parse_slurm_times(job_id: str, path: Path = Path.cwd()) -> float:
    """Performs the parsing of the file slurm-{job_id}.out by returning
    in milliseconds the time measured by Slurm.

    Args:
        out_file (str): The job slurm output file path to parse.
        path (Path): The path where to look for the slurm output.
            Defaults to the current working directory.

    Returns:
        float: The time elapsed by the application, in milliseconds.
    """
    real_time = None
    out_file = path / f"slurm-{job_id}.out"
    try:
        with open(out_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("real"):
                    time = re.split("\t", line)[-1].strip()
                    real_time = parse_milliseconds(time)
                    if real_time:
                        return real_time
        raise ValueError(
            "Could not parse time of slurm output,"
            f"content set to {real_time} !"
        )
    except FileNotFoundError:
        raise FileNotFoundError("Slurm output was not generated.")
