"""
Code related to external processes
"""
import os
import shlex
import subprocess
import sys


def checked_call(command):
    """
    Execute command

    Wrapper around subprocess.check_output. On Posix platforms, the command passed in is split
    first, using shlex.split. Standard error output (stderr) iѕ captures on the standard output
    (stdout).
    """
    if os.name == "posix":
        command = shlex.split(command)

    return subprocess.check_output(
        command, universal_newlines=True, stderr=subprocess.STDOUT
    )


def find_python_script(script_name):
    """
    Return pathname of Python script, or `script_name` if the script could
    not be found in the places checked
    """
    python_root = os.path.dirname(sys.executable)
    root_leaves = []
    result = script_name

    if sys.platform == "win32":
        root_leaves.append("Scripts")

    if os.name == "posix":
        root_leaves.append("")

    for leave in root_leaves:
        pathname = os.path.join(python_root, leave, script_name)

        if os.path.exists(pathname):
            result = pathname
            break

    return result
