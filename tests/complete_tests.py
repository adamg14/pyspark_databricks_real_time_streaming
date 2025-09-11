# local development tests
import sys
import subprocess

def run_terminal_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"Test passed successfully for command: { command }")
    else:
        print(f"Test failed for the command { command }. Error: {result.stderr}")


def main():
    command_line_tests = [
        # syntax check for pipeline code
        ("python -m py_compile pipeline/*.py"),
        # syntax test for ingestion code
        ("python -m py_compile ingestion/*.py")
    ]
    
    for command in command_line_tests:
        run_terminal_command(command=command)

if __name__ == '__main__':
    main()