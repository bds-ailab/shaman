"""
Provides utils functions for remote manipulations of a remote server (running a Linux distribution).

!!! The node running this script must have the ssh keys of the remote server in its authorized keys.
"""
import subprocess
import logging
import time
from shlex import split

from .server_tools import string_in_output


def check_authorized(server_name, user="root"):
    """Checks that the server running this function is among the authorized server in the
    ssh configuration file.

    Args:
        server_name (str): The name of the server.
        user (str, optional): The name of the user to use. Defaults to "root".

    Returns:
        A boolean which indicate if the server is authorized to run.
    """
    _cmd = split(f"ssh {user}@{server_name} hostname")
    ps = subprocess.run(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    connect_msg = "password"
    if connect_msg in ps.stderr.decode() or connect_msg in ps.stdout.decode():
        return False
    return True


def check_process(process):
    """
    Checks if the process process_name is running on a remote server.

    Args:
        process (): A process.
    Returns:
        is_running (bool): Whether or not the process is indeed running
    """
    is_running = False
    if process.poll() is None:
        is_running = True
    return is_running


def check_process_by_name(server, process_name, user="root"):
    """
    Checks if the process process_name is running on a remote server.

    Args:
        server_name (str): The name or the IP of the server on which to run the command
        process_name (str): The name of the process to check for

    Returns:
        is_running (bool): Whether or not the process is indeed running
    """
    logging.info("Check that the process %s is running on the remote host "
                 "%s ...", process_name, server)
    cmd = f"ssh {user}@{server} ps -aux"
    return string_in_output(cmd, process_name)


def check_process_by_pid(server, pid, user="root"):
    """
    Checks if the process with the PID pid is running on a remote server.

    Args:
        server_name (str): The name or the IP of the server on which to run the command
        pid(str): The PID of the process to check for

    Returns:
        is_running (bool): Whether or not the process is indeed running
    """
    logging.info("Check that the process %s is running on the remote host "
                 "%s ...", pid, server)
    cmd = f"ssh {user}@{server} ps -o pid= -p {pid}"
    return string_in_output(cmd, pid)


def run_command(server, cmd, user="root"):
    """Run the command cmd on the server. Returns the process and the PID.
    Args:
        server (str): The name on the server
        cmd (str): The command to run
        user (str, optional): The user to use for running the command. Defaults to "root".
    Returns:
        The stdout, the stderr and the exit code of the process.
    """
    command = split(f"ssh {user}@{server} {cmd}")
    ps = subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    return ps


def run_and_get_pid(server, cmd, user="root"):
    """Run the command cmd on the server and get the PID of the generated process.
    Args:
        server (str): The name or IP of the server
        cmd (str): The command to run
        user (str, optional): The user that should run the command. Defaults to "root".
    """
    command = f'"sh -c \'echo $$ ; exec {cmd}\'"'
    ps = run_command(server, command, user)
    for stdout_line in iter(ps.stdout.readline, ""):
        pid = int(stdout_line.decode().strip())
        break
    return str(pid)


def kill_process(process, timeout=20):
    """
    Kills process process_name on server server_name.

    Args:
        process (): The process to kill.
    Returns:
        Whether or not the process is killed.
    """
    logging.info("Proceeding to kill process ...")
    process.kill()
    # Wait until timeout duration for process to be killed
    elapsed_time = 0
    start_time = time.time()
    while elapsed_time < timeout:
        # If process is ended exit the function
        if check_process(process):
            elapsed_time = time.time() - start_time
        else:
            return True
    _msg = "Could not kill process."
    logging.error(_msg)
    raise TimeoutError(_msg)


def kill_process_by_pid(server, pid, user="root"):
    """
    Kills process given a pid on server server_name.

    Args:
        server (str): The name or the IP of the server.
        pid (int): The pid of the process
        user (str, optional): The user to use for launching the command.
            Defaults to root.

    Returns:
        Whether or not the process is killed.
    """
    _ = run_command(server, f"kill {pid}", user)
    timeout_counter = 0
    while check_process_by_pid(server, pid, user) and timeout_counter < 30:
        time.sleep(0.1)
        timeout_counter += 1
    if timeout_counter >= 30:
        _ = run_command(server, f"kill -9 {pid}", user)
        timeout_counter = 0
        while check_process_by_pid(server, pid, user) and timeout_counter < 10:
            time.sleep(0.1)
            timeout_counter += 1
        return timeout_counter < 10
    return True


def kill_process_by_name(server, process_name, user="root"):
    """
    Kills process given a pid on server server_name.

    Args:
        server (str): The name or the IP of the server.
        process_name (str): The name of the process
        user (str, optional): The user to use for launching the command.
            Defaults to root.

    Returns:
        Whether or not the process is killed.
    """
    _ = run_command(server, f"killall {process_name}", user)
    timeout_counter = 0
    while check_process_by_name(server, process_name, user) and timeout_counter < 30:
        time.sleep(0.1)
        timeout_counter += 1
    if timeout_counter >= 30:
        _ = run_command(server, f"killall -9 {process_name}", user)
        timeout_counter = 0
        while check_process_by_name(server, process_name, user) and timeout_counter < 10:
            time.sleep(0.1)
            timeout_counter += 1
        return timeout_counter < 10
    return True
