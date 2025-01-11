#!/bin/python
"""
Class to execute commands

ATTENTION: This may not work on Windows, 
as the shell commands are written for bash on linux 
and there are encoding problems between the different platforms!
"""
import os
import logging
import subprocess
import threading
from queue import Queue, Empty
from dotenv import load_dotenv
from app.commands.command import Command
from app.commands.executor import CommandExecutor


# Setup logging framework
load_dotenv()
logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                    format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


class ShellCommandExecutor(CommandExecutor):
    """
    Class to execute shell commands in a persistent shell session.
    """

    def __init__(self):
        super().__init__()
        self.shell_process = subprocess.Popen(
            [os.getenv('SHELL', '/bin/bash')],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.current_output = ""
        self._stdout_queue = Queue()
        self._stderr_queue = Queue()

        # Start threads to read from stdout and stderr
        threading.Thread(target=self._enqueue_output,
            args=(self.shell_process.stdout, self._stdout_queue), daemon=True).start()
        threading.Thread(target=self._enqueue_output,
            args=(self.shell_process.stderr, self._stderr_queue), daemon=True).start()

        # Read the initial shell prompt and send init commands
        self._send_command_to_shell(["cd ~"])


    def execute(self, command: Command) -> int:
        """
        Execute the given shell command in the persistent shell session.

        :param command: The Command object to execute.
        :return: The result of the command execution (exit code).
        """
        try:
            #self.current_output = ""
            logger.info("Execute: %s", command.cmds)
            self._send_command_to_shell(command.cmds)
            command.output = self.current_output
            if len(command.output) >100:
                logger.info("Output:  %s...", command.output[:100].replace("\n", "\\n"))
            else:
                logger.info("Output:  %s", command.output.replace("\n", "\\n"))
            command.exit_code = 0  # Shell commands don't always return standard exit codes
            return 0
        except subprocess.CalledProcessError as e:
            logger.error("Error executing command: %s; Error: %s", command.cmds, e)
            command.output = self.current_output
            command.exit_code = 1
            return 1


    def _send_command_to_shell(self, cmds):
        """
        Send commands to the persistent shell.

        :param cmds: List of shell commands to execute.
        """
        self.current_output = ""

        for cmd in cmds:
            # Command marker to signal the end of the command
            # format int as hex string
            command_marker_end = f"COMMAND_{hex(abs(hash(cmd)))}_DONE_MARKER.\n"
            if self.shell_process.stdin:
                # Write the command to the shell
                logger.debug("  STDIN:  %s", cmd)
                cmd = cmd.replace('\r\n', '\n')
                self.shell_process.stdin.write(cmd)

                # Signal the end of the command
                cmd = f"\necho {command_marker_end}\n"
                logger.debug("  STDIN:  %s",cmd)
                cmd = cmd.replace('\r\n', '\n')
                self.shell_process.stdin.write(cmd)

                # TODO: Retrieve the exit code of the command
                #    self.shell_process.stdin.write("\necho $?")

                self.shell_process.stdin.flush()

                # Read the output until the shell prompt is displayed again
                self._read_shell_output(command_marker_end)


    def _read_shell_output(self, command_marker: str):
        """
        Read combined stdout and stderr output.
        """
        while True:
            try:
                stdout_line = self._stdout_queue.get_nowait()
                logger.debug("  STDOUT: %s", stdout_line[:-1])
                if stdout_line == command_marker:
                    break
                if not stdout_line.endswith(command_marker):
                    self.current_output += stdout_line
            except Empty:
                pass

            try:
                stderr_line = self._stderr_queue.get_nowait()
                logger.warning("STDERR: %s", stderr_line[:-1])
                self.current_output += stderr_line
            except Empty:
                pass

            #if self._stdout_queue.empty() and self._stderr_queue.empty():
            #    break

        # remove the first empty line and the last empty line from self.current_output
        if self.current_output.startswith("\n"):
            self.current_output = self.current_output[1:]
        if self.current_output.endswith("\n\n"):
            self.current_output = self.current_output[:-2]


    def _enqueue_output(self, stream, queue):
        """
        Enqueue output from a given stream (stdout or stderr).
        """
        # First trial, works well in linux (but raises UnicodeDecodeError on Windows)
        for line in iter(stream.readline, ''):
            queue.put(line)

        # Second trial for windows: ignores UnicodeDecodeError and discards the line completely
#        while True:
#            try:
#                line = stream.readline()
#                if line:
#                    queue.put(line)
#                else:
#                    break
#            except (IOError, OSError, UnicodeDecodeError) as e:
#                logger.error("Error reading output from stream: %s", e)



    def close(self):
        """
        Close the persistent shell session.
        """
        if self.shell_process:
            self.shell_process.stdin.write('exit\n')
            self.shell_process.stdin.flush()
            self.shell_process.wait()


if __name__ == "__main__":
    # Attention: These commands will only work on the bash on linux
    main_executor = ShellCommandExecutor()
    # define a multi-line agent message
    MAIN_COMMANDS = ["git --version",
        "git --version && git ls-remote https://github.com",
        "# Check if git commands are installed",
        "git --version && echo \"Git is installed\" || echo \"Git is not installed\"",
        "",
        "# Check if GitHub is reachable",
        "ping -c 4 github.com",
        "ls -al"]
    # Print the parsed commands
    try:
        for main_command in MAIN_COMMANDS:
            main_cmd = Command(Command.SHELL, [main_command])
            print(f"Execute: {main_command}")
            main_executor.execute(main_cmd)
            print("---------------------------")
            print(f"Output: \n{main_cmd.output}")
            print("===========================")
    finally:
        main_executor.close()
