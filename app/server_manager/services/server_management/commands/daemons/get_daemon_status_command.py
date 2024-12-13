import json
import logging
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async

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
                "data": json.dumps(None),
                "status": "error"
            }

        command_multi = f'sudo supervisorctl status {self.daemon_id}:*'

        result_multi, error_output_multi = await run_command_async(
            command_multi,
            capture_output=True,
            raise_exception=False
        )

        if error_output_multi:

            if "no such process" in error_output_multi.lower():
                logger.info(
                    f"No multiple processes found for daemon '{self.daemon_id}'. Attempting single process status.")

                command_single = f'sudo supervisorctl status {self.daemon_id}'
                result_single, error_output_single = await run_command_async(
                    command_single,
                    capture_output=True,
                    raise_exception=False
                )

                if error_output_single:
                    if "no such process" in error_output_single.lower():
                        logger.error(
                            f"No such process found for daemon '{self.daemon_id}'. Error: {error_output_single}")
                        return {
                            "message": f"No such process found for daemon '{self.daemon_id}'.",
                            "data": json.dumps(None),
                            "status": "error"
                        }
                    else:
                        logger.error(f"Error retrieving status for daemon '{self.daemon_id}': {error_output_single}")
                        return {
                            "message": "Error retrieving daemon status.",
                            "data": json.dumps(error_output_single),
                            "status": "error"
                        }
                else:

                    process_info = self.parse_supervisor_status(result_single)
                    overall_status = self.determine_overall_status([process_info])
                    return {
                        "message": "Successfully retrieved daemon status.",
                        "data": json.dumps([process_info]),
                        "status": overall_status
                    }
            else:

                logger.error(f"Error retrieving statuses for daemon '{self.daemon_id}': {error_output_multi}")
                return {
                    "message": "Error retrieving daemon status.",
                    "data": json.dumps(error_output_multi),
                    "status": "error"
                }
        else:

            process_statuses = self.parse_supervisor_status_multiple(result_multi)
            overall_status = self.determine_overall_status(process_statuses)
            return {
                "message": "Successfully retrieved daemon status.",
                "data": json.dumps(process_statuses),
                "status": overall_status
            }

    def parse_supervisor_status_multiple(self, result: str):
        lines = result.strip().split('\n')
        process_statuses = []

        for line in lines:
            if not line.strip():
                continue
            parts = line.split(None, 2)
            if len(parts) < 2:
                logger.warning(f"Unexpected line format: {line}")
                continue

            process_name = parts[0]
            status = parts[1]
            description = parts[2] if len(parts) > 2 else ''

            process_statuses.append({
                "process_name": process_name,
                "status": status,
                "description": description
            })

        return process_statuses

    def parse_supervisor_status(self, result: str):
        line = result.strip()
        if not line:
            logger.warning("Empty supervisorctl status output for single process.")
            return {"process_name": self.daemon_id, "status": "UNKNOWN", "description": ""}

        parts = line.split(None, 2)
        if len(parts) < 2:
            logger.warning(f"Unexpected line format for single process: {line}")
            return {"process_name": self.daemon_id, "status": "UNKNOWN", "description": ""}

        process_name = parts[0]
        status = parts[1]
        description = parts[2] if len(parts) > 2 else ''

        return {
            "process_name": process_name,
            "status": status,
            "description": description
        }

    def determine_overall_status(self, process_statuses):
        for proc in process_statuses:
            if proc['status'] not in ["RUNNING", "STARTING"]:
                return "error"
        return "success"
