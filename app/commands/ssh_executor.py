#!/bin/python
"""
SSHCommandExecutor executes commands via a remote SSH shell session. 
It handles command execution, output collection, inactivity/timeout logic, and is fully thread-safe.
"""
import os
import threading
import logging
import time
from queue import Queue, Empty
import uuid
import paramiko
from dotenv import load_dotenv
from app.commands.command import Command
from app.commands.executor import CommandExecutor


load_dotenv()

# Setup logging
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'DEBUG').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)
#paramiko.util.log_to_file("paramiko.log")


class SSHCommandExecutor(CommandExecutor):
    """
    Executes shell commands on a remote system via SSH.
    """

    COMMAND_TIMEOUT = int(os.getenv('COMMAND_TIMEOUT', "600"))
    COMMAND_INACTIVITY_TIMEOUT = int(os.getenv('COMMAND_INACTIVITY_TIMEOUT', "120"))
    SHELLBOX_PORT = int(os.getenv('SHELLBOX_PORT', "22"))


    def __init__(self):
        super().__init__()
        self.current_output = ""
        self._stdout_queue = Queue()
        self._stderr_queue = Queue()

        self.ssh_host = os.getenv("SHELLBOX_HOST")
        self.ssh_user = os.getenv("SHELLBOX_USER", "mentor")
        self.ssh_password = os.getenv("SHELLBOX_PASSWORD", None)
        self.ssh_keyfile = os.getenv("SHELLBOX_SSH_KEYFILE", None)

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connect()

        self.channel = self.client.invoke_shell()
        self._channel_lock = threading.Lock()
        self._start_output_reader()

        self._run_and_capture(["cd ~"])


    def _connect(self):
        try:
            if self.ssh_keyfile:
                pkey = paramiko.RSAKey.from_private_key_file(self.ssh_keyfile)
                self.client.connect(
                    hostname=self.ssh_host,
                    port=self.SHELLBOX_PORT,
                    username=self.ssh_user,
                    pkey=pkey,
                    allow_agent=False,
                    look_for_keys=False)
            else:
                self.client.connect(hostname=self.ssh_host, username=self.ssh_user,
                                    password=self.ssh_password, port=self.SHELLBOX_PORT)
        except paramiko.SSHException as e:
            logger.error("SSH connection to %s:%d failed: %s", self.ssh_host, self.SHELLBOX_PORT, e)
            raise RuntimeError(f"Failed to connect to SSH server at {self.ssh_host}:{self.SHELLBOX_PORT}") from e


    def _start_output_reader(self):
        threading.Thread(target=self._enqueue_output, daemon=True).start()


    def _enqueue_output(self):
        """
        Continuously reads output from SSH channel into queues.
        """
        buf = ""
        while True:
            if self.channel.recv_ready():
                recv = self.channel.recv(1024).decode("utf-8", errors="ignore")
                buf += recv
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    self._stdout_queue.put(line + "\n")
            time.sleep(0.1)


    def execute(self, command: Command) -> int:
        try:
            logger.info("Execute: %s", command.cmds)
            self.current_output = self._run_and_capture(command.cmds)
            command.output = self.current_output
            command.exit_code = 0
            return 0
        except Exception as exc:
            logger.exception("SSH command failed: %s", exc)
            command.output = self.current_output
            command.exit_code = 1
            return 1


    def _run_and_capture(self, cmds) -> str:
        """
        Send one or multiple commands separated by newlines and
        return **only** their combined stdout/stderr.
        """
        # 1) unique token for this round-trip
        token = str(uuid.uuid4()).replace('-', '')
        begin = f"__CMD_BEGIN_{token}__"
        end   = f"__CMD_END_{token}__"

        # 2) flush queues so we start with a clean slate
        self._drain_queues()

        # 3) build the script to send
        script_lines = [
            f"echo {begin}",
            *cmds,
            f"echo {end}"
        ]
        payload = "\n".join(script_lines) + "\n"

        # 4) transmit
        with self._channel_lock:
            self.channel.send(payload)

        # 5) collect output
        return self._collect_between_markers(begin, end)


    def _collect_between_markers(self, begin: str, end: str) -> str:
        """
        Ignore everything until *begin* appears, then record until *end* appears.
        Returns the captured text (without the markers themselves).
        """
        buffer = []
        started = False
        start_time = time.time()
        last_activity = time.time()

        while True:
            if time.time() - start_time > self.COMMAND_TIMEOUT:
                raise TimeoutError("command timed out")
            if time.time() - last_activity > self.COMMAND_INACTIVITY_TIMEOUT:
                raise TimeoutError("inactivity timeout")

            try:
                line = self._stdout_queue.get(timeout=0.1)
            except Empty:
                continue

            last_activity = time.time()
            line_strip = line.rstrip("\r\n")

            if not started:
                # wait for BEGIN marker
                if line_strip == begin:
                    started = True
                if line_strip.endswith("\r" + begin):
                    started = True
                continue

            # already inside capture window
            if line_strip == end:
                break
            if line_strip.endswith("\r" + end):
                break

            if not line_strip.endswith("echo " + end):
                buffer.append(line)

        return "".join(buffer).rstrip("\r\n")


    def _drain_queues(self) -> None:
        """Remove all items currently waiting in stdout/stderr queues."""
        while True:
            try:
                self._stdout_queue.get_nowait()
            except Empty:
                break
        while True:
            try:
                self._stderr_queue.get_nowait()
            except Empty:
                break


    def close(self):
        """ Close the SSH session and channel. """
        try:
            if self.channel:
                self.channel.close()
            if self.client:
                self.client.close()
        except Exception as e:
            logger.warning("Error closing SSH session: %s", e)


if __name__ == "__main__":
    # Example only. Requires appropriate .env settings
    executor = SSHCommandExecutor()
    try:
        commands = [
            "echo Hello via SSH",
            "uname -a",
            "ls -la",
        ]
        for cmd_str in commands:
            main_cmd = Command(Command.SHELL, [cmd_str])
            executor.execute(main_cmd)
            print(f"Command: {cmd_str}\nOutput:\n{main_cmd.output}\n{'='*40}")
    finally:
        executor.close()
