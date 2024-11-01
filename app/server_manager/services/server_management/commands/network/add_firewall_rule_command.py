import uuid
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class AddFirewallRuleCommand(Command):
    def __init__(self, config):
        self.config = config
        self.rule_id = None
        self.name = None
        self.port = None
        self.from_ip = None
        self.rule_type = None

    async def execute(self, data):
        # Extract rule information from the config
        self.config = data
        self.rule_id = self.config.get('rule_id')
        self.name = self.config.get('name')
        self.port = self.config.get('port')
        self.from_ip = self.config.get('from_ip', None)
        self.rule_type = self.config.get('rule_type', 'allow').lower()

        # Construct the ufw command
        ufw_command = f"sudo ufw {self.rule_type} {self.port}"

        # Add 'from' IP if provided
        if self.from_ip:
            ufw_command += f" from {self.from_ip}"

        # Execute the command
        await run_command_async(ufw_command)

        return {
            "message": f"UFW rule added successfully. {self.rule_type.capitalize()} traffic on port {self.port} "
                       f"{'from ' + self.from_ip if self.from_ip else ''}",
            "data": self.rule_id
        }
