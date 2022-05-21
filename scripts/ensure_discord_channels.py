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

        project_channels_category = None
        for channel in guild_channels:
            if 'Projects' in channel.name and isinstance(channel, discord.CategoryChannel):
                project_channels_category = channel
                break

        project_channels = {}
        for channel in guild_channels:
            if channel.category == project_channels_category:
                project_channels[channel.name] = channel

        for project in projects:
            if project['chatchannel'] not in project_channels:
                print(f'Creating channel {project["chatchannel"]}')
                await guild.create_text_channel(
                    project['chatchannel'],
                    category=project_channels_category
                )
                await guild.create_voice_channel(
                    project['chatchannel'],
                    category=project_channels_category
                )

        await self.close()


client = EnsureChannelsClient()
client.run(os.getenv('DISCORD_TOKEN'))
