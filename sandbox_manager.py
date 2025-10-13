from novita_sandbox.code_interpreter import Sandbox


class SandboxManager:
    def __init__(
        self,
        sandbox_template: str,
        api_key_for_sandbox: str,
        sandbox_domain: str,
        sandbox_timeout: int,
    ):
        self.sandbox: Sandbox | None = None
        self.sandbox_template = sandbox_template
        self.api_key_for_sandbox = api_key_for_sandbox
        self.sandbox_domain = sandbox_domain
        self.sandbox_timeout = sandbox_timeout

    def _ensure_sandbox_is_running(self) -> None:
        """
        Ensures that a sandbox is running else raise an exception.
        """
        if not self.sandbox:
            raise Exception("No sandbox session has been created.")

        if not self.sandbox.is_running():
            raise Exception("Current sandbox has been killed or timeout.")

    def create_sandbox_session(self) -> str:
        """
        This will create a new singleton sandbox instance meaning any pre-existing sandbox will be killed.
        """
        try:

            if self.sandbox:
                # kill the previous sandbox if it exists
                self.stop_sandbox_session()

            # create the new sandbox
            self.sandbox = Sandbox.create(
                template=self.sandbox_template,
                api_key=self.api_key_for_sandbox,
                domain=self.sandbox_domain,
                timeout=self.sandbox_timeout,
            )
            return "Sandbox created successfully."

        except Exception as e:
            return f"Failed to create new sandbox:{str(e)}"

    def stop_sandbox_session(self) -> str:
        """
        This will kill the active singleton sandbox instance if any.
        """
        try:

            if self.sandbox:
                self.sandbox.kill()
                self.sandbox = None
                return "Sandbox killed successfully."
            else:
                return "No sandbox to kill."

        except Exception as e:
            return f"Failed to kill sandbox: {str(e)}"

    def run_python_code(self, python_code: str) -> dict:
        """
        Runs the python code on the active sandbox, and if there any image outputs they are skipped.

        Args:
            python_code (str): The python code to run.

        Returns:
            dict: Containing stdout, logs, error, etc.
        """

        try:
            self._ensure_sandbox_is_running()

            execution = self.sandbox.run_code(python_code, language="python")

            return {
                # we will skip image outputs.
                "outputs": [result for result in execution.results if not result.png],
                "logs": execution.logs,
                "error": execution.error,
            }

        except Exception as e:
            return {"error": str(e)}

    def run_on_command_line(self, command: str) -> dict:
        """
        Runs the command on the active sandbox.

        Args:
            command (str): The command to run.

        Returns:
            dict: Containing the output of the command and the execution error if any.
        """

        try:
            self._ensure_sandbox_is_running()

            result = self.sandbox.commands.run(command)
            return {
                "output": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "error": result.error,
                },
                "execution error": None,
            }

        except Exception as e:
            return {"output": None, "execution error": str(e)}
