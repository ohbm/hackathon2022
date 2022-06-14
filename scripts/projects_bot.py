import asyncio
import os
from typing import Dict

import discord
import discord.ext.tasks
import yaml

from fetch_gh_issues import fetch_gh_issues

EMOJI_PROJECT_ROLES = list(
    "🐁🐂🐄🐇🐈🐉🐊🐋🐌"
    "🐍🐎🐏🐐🐑🐒🐓🐕🦛"
    "🦚🐘🐙🐚🐛🦢🐝🐞🦕"
    "🦖🐡🐢🐦🐧🦜🐩🐪🐬"
    "🐿🕊🦜🦂🦃🦆🦇🦈🦒"
    "🦉🦋🦎🦔"
)

ROLES_PROJECT_MESSAGE = "{emoji} [{title}]({link}): [@{key}](https://discordapp.com/channels/{guild}/{channel})"

ROLES_MESSAGE = """
> Please react to this message with the appropriate emoji for the project.
> 
> The emoji reaction will allow you to receive notifications from the project via the tag `@proj-<project name>`.
"""

ROLES_MESSAGE_ACK = """
The emojis were assigned to the projects *at random*, if you'd like to change your project's emoji, please contact the <@&{staff_role}>.
"""


class Project:
    def __init__(self, client, data, emoji):
        self.client = client
        self.guild = client.guild

        self.key = data['chatchannel']
        self.title = data['title']
        self.link = data['issue_link']
        self.emoji = emoji

        self.channel = client.projects_channels.get(self.key)
        self.role = client.projects_roles.get(f'proj-{self.key}')
        self.react = None

    def __str__(self):
        s = (f"@{self.key}\n"
             f"title: {self.title}\n"
             f"link: {self.link}")
        if self.role is not None:
            s += f"\nrole: {self.role.id}"
        if self.channel is not None:
            s += f"\nchannel: {self.channel.id}"
        if self.react is not None:
            s += f"\nreact: {self.react[1]} on {self.react[0]}"
        return s

    def __await__(self):
        # not my favorite part of the code
        yield from asyncio.create_task(self.ensure_role())
        yield from asyncio.create_task(self.ensure_channel())
        yield from asyncio.create_task(self.ensure_channel_permissions())
        return self
    
    async def ensure_role(self):
        if self.role is not None:
            return False

        self.role =  await self.guild.create_role(
            name=f'proj-{self.key}',
            mentionable=True,
        )
        await self.role.edit(position=2)
        return True
    
    async def ensure_channel(self):
        if self.channel is not None:
            return False
        
        await self.ensure_role()

        self.channel = await self.guild.create_voice_channel(
            name=self.key,
            category=self.client.projects_category
        )

    async def ensure_channel_permissions(self):
        await self.ensure_channel()

        permission_hidden = discord.PermissionOverwrite(
            view_channel=False
        )
        permission_shown = discord.PermissionOverwrite(
            view_channel=True
        )
        overwrites = {
            self.guild.default_role: permission_shown, # TODO need to change this for the roles to work
            self.client.roles['muted']: permission_hidden,
            self.client.roles['carl']: permission_shown,
            self.client.roles['hackathon-bot']: permission_shown,
            self.client.roles['staff']: permission_shown,
            self.role: permission_shown,
        }
        await self.channel.edit(overwrites=overwrites)
        return True


class ProjectsClient(discord.Client):

    def __init__(self,
                 guild: int, roles_channel: int,
                 just_ensure_channels: bool = False,
                 *args, **kwargs):

        intents = discord.Intents.default()
        super().__init__(intents=intents, *args, **kwargs)

        self._just_ensure_channels = just_ensure_channels
        self._guild_id = guild
        self._roles_channel_id = roles_channel
        self._ready_to_bot = False

    async def cache_structures(self):
        guild = self.get_guild(self._guild_id)
        assert guild is not None
        self._guild: discord.Guild = guild

        roles_channel = self.get_channel(self._roles_channel_id)
        assert roles_channel is not None
        assert isinstance(roles_channel, discord.TextChannel)
        self._roles_channel: discord.TextChannel = roles_channel

        # TODO fixed ids :(
        self._roles = {
            'staff': self._guild.get_role(920383461829795926),
            'carl': self._guild.get_role(971318302100033570),
            'hackathon-bot': self._guild.get_role(965650036308447276),
            'muted': self._guild.get_role(962429030714458162),
        }

        projects_category = None
        for category in self._guild.categories:
            if category.name == 'Projects':
                projects_category = category
                break

        if projects_category is None:
            projects_category = await guild.create_category_channel('Projects')

        self._projects_category = projects_category
        self._projects_channels = {
            c.name: c
            for c in projects_category.voice_channels
        }
        self._projects_roles = {
            role.name: role
            for role in self.guild.roles
            if role.name.replace('proj-', '') in self._projects_channels
        }


    @property
    def guild(self) -> discord.Guild:
        assert self._guild is not None
        return self._guild

    @property
    def roles_channel(self) -> discord.TextChannel:
        return self._roles_channel

    @property
    def projects_category(self) -> discord.CategoryChannel:
        return self._projects_category

    @property
    def projects_channels(self) -> Dict[str, discord.VoiceChannel]:
        return self._projects_channels

    @property
    def projects_roles(self) -> Dict[str, discord.Role]:
        return self._projects_roles

    @property
    def roles(self) -> Dict[str, discord.Role]:
        return self._roles

    @discord.ext.tasks.loop(minutes=1)
    async def on_check_again(self):
        if not self._ready_to_bot:
            # Skip first iteration, we just did all this
            self._ready_to_bot = True
            return

        print('Refreshing issues and all')
        current_project_ids = set(self.projects.keys())
        await self.cache_structures()
        await self.ensure_projects()

        # There are new projects. refresh internal memory
        # TODO just run things for new projects?
        if current_project_ids.difference(self.projects.keys()):
            print(f'Loaded {len(self.projects)} projects')
            print('Checking roles messages')
            await self.ensure_roles_messages()

    async def ensure_projects(self):
        if not self._just_ensure_channels:
            fetch_gh_issues()

        self.projects = {}
        self.projects_emoji = {}
        with open('_data/projects.yml', 'r') as f:
            projects = yaml.safe_load(f)

            for i, data in enumerate(projects):
                project = await Project(self, data, EMOJI_PROJECT_ROLES[i])
                self.projects[project.key] = project
                self.projects_emoji[project.emoji] = project

    async def on_ready(self):
        print('Logged on as', self.user)

        await self.cache_structures()
        await self.ensure_projects()

        print(f'Loaded {len(self.projects)} projects')

        await self.roles['muted'].edit(position=1)

        # Checking if all projects are in the guild
        # Let the roles thing to the constantly-running bot
        if self._just_ensure_channels:
            await self.close()
            return

        await self.ensure_roles_messages()
        
        self.on_check_again.start()

    async def ensure_roles_messages(self):
        self._role_messages = []
        cur_messages = self.roles_channel.history(limit=10, oldest_first=True)
        async for message in cur_messages:
            if len(message.embeds) < 1:
                continue
            if message.embeds[-1].title != 'Projects':
                continue

            self._role_messages += [message]
        self._role_messages_ids = [m.id for m in self._role_messages]
        del cur_messages

        ack_message = ROLES_MESSAGE_ACK.format(
            staff_role=str(self.roles['staff'].id))

        ack_embed = discord.Embed(
            description=ack_message,
            color=0xff0000,
        )

        PROJECTS_PER_MESSAGE = 10  # max number of reactions\
        EMBED_DESCRIPTION_LIMIT = 4096  # max number of characters in embeds
        EMBEDS_CHAR_SUM = 6000

        description = ""
        project_emojis = []
        projects_in_message = 0
        messages_sent = 0
        for pi, (key, project) in enumerate(self.projects.items()):

            description += ROLES_PROJECT_MESSAGE.format(
                emoji=project.emoji, title=project.title, link=project.link,
                key=key, guild=self.guild.id, channel=project.channel.id)
            description += "\n"

            project_emojis.append(project.emoji)
            projects_in_message += 1

            description_limit = EMBED_DESCRIPTION_LIMIT
            if messages_sent == 0:
                sum_limit = EMBEDS_CHAR_SUM - len(str(ack_embed.description))
                description_limit = min(description_limit, sum_limit)

            if (len(description) >= description_limit
                    or projects_in_message >= PROJECTS_PER_MESSAGE
                    or pi == len(self.projects) - 1):

                embeds = []
                content = None
                if messages_sent == 0:
                    embeds += [ack_embed]
                    content = ROLES_MESSAGE

                embed = discord.Embed(
                    title='Projects',
                    description=description,
                    color=0x00ff00,
                )
                embeds += [embed]

                if messages_sent >= len(self._role_messages):
                    message = await self.roles_channel.send(
                        content=content,
                        embeds=embeds
                    )
                    self._role_messages_ids += [message.id]
                else:
                    message = self._role_messages[messages_sent]
                    await message.edit(
                        content=content,
                        embeds=embeds
                    )

                bot_reactions = {r.emoji: r for r in message.reactions if r.me}
                for pe in project_emojis:
                    if pe not in bot_reactions:
                        await message.add_reaction(pe)
                    if pe in bot_reactions:
                        del bot_reactions[pe]

                for e in bot_reactions.keys():
                    await message.remove_reaction(e, member=self.user)


                # Reset for next message
                description = ""
                project_emojis = []
                projects_in_message = 0

                messages_sent += 1

    async def reaction_role(self, payload, add):
        if (payload.message_id not in self._role_messages_ids
                or str(payload.emoji) not in self.projects_emoji
                or payload.user_id == self.user.id):
            return

        project = self.projects_emoji[str(payload.emoji)]
        user = await self.roles_channel.guild.fetch_member(payload.user_id)
        if add:
            await user.add_roles(project.role)
        else:
            await user.remove_roles(project.role)

    async def on_raw_reaction_add(self, payload):
        await self.reaction_role(payload, True)

    async def on_raw_reaction_remove(self, payload):
        await self.reaction_role(payload, False)


if __name__ == '__main__':

    guild = 920383461829795920
    # roles_channel = 920383461829795929
    roles_channel = 986052228303429654 # Pivate channel for testing

    client = ProjectsClient(guild, roles_channel)
    client.run(os.getenv('DISCORD_TOKEN', ''))
