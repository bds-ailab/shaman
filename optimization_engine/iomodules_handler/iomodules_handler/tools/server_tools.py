"""
This module contains different tools to interact with the server.
"""

__copyright__ = """
Copyright (C) 2019 Bull S. A. S. - All rights reserved
Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois, France
This is not Free or Open Source software.
Please contact Bull S. A. S. for details about its license.
"""

import subprocess
from shlex import split


def string_in_output(command, string):
    """This function checks if a string is located in the output of a bash command.

    Args:
        command (str): The command to run.
        string (str): The string to look for.

    Returns:
        A boolean which indicates if the string is located in the output of the bash command.
    """
    cmd = split(command)
    sub_ps = subprocess.run(cmd, stdout=subprocess.PIPE, shell=False)
    ps_stdout = sub_ps.stdout.decode()
    return string in ps_stdout and sub_ps.returncode == 0


def check_slurm_queue_name(job_name):
    """Returns true if the job called job_name is in the slurm queue.
    Note that the maximum length for the squeue slurm name is set to 8
    and this function truncates the job_name if it exceeds this number of
    characters.

    Args:
        job_name (str): The name of the job.

    Returns:
        A boolean indicating whether or not the slurm job is running.
    """
    return string_in_output("squeue", job_name[:8])


def check_slurm_queue_id(job_id):
    """Returns true if the job whose id is job_id is in the slurm queue.

    Args:
        job_id (int): The ID of the job.

    Returns:
        A boolean indicating whether or not the slurm job is running.
    """
    try:
        return string_in_output("squeue", str(int(job_id)))
    except TypeError:
        raise TypeError("Job id must be an integer.")


def check_rpm_installed(rpm_name):
    """Checks if the rpm rpm_name is installed on the machine.
    Args:
        rpm_name (String): the name of the rpm to check the install for.

    Returns:
        True if the rpm is installed on the machine.
    """
    return string_in_output("rpm -qa", rpm_name)
