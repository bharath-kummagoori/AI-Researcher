"""
LocalEnv: A Docker-free alternative to DockerEnv for running commands locally.
This enables running AI-Researcher on Windows/Mac/Linux without Docker.
Commands execute directly via subprocess on the host machine.
"""
import os
import os.path as osp
import subprocess
import platform
import sys
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Union, Dict
from functools import update_wrapper
from inspect import signature


@dataclass
class LocalConfig:
    """Configuration for local execution environment."""
    workplace_name: str
    communication_port: int = 0  # Not used in local mode, kept for interface compatibility
    container_name: str = "local"
    test_pull_name: str = field(default='main')
    task_name: Optional[str] = field(default=None)
    git_clone: bool = field(default=False)
    setup_package: Optional[str] = field(default=None)
    local_root: str = field(default_factory=os.getcwd)


class LocalEnv:
    """
    Drop-in replacement for DockerEnv that executes commands locally.
    Implements the same interface so it can be used interchangeably.
    """

    def __init__(self, config: Union[LocalConfig, Dict]):
        if isinstance(config, Dict):
            config = LocalConfig(**config)
        self.workplace_name = config.workplace_name
        self.local_workplace = osp.join(config.local_root, config.workplace_name)
        self.docker_workplace = self.local_workplace  # In local mode, both point to the same path
        self.container_name = config.container_name
        self.test_pull_name = config.test_pull_name
        self.task_name = config.task_name
        self.git_clone = config.git_clone
        self.setup_package = config.setup_package
        self.communication_port = config.communication_port
        self._is_windows = platform.system() == "Windows"

    def init_container(self):
        """Initialize the local workspace (no Docker needed)."""
        os.makedirs(self.local_workplace, exist_ok=True)

        if self.setup_package is not None:
            import tarfile
            tar_path = f"packages/{self.setup_package}.tar.gz"
            if os.path.exists(tar_path):
                with tarfile.open(tar_path, 'r:gz') as tar:
                    tar.extractall(path=self.local_workplace)

        if self.git_clone:
            metachain_path = os.path.join(self.local_workplace, 'metachain')
            if not os.path.exists(metachain_path):
                github_token = os.getenv('GITHUB_AI_TOKEN', '')
                ai_user = os.getenv('AI_USER', 'ai-sin')
                git_url = f"https://{ai_user}:{github_token}@github.com/tjb-tech/metachain.git"
                result = subprocess.run(
                    ["git", "clone", "-b", self.test_pull_name, git_url],
                    cwd=self.local_workplace,
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise Exception(f"Failed to clone repository: {result.stderr}")

            if self.task_name:
                new_branch_name = f"{self.test_pull_name}_{self.task_name}"
                result = subprocess.run(
                    ["git", "checkout", "-b", new_branch_name],
                    cwd=metachain_path,
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ["git", "checkout", new_branch_name],
                        cwd=metachain_path,
                        capture_output=True, text=True
                    )

        print(f"Local workspace initialized at: {self.local_workplace}")

    def stop_container(self):
        """No-op for local mode."""
        pass

    def run_command(self, command, stream_callback=None):
        """
        Execute a command locally via subprocess.

        Args:
            command: The command to execute
            stream_callback: optional callback function for handling stream output

        Returns:
            dict: Result with 'status' and 'result' keys (same interface as DockerEnv)
        """
        try:
            if self._is_windows:
                shell_cmd = command
                shell_executable = None
                use_shell = True
            else:
                shell_cmd = command
                shell_executable = "/bin/bash"
                use_shell = True

            # Set working directory to the workplace
            cwd = self.local_workplace if os.path.isdir(self.local_workplace) else os.getcwd()

            process = subprocess.Popen(
                shell_cmd,
                shell=use_shell,
                executable=shell_executable,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )

            output_lines = []
            for line in process.stdout:
                output_lines.append(line)
                if stream_callback:
                    stream_callback(line.rstrip('\n'))

            process.wait()

            result_text = ''.join(output_lines)

            return {
                'status': process.returncode,
                'result': result_text
            }

        except Exception as e:
            return {
                'status': -1,
                'result': f'Error executing command: {str(e)}'
            }

    def wait_for_container_ready(self, timeout=30):
        """Always ready in local mode."""
        return True


def with_env(env: 'LocalEnv'):
    """Inject env into tool functions (same interface as DockerEnv's with_env)."""
    def decorator(func):
        def wrapped(*args, **kwargs):
            return func(env=env, *args, **kwargs)

        update_wrapper(wrapped, func)
        wrapped.__signature__ = signature(func).replace(
            parameters=[p for p in signature(func).parameters.values() if p.name != 'env']
        )
        if func.__doc__:
            try:
                if '{docker_workplace}' in func.__doc__:
                    wrapped.__doc__ = func.__doc__.format(docker_workplace=env.docker_workplace)
                elif '{local_workplace}' in func.__doc__:
                    wrapped.__doc__ = func.__doc__.format(local_workplace=env.local_workplace)
                else:
                    wrapped.__doc__ = func.__doc__
            except (KeyError, IndexError, ValueError):
                wrapped.__doc__ = func.__doc__
        return wrapped
    return decorator
