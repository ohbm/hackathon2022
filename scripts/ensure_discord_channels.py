import os
from projects_bot import ProjectsClient

if __name__ == '__main__':

    guild = 920383461829795920
    roles_channel = 920383461829795929

    client = ProjectsClient(guild, roles_channel, just_ensure_channels=True)
    client.run(os.getenv('DISCORD_TOKEN', ''))
