import os
import uuid
import pwd
import aiofiles
import asyncio
from app.server_manager.interfaces.command_interface import Command


class AddSSHKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        self.user = None
        self.ssh_key = None
        self.key_id = None

    async def execute(self, data):
        self.config = data
        self.user = self.config.get('user')
        self.ssh_key = self.config.get('ssh_key')
        self.key_id = self.config.get('key_id', str(uuid.uuid4()))

        ssh_dir = f"/home/{self.user}/.ssh"
        authorized_keys_file = f"{ssh_dir}/authorized_keys"

        await self._make_dirs_async(ssh_dir, mode=0o700)
        await self._set_owner_and_permissions_async(ssh_dir, 0o700)

        key_with_id = f"# KEY_ID={self.key_id}\n{self.ssh_key}\n"

        try:
            async with aiofiles.open(authorized_keys_file, 'a') as f:
                await f.write(key_with_id)

            await self._set_owner_and_permissions_async(authorized_keys_file, 0o600)

            return {
                "message": "SSH key added successfully",
                "data": {
                    "id": self.key_id,
                }
            }
        except Exception as e:
            return {"error": f"Failed to add SSH key: {str(e)}"}

    async def _get_user_info_async(self):
        return await asyncio.to_thread(pwd.getpwnam, self.user)

    async def _make_dirs_async(self, path, mode=0o777):
        await asyncio.to_thread(os.makedirs, path, mode, exist_ok=True)

    async def _set_owner_and_permissions_async(self, path, mode):
        user_info = await self._get_user_info_async()
        await asyncio.to_thread(os.chmod, path, mode)
        await asyncio.to_thread(os.chown, path, user_info.pw_uid, user_info.pw_gid)
