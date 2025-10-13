from novita_sandbox.code_interpreter import Sandbox


class SandboxManager:
    def __init__(
        self,
        sandbox_template: str,
        sandbox_domain: str,
        sandbox_timeout: int,
    ):
        self.sandbox_template = sandbox_template
        self.sandbox_domain = sandbox_domain
        self.sandbox_timeout = sandbox_timeout

    def create_sandbox_session(self, sandbox_api_key: str) -> str:
        """
        This will create a new sandbox instance.

        Args:
            sandbox_api_key (str): The API key for the sandbox.

        Returns:
            str: Success message with the sandbox ID of the new sandbox or error message.
        """
        try:

            # create the new sandbox
            sandbox = Sandbox.create(
                template=self.sandbox_template,
                api_key=sandbox_api_key,
                domain=self.sandbox_domain,
                timeout=self.sandbox_timeout,
            )

            return f"Successfully created sandbox. Sandbox ID: {sandbox.sandbox_id}"

        except Exception as e:
            return f"Failed to create new sandbox:{str(e)}"

    def stop_sandbox_session(self, sandbox_api_key: str, sandbox_id: str) -> str:
        """
        This will kill a sandbox instance if it exists.

        Args:
            sandbox_api_key (str): The API key for the sandbox.
            sandbox_id (str): The ID of the sandbox.

        Returns:
            str: Success message with the sandbox ID of the killed sandbox or error message.
        """
        try:
            # connect to sandbox
            sandbox = Sandbox.connect(
                api_key=sandbox_api_key,
                sandbox_id=sandbox_id,
            )

            sandbox.kill()

            return f"Successfully killed Sandbox ID: {sandbox_id}"

        except Exception as e:
            return f"Failed to kill Sandbox ID: {sandbox_id}\n {str(e)}"

    def run_python_code(
        self, python_code: str, sandbox_api_key: str, sandbox_id: str
    ) -> dict:
        """
        Runs the python code on the sandbox, and if there any image outputs they are skipped.

        Args:
            python_code (str): The python code to run.
            sandbox_api_key (str): The API key for the sandbox.
            sandbox_id (str): The ID of the sandbox.

        Returns:
            dict: Containing stdout, logs, error, etc.
        """

        try:
            # connect to sandbox
            sandbox = Sandbox.connect(
                api_key=sandbox_api_key,
                sandbox_id=sandbox_id,
            )

            execution = sandbox.run_code(python_code, language="python")

            return {
                # we will skip image outputs.
                "outputs": [result for result in execution.results if not result.png],
                "logs": execution.logs,
                "error": execution.error,
            }

        except Exception as e:
            return {"error": str(e)}

    def run_on_command_line(
        self, command: str, sandbox_api_key: str, sandbox_id: str
    ) -> dict:
        """
        Runs the command on the sandbox.

        Args:
            command (str): The command to run.
            sandbox_api_key (str): The API key for the sandbox.
            sandbox_id (str): The ID of the sandbox.

        Returns:
            dict: Containing the output of the command and the execution error if any.
        """

        try:
            # connect to sandbox
            sandbox = Sandbox.connect(
                api_key=sandbox_api_key,
                sandbox_id=sandbox_id,
            )

            result = sandbox.commands.run(command)
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
