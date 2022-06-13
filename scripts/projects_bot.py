import os
import discord
import yaml

EMOJI_NUMS = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣',
              '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']


class Project:
    def __init__(self, data):
        self.key = data['chatchannel']
        self.title = data['title']
        self.link = data['link']
        self.role = None
        self.channel = None
        self.react = None

    def __str__(self):
        s = (f"@{self.key}\n"
             f"title: {self.title}\n"
             f"link: {self.link}")
        if self.role is not None:
            s += f"\nrole: {self.role.id}"
        if self.channel is not None:
            s += f"\nchannel: {self.channel.id}"
        if self.reaction is not None:
            s += f"\nreact: {self.react[1]} on {self.react[0]}"
        return s


class ProjectsClient(discord.Client):
    def parse_projects(self, text):
        return [line.rsplit('@', 1)[-1] for line in text.split('\n')]

    def format_projects(self, keys):
        lines = []
        for i, key in enumerate(keys):
            p = self.projects[key]
            lines.append(f"{EMOJI_NUMS[i]} [{p.title}]({p.link}) @{key}")
        return '\n'.join(lines)

    async def on_ready(self):
        print('Logged on as', self.user)

        # read in projects
        with open('_data/projects.yml', 'r') as f:
            projects_yml = yaml.safe_load(f)

        self.projects = {}
        for p in projects_yml:
            project = Project(p)
            self.projects[project.key] = project

        # get server
        guild = self.get_guild(int(os.getenv('DISCORD_GUILD_ID')))
        staff_role = guild.get_role(920383461829795926)
        carl_role = guild.get_role(971318302100033570)
        self.roles_channel = guild.get_channel(920383461829795929)

        # ROLES
        for role in guild.roles:
            if role.name == 'muted':
                muted_role = role
            elif role.name in self.projects:
                self.projects[role.name].role = role
                print(f"'{role.name}' role exists")

        role_made = False
        for key, project in self.projects.items():
            if project.role is None:
                project.role = await guild.create_role(
                    name=key, mentionable=True)
                await project.role.edit(position=2)
                role_made = True
                print(f"'{key}' role made")

        if role_made:
            await muted_role.edit(position=1)

        # CATEGORY
        projects_category = None
        for category in guild.categories:
            if category.name == 'Projects':
                projects_category = category
                print("'Projects' category exists")
                break

        if projects_category is None:
            projects_category = await guild.create_category_channel('Projects')
            print("'Projects' category made")

        # CHANNELS
        for channel in projects_category.voice_channels:
            if channel.name in self.projects:
                self.projects[channel.name].channel = channel
                print(f"'{channel.name}' channel exists")

        for key, project in self.projects.items():
            if project.channel is None:
                project.channel = await guild.create_voice_channel(
                    name=key, category=projects_category)
                print(f"'{key}' channel made")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False),
                muted_role: discord.PermissionOverwrite(
                    view_channel=False),
                project.role: discord.PermissionOverwrite(
                    view_channel=True),
                carl_role: discord.PermissionOverwrite(
                    view_channel=True),
                staff_role: discord.PermissionOverwrite(
                    view_channel=True)
            }
            await project.channel.edit(overwrites=overwrites)

        # REACTION ROLES
        self.react_keys = {}
        async for msg in self.roles_channel.history(limit=10):
            if len(msg.embeds) < 1 or msg.embeds[0].title != 'Projects':
                continue
            text = msg.embeds[0].description
            self.react_keys[msg] = self.parse_projects(text)

            for i, key in enumerate(self.react_keys[msg]):
                if key in self.projects:
                    self.projects[key].react = (msg.id, i)
                    print(f"'{key}' react exists")

        for key, project in self.projects.items():
            if project.react is None:
                react_made = False

                # add to existing msg if not full
                for msg, keys in self.react_keys.items():
                    if len(keys) >= len(EMOJI_NUMS):
                        continue
                    keys.append(key)
                    await msg.edit(embed=discord.Embed(
                        title='Projects',
                        description=self.format_projects(keys)))
                    await msg.add_reaction(EMOJI_NUMS[len(keys) - 1])
                    react_made = True

                # start new embed msg if full
                if not react_made:
                    msg = await self.roles_channel.send(embed=discord.Embed(
                        title='Projects',
                        description=self.format_projects([key])))
                    self.react_keys[msg] = [key]
                    await msg.add_reaction(EMOJI_NUMS[0])
                    react_made = True

                if react_made:
                    print(f"'{key}' react made")
                else:
                    print(f"ERROR: failed to make '{key}' react")


client = ProjectsClient()
client.run(os.getenv('DISCORD_TOKEN'))
