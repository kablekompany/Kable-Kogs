import asyncio
import random
import re
import unicodedata
from datetime import datetime, timedelta

import discord
import stringcase
import unidecode
from redbot.core import Config, checks, commands, modlog
from redbot.core.utils.chat_formatting import box, humanize_timedelta
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

from .randomnames import adjectives, nouns, properNouns


async def enabled_global(ctx: commands.Context):
    return ctx.bot.get_cog("Decancer").enabled_global


# originally from https://github.com/PumPum7/PumCogs repo which has a en masse version of this
class Decancer(commands.Cog):
    """
    Decancer users names removing special and accented chars.

    `[p]decancerset` to get started if you're already using redbot core modlog
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=7778847744,
            force_registration=True,
        )
        default_guild = {"modlogchannel": None, "new_custom_nick": "simp name", "auto": False}
        default_global = {"auto": True}
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

        self.enabled_global = None
        self.enabled_guilds = set()

    __author__ = ["KableKompany#0001", "PhenoM4n4n"]
    __version__ = "1.8.2"

    async def red_delete_data_for_user(self, **kwargs):
        """This cog does not store user data"""
        return

    async def initialize(self):
        self.enabled_global = await self.config.auto()
        for guild_id, guild_data in (await self.config.all_guilds()).items():
            if guild_data["auto"]:
                self.enabled_guilds.add(guild_id)

    @staticmethod
    def is_cancerous(text: str) -> bool:
        for segment in text.split():
            for char in segment:
                if not (char.isascii() and char.isalnum()):
                    return True
        return False

    # the magic
    @staticmethod
    def strip_accs(text):
        try:
            text = unicodedata.normalize("NFKC", text)
            text = unicodedata.normalize("NFD", text)
            text = unidecode.unidecode(text)
            text = text.encode("ascii", "ignore")
            text = text.decode("utf-8")
        except Exception as e:
            print(e)
        return str(text)

    # the magician
    async def nick_maker(self, guild: discord.Guild, old_shit_nick):
        old_shit_nick = self.strip_accs(old_shit_nick)
        new_cool_nick = re.sub("[^a-zA-Z0-9 \n.]", "", old_shit_nick)
        new_cool_nick = " ".join(new_cool_nick.split())
        new_cool_nick = stringcase.lowercase(new_cool_nick)
        new_cool_nick = stringcase.titlecase(new_cool_nick)
        default_name = await self.config.guild(guild).new_custom_nick()
        if len(new_cool_nick.replace(" ", "")) <= 1 or len(new_cool_nick) > 32:
            if default_name == "random":
                new_cool_nick = await self.get_random_nick(2)
            elif default_name:
                new_cool_nick = default_name
            else:
                new_cool_nick = "simp name"
        return new_cool_nick

    async def decancer_log(
        self,
        guild: discord.Guild,
        member: discord.Member,
        moderator: discord.Member,
        old_nick: str,
        new_nick: str,
        dc_type: str,
    ):
        channel = guild.get_channel(await self.config.guild(guild).modlogchannel())
        if not channel or not (
            channel.permissions_for(guild.me).send_messages
            and channel.permissions_for(guild.me).embed_links
        ):
            await self.config.guild(guild).modlogchannel.clear()
            return
        color = 0x2FFFFF
        description = [
            f"**Offender:** {member} {member.mention}",
            f"**Reason:** Remove cancerous characters from previous name",
            f"**New Nickname:** {new_nick}",
            f"**Responsible Moderator:** {moderator} {moderator.mention}",
        ]
        embed = discord.Embed(
            color=discord.Color(color),
            title=dc_type,
            description="\n".join(description),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    async def get_random_nick(self, nickType: int):
        if nickType == 1:
            new_nick = random.choice(properNouns)
        elif nickType == 2:
            adjective = random.choice(adjectives)
            noun = random.choice(nouns)
            new_nick = adjective + noun
        elif nickType == 3:
            adjective = random.choice(adjectives)
            new_nick = adjective.lower()
        if nickType == 4:
            nounNicks = nouns, properNouns
            new_nick = random.choice(random.choices(nounNicks, weights=map(len, nounNicks))[0])
        return new_nick

    @commands.group()
    @checks.mod_or_permissions(manage_channels=True)
    @commands.guild_only()
    async def decancerset(self, ctx):
        """
        Set up the modlog channel for decancer'd users,
        and set your default name if decancer is unsuccessful.
        """
        if ctx.invoked_subcommand:
            return
        data = await self.config.guild(ctx.guild).all()
        channel = ctx.guild.get_channel(data["modlogchannel"])
        name = data["new_custom_nick"]
        auto = data["auto"]
        if channel is None:
            try:
                check_modlog_exists = await modlog.get_modlog_channel(ctx.guild)
                await self.config.guild(ctx.guild).modlogchannel.set(check_modlog_exists.id)
                await ctx.send(
                    f"I set {check_modlog_exists.mention} as the decancer log channel. You can change this by running ``{ctx.prefix}decancerset modlog <channel> [--override]`"
                )
                channel = check_modlog_exists.mention
            except RuntimeError:
                channel = "**NOT SET**"
        else:
            channel = channel.mention
        values = [f"**Modlog Destination:** {channel}", f"**Default Name:** `{name}`"]
        if await self.config.auto():
            values.append(f"**Auto-Decancer:** `{auto}`")
        e = discord.Embed(colour=await ctx.embed_colour())
        e.add_field(
            name=f"{ctx.guild.name} Settings",
            value="\n".join(values),
        )
        e.set_footer(text="To change these, pass [p]decancerset modlog|defaultname")
        e.set_image(url=ctx.guild.icon_url)
        try:
            await ctx.send(embed=e)
        except Exception:
            pass

    @decancerset.command(aliases=["ml"])
    async def modlog(self, ctx, channel: discord.TextChannel, override: str = None):
        """
        Set a decancer entry to your modlog channel.
        If you've set one up with `[p]modlogset channel`
        it will default to using that
        """
        channel_check = await self.config.guild(ctx.guild).modlogchannel()

        if override != "-override" and channel_check:
            await ctx.send(
                f"Your current channel is <#{channel_check}>. Pass `-override` to change this."
            )
            return

        if not (
            channel.permissions_for(ctx.guild.me).send_messages
            and channel.permissions_for(ctx.guild.me).embed_links
        ):
            await ctx.send("Kind of need permissions to post in that channel LMFAO")
            return

        await self.config.guild(ctx.guild).modlogchannel.set(channel.id)
        await ctx.send(f"Channel has been set to {channel.mention}")
        await ctx.tick()

    @decancerset.command(aliases=["name"])
    async def defaultname(self, ctx, *, name):
        """
        If you don't want a server of simps, change this
        to whatever you'd like, simp.


            Example: `[p]decancerset name kable is coolaf`
        Changing the default to "random" might do something cool..
        """
        if len(name) > 32 or len(name) < 3:
            await ctx.send("Let's keep that nickname within reasonable range, scrub")
            return

        await self.config.guild(ctx.guild).new_custom_nick.set(name)
        await ctx.send(
            f"Your fallback name, should the cancer be too gd high for me to fix, is `{name}`"
        )

    @commands.check(enabled_global)
    @decancerset.command()
    async def auto(self, ctx, true_or_false: bool = None):
        """Toggle automatically decancering new users."""
        if not await self.config.guild(ctx.guild).modlogchannel():
            return await ctx.send(
                f"Set up a modlog for this server using `{ctx.prefix}decancerset modlog #channel`"
            )
        target_state = (
            true_or_false
            if true_or_false is not None
            else not (await self.config.guild(ctx.guild).auto())
        )
        await self.config.guild(ctx.guild).auto.set(target_state)
        if target_state:
            self.enabled_guilds.add(ctx.guild.id)
            await ctx.send("I will now decancer new users.")
        else:
            self.enabled_guilds.remove(ctx.guild.id)
            await ctx.send("I will no longer decancer new users.")

    @checks.is_owner()
    @decancerset.command(name="autoglobal")
    async def global_auto(self, ctx, true_or_false: bool = None):
        """Enable/disable auto-decancering globally."""
        target_state = (
            true_or_false if true_or_false is not None else not (await self.config.auto())
        )
        await self.config.auto.set(target_state)
        self.enabled_global = target_state
        if target_state:
            await ctx.send("Automatic decancering has been re-enabled globally.")
        else:
            await ctx.send("Automatic decancering has been disabled globally.")

    @commands.command(name="decancer")
    @checks.mod_or_permissions(manage_nicknames=True)
    @checks.bot_has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nick_checker(
        self, ctx: commands.Context, user: discord.Member, freeze: bool = False
    ):
        """
        Remove special/cancerous characters from user nicknames

        Change username glyphs (i.e 乇乂, 黑, etc)
        special font chars (zalgo, latin letters, accents, etc)
        to their unicode counterpart. If the former, expect the "english"
        equivalent to other language based glyphs.
        """
        if not await self.config.guild(ctx.guild).modlogchannel():
            return await ctx.send(
                f"Set up a modlog for this server using `{ctx.prefix}decancerset modlog #channel`"
            )

        if user.top_role >= ctx.me.top_role:
            return await ctx.send(
                f"I can't decancer that user since they are higher than me in heirarchy."
            )
        m_nick = user.display_name
        new_cool_nick = await self.nick_maker(ctx.guild, m_nick)
        if m_nick != new_cool_nick:
            try:
                await user.edit(
                    reason=f"Old name ({m_nick}): contained special characters",
                    nick=new_cool_nick,
                )
                if (
                    freeze
                ):  # thanks for this badass cog from Dav@https://github.com/Dav-Git/Dav-Cogs
                    cog_checking = self.bot.get_cog("NickNamer")
                    freeze_it = self.bot.get_command("freezenick")
                    await ctx.invoke(
                        freeze_it,
                        user=user,
                        nickname=new_cool_nick,
                        reason="Decancer'd and frozen",
                    )
            except Exception as e:
                await ctx.send(
                    f"Double check my order in heirarchy buddy, got an error\n```diff\n- {e}\n```"
                )
                return
            await ctx.send(f"({m_nick}) was changed to {new_cool_nick}")

            guild = ctx.guild
            await self.decancer_log(guild, user, ctx.author, m_nick, new_cool_nick, "decancer")
            try:
                await ctx.tick()
            except discord.NotFound:
                pass

        else:
            await ctx.send(f"{user.display_name} was already decancer'd")
            try:
                await ctx.message.add_reaction("\N{CROSS MARK}")
            except Exception:
                return

    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.cooldown(1, 36000, commands.BucketType.guild)
    @checks.mod_or_permissions(manage_nicknames=True)
    @checks.bot_has_permissions(manage_nicknames=True)
    @commands.guild_only()
    @commands.command(cooldown_after_parsing=True)
    async def dehoist(self, ctx: commands.Context, *, role: discord.Role = None):
        """Decancer all members of the targeted role.

        Role defaults to all members of the server."""
        if not await self.config.guild(ctx.guild).modlogchannel():
            await ctx.send(
                f"Set up a modlog for this server using `{ctx.prefix}decancerset modlog #channel`"
            )
            ctx.command.reset_cooldown(ctx)
            return

        role = role or ctx.guild.default_role
        guild = ctx.guild
        cancerous_list = [
            member
            for member in role.members
            if not member.bot
            and self.is_cancerous(member.display_name)
            and ctx.me.top_role > member.top_role
        ]
        if not cancerous_list:
            await ctx.send(f"There's no one I can decancer in **`{role}`**.")
            ctx.command.reset_cooldown(ctx)
            return
        if len(cancerous_list) > 5000:
            await ctx.send(
                "There are too many members to decancer in the targeted role. "
                "Please select a role with less than 5000 members."
            )
            ctx.command.reset_cooldown(ctx)
            return
        member_preview = "\n".join(
            f"{member} - {member.id}"
            for index, member in enumerate(cancerous_list, 1)
            if index <= 10
        ) + (
            f"\nand {len(cancerous_list) - 10} other members.." if len(cancerous_list) > 10 else ""
        )

        case = "" if len(cancerous_list) == 1 else "s"
        msg = await ctx.send(
            f"Are you sure you want me to decancer the following {len(cancerous_list)} member{case}?\n"
            + box(member_preview, "py")
        )
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)
        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        try:
            await self.bot.wait_for("reaction_add", check=pred, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Action cancelled.")
            ctx.command.reset_cooldown(ctx)
            return

        if pred.result is True:
            await ctx.send(
                f"Ok. This will take around **{humanize_timedelta(timedelta=timedelta(seconds=len(cancerous_list) * 1.5))}**."
            )
            async with ctx.typing():
                for member in cancerous_list:
                    await asyncio.sleep(1)
                    old_nick = member.display_name
                    new_cool_nick = await self.nick_maker(guild, member.display_name)
                    if old_nick.lower() != new_cool_nick.lower():
                        try:
                            await member.edit(
                                reason=f"Dehoist | Old name ({old_nick}): contained special characters",
                                nick=new_cool_nick,
                            )
                        except discord.Forbidden:
                            await ctx.send("Dehoist failed due to invalid permissions.")
                            return
                        except discord.NotFound:
                            continue
                    # else:
                    #     await self.decancer_log(
                    #         guild, member, guild.me, old_nick, new_cool_nick, "dehoist"
                    #     )
            try:
                await ctx.send("Dehoist completed.")
            except (discord.NotFound, discord.Forbidden):
                pass
        else:
            await ctx.send("Action cancelled.")
            ctx.command.reset_cooldown(ctx)
            return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if self.enabled_global is False or member.bot:
            return

        guild: discord.Guild = member.guild
        if guild.id not in self.enabled_guilds:
            return

        data = await self.config.guild(guild).all()
        if not (
            data["auto"] and data["modlogchannel"] and guild.me.guild_permissions.manage_nicknames
        ):
            return

        old_nick = member.display_name
        if not self.is_cancerous(old_nick):
            return

        await asyncio.sleep(
            5
        )  # waiting for auto mod actions to take place to prevent discord from fucking up the nickname edit
        member = guild.get_member(member.id)
        if not member:
            return
        if member.top_role >= guild.me.top_role:
            return
        new_cool_nick = await self.nick_maker(guild, old_nick)
        if old_nick.lower() != new_cool_nick.lower():
            try:
                await member.edit(
                    reason=f"Auto Decancer | Old name ({old_nick}): contained special characters",
                    nick=new_cool_nick,
                )
            except discord.NotFound:
                pass
            except discord.Forbidden:
                await self.config.guild(guild).auto.set(False)
            else:
                await self.decancer_log(
                    guild, member, guild.me, old_nick, new_cool_nick, "auto-decancer"
                )
