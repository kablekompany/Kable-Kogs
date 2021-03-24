from collections import Counter
from typing import Union

import discord
from redbot.core import checks, commands

from . import formats, time


class FetchedUser(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument("Not a valid user ID.")
        try:
            return await ctx.bot.get_or_fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument("User not found.") from None
        except discord.HTTPException:
            raise commands.BadArgument("An error occurred while fetching the user.") from None


class AllUtils(commands.Cog):
    """Grab meta, make polls. Bitchin'"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="get", cooldown_after_parsing=True)
    async def get_that(self, ctx: commands.Context):
        """Group commands for fetching various information"""

    @get_that.command(aliases=["av"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def avatar(self, ctx, *, user: Union[discord.Member, FetchedUser] = None):
        """Shows a user's enlarged avatar (if possible).

        Works to fetch user if not in server (must provide UserID)
        """
        embed = discord.Embed()
        user = user or ctx.author
        avatar = user.avatar_url_as(static_format="png")
        embed.set_author(name=str(user), url=avatar)
        embed.set_image(url=avatar)
        embed.colour = await ctx.embed_colour()
        await ctx.send(embed=embed)

    @get_that.command(hidden=True, aliases=["ui"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def userinfo(self, ctx, *, user: Union[discord.Member, FetchedUser] = None):
        """Shows info about a user.

        Must supply UserID
        """

        user = user or ctx.author
        if ctx.guild and isinstance(user, discord.User):
            user = ctx.guild.get_member(user.id) or user

        e = discord.Embed()
        roles = [role.name.replace("@", "@\u200b") for role in getattr(user, "roles", [])]
        shared = sum(g.get_member(user.id) is not None for g in self.bot.guilds)
        e.set_author(name=str(user))

        def format_date(dt):
            if dt is None:
                return "N/A"
            return f"{dt:%Y-%m-%d %H:%M} ({time.human_timedelta(dt, accuracy=3)})"

        e.add_field(name="ID", value=user.id, inline=False)
        e.add_field(name="Servers", value=f"{shared} shared", inline=False)
        e.add_field(
            name="Joined", value=format_date(getattr(user, "joined_at", None)), inline=False
        )
        e.add_field(name="Created", value=format_date(user.created_at), inline=False)

        voice = getattr(user, "voice", None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = (
                f"{vc.name} with {other_people} others"
                if other_people
                else f"{vc.name} by themselves"
            )
            e.add_field(name="Voice", value=voice, inline=False)

        if roles:
            e.add_field(
                name="Roles",
                value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
                inline=False,
            )

        colour = user.colour
        if colour.value:
            e.colour = colour

        if user.avatar:
            e.set_thumbnail(url=user.avatar_url)

        if isinstance(user, discord.User):
            e.set_footer(text="This member is not in this server.")

        await ctx.send(embed=e)

    @get_that.command(aliases=["guildinfo", "si"], usage="")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def serverinfo(self, ctx, *, guild_id: int = None):
        """Shows info about the current server."""

        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f"Invalid Guild ID given.")
        else:
            guild = ctx.guild

        roles = [role.name.replace("@", "@\u200b") for role in guild.roles]

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (
                not perms.connect or not perms.speak
            ):
                secret[channel_type] += 1

        # member_by_status = Counter(str(m.status) for m in guild.members)

        e = discord.Embed()
        e.title = guild.name
        e.description = f"**ID**: {guild.id}\n**Owner**: {guild.owner}"
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: "<:channel:777109611395678218>",
            discord.VoiceChannel: "<:voice:777109848499290113>",
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f"{emoji} {total} ({secrets} locked)")
            else:
                channel_info.append(f"{emoji} {total}")

        features = set(guild.features)
        all_features = {
            "PARTNERED": "Partnered",
            "VERIFIED": "Verified",
            "DISCOVERABLE": "Server Discovery",
            "COMMUNITY": "Community Server",
            "FEATURABLE": "Featured",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen",
            "INVITE_SPLASH": "Invite Splash",
            "VIP_REGIONS": "VIP Voice Servers",
            "VANITY_URL": "Vanity Invite",
            "COMMERCE": "Commerce",
            "LURKABLE": "Lurkable",
            "NEWS": "News Channels",
            "ANIMATED_ICON": "Animated Icon",
            "BANNER": "Banner",
        }

        info = [
            f"<:agree:749441222954844241>: {label}"
            for feature, label in all_features.items()
            if feature in features
        ]

        if info:
            e.add_field(name="Features", value="\n".join(info))

        e.add_field(name="Channels", value="\n".join(channel_info))

        if guild.premium_tier != 0:
            boosts = f"Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts"
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f"{boosts}\nLast Boost: {last_boost} ({time.human_timedelta(last_boost.premium_since, accuracy=2)})"
            e.add_field(name="Boosts", value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        # fmt = f'<:online:316856575413321728> {member_by_status["online"]} ' \
        #       f'<:idle:316856575098880002> {member_by_status["idle"]} ' \
        #       f'<:dnd:316856574868193281> {member_by_status["dnd"]} ' \
        #       f'<:offline:316856575501402112> {member_by_status["offline"]}\n' \
        fmt = f"Total: {guild.member_count} ({formats.plural(bots):bot})"

        e.add_field(name="Members", value=fmt, inline=False)
        e.add_field(
            name="Roles", value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles"
        )

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats["animated"] += 1
                emoji_stats["animated_disabled"] += not emoji.available
            else:
                emoji_stats["regular"] += 1
                emoji_stats["disabled"] += not emoji.available

        fmt = (
            f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n'
            f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n'
        )
        if emoji_stats["disabled"] or emoji_stats["animated_disabled"]:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f"{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit*2}"
        e.add_field(name="Emoji", value=fmt, inline=False)
        e.set_footer(text="Created").timestamp = guild.created_at
        await ctx.send(embed=e)

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.avatar_url_as(static_format="png")
        e.set_author(name=str(member), url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace("_", " ").replace("guild", "server").title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name="Allowed", value="\n".join(allowed))
        e.add_field(name="Denied", value="\n".join(denied))
        await ctx.send(embed=e)

    @get_that.command(aliases=["up"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def userperms(
        self, ctx, member: discord.Member = None, channel: discord.TextChannel = None
    ):
        """Shows a member's permissions in a specific channel.

        If no channel is given then it uses the current one.
        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = channel or ctx.channel
        if member is None:
            member = ctx.author

        await self.say_permissions(ctx, member, channel)

    @get_that.command(aliases=["bp"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @checks.admin_or_permissions(manage_roles=True)
    async def botperms(self, ctx, *, channel: discord.TextChannel = None):
        """Shows the bot's permissions in a specific channel.

        If no channel is given then it uses the current one.
        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.
        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = channel or ctx.channel
        member = ctx.guild.me
        await self.say_permissions(ctx, member, channel)

    @commands.command(aliases=["dxp"])
    @commands.is_owner()
    async def debugperms(self, ctx, guild_id: int, channel_id: int, author_id: int = None):
        """Shows permission resolution for a channel and an optional author."""

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send("Guild not found?")

        channel = guild.get_channel(channel_id)
        if channel is None:
            return await ctx.send("Channel not found?")

        member = guild.me if author_id is None else guild.get_member(author_id)
        if member is None:
            return await ctx.send("Member not found?")

        await self.say_permissions(ctx, member, channel)
