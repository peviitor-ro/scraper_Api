import subprocess

import subprocess

def run_process(command, path):
    """
    Run a process with the given command in the specified path.

    Args:
        command (list): The command to execute.
        path (str): The path where the process should be run.

    Returns:
        tuple: A tuple containing the stdout (str), stderr (str), and return code (int) of the process.
    """
    process = subprocess.Popen(command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return (stdout.decode('utf-8'), stderr.decode('utf-8'), process.returncode)