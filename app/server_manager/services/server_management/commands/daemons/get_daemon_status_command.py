from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async
import logging

logger = logging.getLogger(__name__)

class GetDaemonStatusCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')

        if not self.daemon_id or not isinstance(self.daemon_id, str):
            logger.error("Invalid daemon_id provided.")
            return {
                "message": "Invalid daemon_id provided.",
                "data": None,
                "status": "error"
            }

        command = f'sudo supervisorctl status {self.daemon_id}:*'

        result, error_output = await run_command_async(
            command,
            capture_output=True,
            raise_exception=False
        )

        if error_output:

            if "no such process" in error_output.lower():
                logger.error(f"No such process found for daemon '{self.daemon_id}'. Error: {error_output}")
                return {
                    "message": f"No such process found for daemon '{self.daemon_id}'.",
                    "data": None,
                    "status": "error"
                }
            else:
                logger.error(f"Error retrieving status for daemon '{self.daemon_id}': {error_output}")
                return {
                    "message": "Error retrieving daemon status.",
                    "data": error_output,
                    "status": "error"
                }
        else:

            lines = result.strip().split('\n')
            process_statuses = []
            overall_status = "success"

            for line in lines:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) < 2:
                    logger.warning(f"Unexpected line format: {line}")
                    continue

                process_name = parts[0]
                status = parts[1]

                process_statuses.append({
                    "process_name": process_name,
                    "status": status
                })


                if status not in ["RUNNING", "STARTING"]:
                    overall_status = "error"

            logger.info(f"Successfully retrieved status for daemon '{self.daemon_id}'.")
            return {
                "message": "Successfully retrieved daemon status.",
                "data": process_statuses,
                "status": overall_status
            }
