from app.server_manager.services.server_management.commands.network.add_firewall_rule_command import \
    AddFirewallRuleCommand
from app.server_manager.services.server_management.commands.network.remove_firewall_rule_command import \
    RemoveFireWallRuleCommand
from app.server_manager.services.service import Service


class FireWallService(Service):

    def __init__(self):
        super().__init__()
        self.executor.register('add_firewall_rule_command', AddFirewallRuleCommand({'config': {}}))
        self.executor.register('remove_firewall_rule_command', RemoveFireWallRuleCommand({'config': {}}))

    async def add_firewall_rule(self, data):
        return await self.executor.execute('add_firewall_rule_command', data)

    async def remove_firewall_rule(self, data):
        return await self.executor.execute('remove_firewall_rule_command', data)
