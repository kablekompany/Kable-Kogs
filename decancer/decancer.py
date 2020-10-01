import asyncio
import random
import re
import unicodedata
from datetime import datetime

import discord
import stringcase
import unidecode
from redbot.core import Config, checks, commands, modlog
from redbot.core.commands import errors

from .randomnames import adjectives, nouns, properNouns

BaseCog = getattr(commands, "Cog", object)


async def enabled_global(ctx: commands.Context):
    return await ctx.bot.get_cog("Decancer").config.auto()


# originally from https://github.com/PumPum7/PumCogs repo which has a en masse version of this
class Decancer(BaseCog):
    """Decancer users' names removing special and accented chars. `[p]decancerset` to get started if you're already using redbot core modlog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=7778847744, force_registration=True,)
        default_guild = {"modlogchannel": None, "new_custom_nick": "simp name", "auto": False}
        default_global = {"auto": True}
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

    __author__ = ["KableKompany#0001", "PhenoM4n4n"]
    __version__ = "1.7.1"

    async def red_delete_data_for_user(self, **kwargs):
        """This cog does not store user data"""
        return

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
            pass
        return str(text)

    # the magician
    async def nick_maker(self, guild: discord.Guild, old_shit_nick):
        old_shit_nick = self.strip_accs(old_shit_nick)
        new_cool_nick = re.sub("[^a-zA-Z0-9 \n.]", "", old_shit_nick)
        new_cool_nick = new_cool_nick.split()
        new_cool_nick = " ".join(new_cool_nick)
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
        embed = discord.Embed(
            color=discord.Color(color),
            title=dc_type,
            description=f"**Offender:** {str(member)} {member.mention} \n**Reason:** Remove cancerous characters from previous name\n**New Nickname:** {new_nick}\n**Responsible Moderator:** {str(moderator)} {moderator.mention}",
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
            name=f"{ctx.guild.name} Settings", value="\n".join(values),
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
            await ctx.send("I will now decancer new users.")
        else:
            await ctx.send("I will no longer decancer new users.")

    @checks.is_owner()
    @decancerset.command(name="autoglobal")
    async def global_auto(self, ctx, true_or_false: bool = None):
        """Enable/disable auto-decancering globally."""
        target_state = (
            true_or_false if true_or_false is not None else not (await self.config.auto())
        )
        await self.config.auto.set(target_state)
        if target_state:
            await ctx.send("Automatic decancering has been re-enabled globally.")
        else:
            await ctx.send("Automatic decancering has been disabled globally.")

    @commands.command(name="decancer", aliases=["dc"])
    @checks.mod_or_permissions(manage_nicknames=True)
    @checks.bot_has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nick_checker(
        self, ctx: commands.Context, user: discord.Member, freeze: bool = False
    ):
        """
        Change username glyphs (i.e 乇乂, 黑, etc)
        special font chars (zalgo, latin letters, accents, etc)
        to their unicode counterpart. If the former, expect the "english"
        equivalent to other language based glyphs.
        """
        if not await self.config.guild(ctx.guild).modlogchannel():
            return await ctx.send(
                f"Set up a modlog for this server using `{ctx.prefix}decancerset modlog #channel`"
            )
        await ctx.trigger_typing()
        if user.top_role.position >= ctx.me.top_role.position:
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
                    if not cog_checking:
                        pass
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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        data = await self.config.guild(guild).all()
        if not (
            await self.config.auto()
            and data["auto"]
            and data["modlogchannel"]
            and guild.me.guild_permissions.manage_nicknames
        ):
            return
        if member.bot:
            return

        cancerous = 0
        old_nick = member.display_name
        for segment in old_nick.split():
            for char in segment:
                if not (char.isascii() and char.isalnum()):
                    cancerous += 1

        if cancerous / len(old_nick) <= 1 / 10:
            return  # even though decancer output may be different than their current name, there isnt much reason to decancer

        await asyncio.sleep(
            5
        )  # waiting for auto mod actions to take place to prevent discord from fucking up the nickname edit
        member = guild.get_member(member.id)
        if not member:
            return
        if member.top_role.position >= guild.me.top_role.position:
            return
        new_cool_nick = await self.nick_maker(guild, old_nick)
        if old_nick.lower() != new_cool_nick.lower():
            try:
                await member.edit(
                    reason=f"Auto Decancer | Old name ({old_nick}): contained special characters",
                    nick=new_cool_nick,
                )
            except discord.errors.Forbidden:
                await self.config.guild(guild).auto.set(False)
            else:
                await self.decancer_log(
                    guild, member, guild.me, old_nick, new_cool_nick, "auto-decancer"
                )
