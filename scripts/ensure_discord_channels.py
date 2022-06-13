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

        # Delete old channels: project-space, project-chat
        for channel in guild_channels:
            if channel.name in ['project-space', 'project-chat']:
                await channel.delete()

        # Find Projects category. If none, make it.
        projects_category = None
        for channel in guild_channels:
            if (isinstance(channel, discord.CategoryChannel)
                    and 'projects' in channel.name.lower()):
                projects_category = channel
                break

        if projects_category is None:
            print("Creating 'Projects' category")
            projects_category = await guild.create_category_channel('Projects')

        # A voice channel for each project
        project_channels = {channel.name: channel for channel
                            in projects_category.voice_channels}

        for project in projects:
            if project['chatchannel'] in project_channels:
                print(f"'{project['chatchannel']}' exists")
                continue

            print(f"Creating '{project['chatchannel']}'")
            await guild.create_voice_channel(
                project['chatchannel'],
                category=projects_category
            )

        await self.close()


client = EnsureChannelsClient()
client.run(os.getenv('DISCORD_TOKEN'))
