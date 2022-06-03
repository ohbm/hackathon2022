import os
import discord
import yaml


class EnsureChannelsClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

        with open('_data/projects.yml', 'r') as f:
            projects = yaml.safe_load(f)

        guild = self.get_guild(int(os.getenv('DISCORD_GUILD_ID')))
        guild_channels = guild.channels
        categories = [channel.name for channel in guild_channels
                      if isinstance(channel, discord.CategoryChannel)]

        for project in projects:
            if project['chatchannel'] in categories:
                print(f"{project['chatchannel']} exists")
                continue

            print(f"Creating {project['chatchannel']}")
            project_category = await guild.create_category_channel(
                project['chatchannel']
            )
            await guild.create_text_channel(
                'project-chat',
                category=project_category
            )
            await guild.create_voice_channel(
                'project-space',
                category=project_category
            )

        await self.close()


client = EnsureChannelsClient()
client.run(os.getenv('DISCORD_TOKEN'))
