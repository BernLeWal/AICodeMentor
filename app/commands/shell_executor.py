#!/bin/python
"""
Class to execute commands
"""
import logging
import subprocess
import threading
from queue import Queue, Empty
from app.commands.command import Command
from app.commands.executor import CommandExecutor

# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class ShellCommandExecutor(CommandExecutor):
    """
    Class to execute shell commands in a persistent shell session.
    """

    SHELL_BASH = '/bin/bash'
    SHELL_SH = '/bin/sh'
    SHELL_POWERSHELL = 'powershell'
    SHELL_CMD = 'cmd.exe'

    COMMAND_END = "DONE.\n"

    def __init__(self, shell: str = SHELL_BASH):
        super().__init__()
        self.shell_interpreter = shell
        self.shell_process = subprocess.Popen(
            [shell],
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

        # Read the initial shell prompt
        self.shell_process.stdin.write(f"\necho {self.COMMAND_END}")
        self.shell_process.stdin.flush()
        self._read_shell_output()


    def execute(self, command: Command) -> int:
        """
        Execute the given shell command in the persistent shell session.

        :param command: The Command object to execute.
        :return: The result of the command execution (exit code).
        """
        try:
            #self.current_output = ""
            self._send_command_to_shell(command.cmds)
            command.output = self.current_output
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
            if self.shell_process.stdin:
                # Write the command to the shell
                self.shell_process.stdin.write(cmd)
                # Signal the end of the command
                self.shell_process.stdin.write(f"\necho {self.COMMAND_END}")
                # Retrieve the exit code of the command
                #if self.shell_interpreter == self.SHELL_CMD:
                #    self.shell_process.stdin.write("\necho %ERRORLEVEL%")
                #elif self.shell_interpreter == self.SHELL_POWERSHELL:
                #    self.shell_process.stdin.write("\n$LASTEXITCODE")
                #elif self.shell_interpreter == self.SHELL_BASH or self.shell_interpreter == self.SHELL_SH:
                #    self.shell_process.stdin.write("\necho $?")

                self.shell_process.stdin.flush()

                # Read the output until the shell prompt is displayed again
                self._read_shell_output()


    def _read_shell_output(self):
        """
        Read combined stdout and stderr output.
        """
        while True:
            try:
                stdout_line = self._stdout_queue.get_nowait()
                logger.debug("  STDOUT: %s", stdout_line[:-1])
                if stdout_line == self.COMMAND_END:
                    break
                if not stdout_line.endswith(self.COMMAND_END):
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
        for line in iter(stream.readline, ''):
            queue.put(line)


    def close(self):
        """
        Close the persistent shell session.
        """
        if self.shell_process:
            self.shell_process.stdin.write('exit\n')
            self.shell_process.stdin.flush()
            self.shell_process.wait()

if __name__ == "__main__":
    # Attention: These commands will only work on the cmd.exe shell on windows
    main_commands = [
        'echo Hello, World!',
        'set VAR=PersistentShell',
        'echo %VAR%',
        'cd ..',
        'cd',
        'pwd',  # This will fail in cmd.exe, testing stderr capture
    ]

    main_executor = ShellCommandExecutor(ShellCommandExecutor.SHELL_CMD)
    try:
        for main_command in main_commands:
            main_cmd = Command(Command.SHELL, [main_command])
            print(f"Execute {main_cmd.cmds}")
            main_executor.execute(main_cmd)
            print(f"Output: \n{main_cmd.output}")
    finally:
        main_executor.close()

    print("Done.")
