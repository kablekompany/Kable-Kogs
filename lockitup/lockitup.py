import asyncio
import logging
from datetime import datetime
from os.path import exists
from typing import Optional, Union

import discord
from redbot.core import Config, checks, commands
from redbot.core.commands import Greedy
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

BaseCog = getattr(commands, "Cog", object)

# core functioning from Sharky-Cogs @https://github.com/SharkyTheKing/Sharky
class LockItUp(BaseCog):
    """`[p]lds` to get started on configuration"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=3734879387937497)

        default_guild = {
            "channels": [],
            "roles": [],
            "lockdown_message": None,
            "unlockdown_message": None,
            "locked": False,
            "vc_channels": [],
            "send_alert": True,
            "nondefault": False,
            "secondary_role": None,
            "secondary_channels": [],
        }

        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.kko-cogs.lockitup")

    async def red_delete_data_for_user(self, **kwargs):
        """This cog does not store user data"""
        return

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_channels=True)
    @checks.bot_has_permissions(manage_channels=True)
    async def lockdown(self, ctx: commands.Context):
        """
        Lockdown a server
        """
        guild = ctx.guild

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        lock_check = await self.config.guild(ctx.guild).locked()
        if lock_check is True:
            return await ctx.send("You're already locked")

        author = ctx.author
        msg = await self.config.guild(guild).lockdown_message()
        color1 = 0xF50A0A
        e = discord.Embed(
            color=discord.Color(color1),
            title=f"Server Lockdown :lock:",
            description=msg,
            timestamp=ctx.message.created_at,
        )
        e.set_footer(text=f"{guild.name}")
        bot_override = ctx.bot.user

        await ctx.trigger_typing()

        nondefault_lock = await self.config.guild(guild).nondefault()
        if nondefault_lock is True:
            await ctx.send("You ready to lock up? `[yes|no]`")
            try:
                confirm_special = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_special.content.lower() != "yes":
                    return await ctx.send("Canceling....")
            except asyncio.TimeoutError:
                return await ctx.send("You didn't answer in time!")

            special_chans = await self.config.guild(guild).secondary_channels()
            spec_role = await self.config.guild(guild).secondary_role()
            for guild_channel in guild.channels:
                if guild_channel.id in special_chans:
                    overwrite1 = guild_channel.overwrites_for(bot_override)
                    overwrite1.update(send_messages=True, embed_links=True)
                    try:
                        if not overwrite1.send_messages:
                            await guild_channel.set_permissions(
                                bot_override,
                                overwrite=overwrite1,
                                reason="Securing bot overrides for lockdown",
                            )
                    except Exception:
                        return await ctx.send(
                            "You'll need to raise my role, or make sure I can manage those channels. I failed trying to secure my own overrides. This lockdown will not resume"
                        )
                    role = discord.utils.get(guild.roles, id=spec_role)
                    spec_overwrite = guild_channel.overwrites_for(role)
                    spec_overwrite.update(send_messages=False)
                    try:
                        await guild_channel.set_permissions(
                            role,
                            overwrite=spec_overwrite,
                            reason="Lockdown in effect. Requested by {} ({})".format(
                                author.name, author.id
                            ),
                        )
                    except discord.Forbidden:
                        self.log.info("Could not lockdown {}".format(guild_channel.name))
                    if msg is not None:
                        notifier = await self.config.guild(guild).send_alert()
                        if notifier is True:
                            try:
                                await guild_channel.send(embed=e)
                            except discord.Forbidden:
                                self.log.info(
                                    "Could not send message to {}".format(guild_channel.name)
                                )

        # proceed to default lockdown
        channel_ids = await self.config.guild(guild).channels()
        if not channel_ids:
            await ctx.send("You need to set this up by running `;;lockdownset addchan` first!")
            return
        spec_ran = await self.config.guild(guild).nondefault()
        if spec_ran is False:
            await ctx.send("You sure you wanna lock up? `[yes|no]`")

            try:
                confirm_lockdown = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_lockdown.content.lower() != "yes":
                    return await ctx.send("Okay. Stop wasting my time")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply!")

        role = guild.default_role
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite1 = guild_channel.overwrites_for(bot_override)
                overwrite1.update(send_messages=True, embed_links=True)
                try:
                    if not overwrite1.send_messages:
                        await guild_channel.set_permissions(
                            bot_override,
                            overwrite=overwrite1,
                            reason="Securing bot overrides for lockdown",
                        )
                except Exception:
                    return await ctx.send(
                        "You'll need to raise my role, or make sure I can manage those channels. I failed trying to secure my own overrides. This lockdown will not resume"
                    )

                overwrite = guild_channel.overwrites_for(role)
                overwrite.update(send_messages=False)
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Could not lockdown {}".format(guild_channel.name))
                if msg is not None:
                    notifier = await self.config.guild(guild).send_alert()
                    if notifier is True:
                        try:
                            await guild_channel.send(embed=e)
                        except discord.Forbidden:
                            self.log.info(
                                "Could not send message to {}".format(guild_channel.name)
                            )
        try:
            await ctx.send(
                "We're locked up, fam. Revert this by running `{}unlockdown`".format(ctx.prefix)
            )
        except discord.Forbidden:
            self.log.info(
                f"Couldn't secure overrides in Guild {ctx.guild.name} ({ctx.guild.id}): Locked as requested."
            )

        await self.config.guild(guild).locked.set(True)

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    @checks.bot_has_permissions(manage_channels=True)
    async def unlockdown(self, ctx: commands.Context):
        """
        Ends the lockdown for the guild
        """
        guild = ctx.guild

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        lock_check = await self.config.guild(ctx.guild).locked()
        if lock_check is False:
            return await ctx.send("You're not locked")

        author = ctx.author
        msg = await self.config.guild(guild).unlockdown_message()
        color2 = 0x2FFFFF
        e = discord.Embed(
            color=discord.Color(color2),
            title=f"Server Unlock :unlock:",
            description=msg,
            timestamp=ctx.message.created_at,
        )
        e.set_footer(text=f"{guild.name}")

        await ctx.trigger_typing()

        nondefault_lock = await self.config.guild(guild).nondefault()
        if nondefault_lock is True:
            await ctx.send("Ready to unlock? `[yes|no]`")
            special_chans = await self.config.guild(guild).secondary_channels()
            spec_role = await self.config.guild(guild).secondary_role()
            try:
                confirm_special = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_special.content.lower() != "yes":
                    return await ctx.send("Looks like we aren't locking this thing up today")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply!")

            for guild_channel in guild.channels:
                if guild_channel.id in special_chans:
                    role = discord.utils.get(guild.roles, id=spec_role)
                    spec_overwrite = guild_channel.overwrites_for(role)
                    spec_overwrite.update(send_messages=True)
                    try:
                        await guild_channel.set_permissions(
                            role,
                            overwrite=spec_overwrite,
                            reason="Lockdown rescinded. Requested by {} ({})".format(
                                author.name, author.id
                            ),
                        )
                    except discord.Forbidden:
                        self.log.info("Could not unlock {}".format(guild_channel.name))
                    if msg is not None:
                        notifier = await self.config.guild(guild).send_alert()
                        if notifier is True:
                            try:
                                await guild_channel.send(embed=e)
                            except discord.Forbidden:
                                self.log.info(
                                    "Could not send message to {}".format(guild_channel.name)
                                )

        # proceed to default lockdown
        channel_ids = await self.config.guild(guild).channels()
        if not channel_ids:
            await ctx.send("You need to set this up by running `{}lockdownset addchan` first!".format(ctx.prefix))
            return
        spec_ran = await self.config.guild(guild).nondefault()
        if spec_ran is False:
            await ctx.send("R U sure about that `[yes|no]`")

            try:
                confirm_unlockdown = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_unlockdown.content.lower() != "yes":
                    return await ctx.send("Okay. Stop wasting my time")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply!")

        role = guild.default_role
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite.update(send_messages=None)
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown rescinded. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Could not unlock {}".format(guild_channel.name))
                if msg is not None:
                    notifier = await self.config.guild(guild).send_alert()
                    if notifier is True:
                        try:
                            await guild_channel.send(embed=e)
                        except discord.Forbidden:
                            self.log.info(
                                "Could not send message to {}".format(guild_channel.name)
                            )
        try:
            await ctx.send("Server Unlocked")
        except discord.Forbidden:
            self.log.info(
                f"Something is wrong with my permissions in {ctx.guild.name} ({ctx.guild.id}) when unlock was requested."
            )

        await self.config.guild(guild).locked.set(False)

    @commands.group(aliases=["lds"])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    @checks.bot_has_permissions(embed_links=True)
    async def lockdownset(self, ctx: commands.Context):
        """
        Settings for lockdown
        For each setting, pass one ID each invocation. So if you need to add multiple channels, run the commands to do so multiple times (same for removal, duh)
        """
        pass

    @lockdownset.command(name="showsettings")
    async def show_settings(self, ctx: commands.Context):
        """See Guild Configuration"""
        guild = ctx.guild
        fetch_all = await self.config.guild(guild).get_raw()
        get_channel = fetch_all["channels"]
        get_lock = fetch_all["lockdown_message"]
        get_unlock = fetch_all["unlockdown_message"]
        get_sec_role = fetch_all["secondary_role"]
        get_sec_chans = fetch_all["secondary_channels"]
        check_silent = fetch_all["send_alert"]

        chan = []
        chan_count = len(get_channel)
        if not get_channel:
            e = discord.Embed(
                color=await ctx.embed_color(),
                title="Lockdown Settings:",
                description="No channels added",
            )
            e.add_field(name="Lock Message:", value=get_lock if get_lock else "**None**")
            e.add_field(name="Unlock Message:", value=get_unlock if get_unlock else "**None**")
            check_specs = fetch_all["nondefault"]
            if check_specs is False:
                e.add_field(
                    name="Special Role",
                    value=f"<@&{get_sec_role}> — `{get_sec_role}`" if get_sec_role else "**None**",
                )
            if get_sec_chans:
                if not get_sec_role:
                    e.add_field(
                        name="Special Channels",
                        value="There are channels set, but a role needs to be set for them to work",
                    )

            e.add_field(
                name="Channel Notification:",
                value="**Enabled**" if check_silent else "**Disabled**",
            )
            return await ctx.send(embed=e)
        else:
            msg = ""
            for chan_id in get_channel:
                channel_name = f"<#{chan_id}>"
                msg += f"{channel_name} — `{chan_id}`\n"

        channel_list = sorted(msg)
        e_list = []
        for page in pagify(msg, shorten_by=1000):
            e = discord.Embed(
                color=await ctx.embed_color(),
                title="Lockdown Settings:",
                description="Channels: {}\n{}".format(chan_count, page),
            )
            e.add_field(
                name="Lock Message:", value=get_lock if get_lock else "**None**", inline=False
            )
            e.add_field(
                name="Unlock Message:",
                value=get_unlock if get_unlock else "**None**",
                inline=False,
            )
            check_specs = fetch_all["nondefault"]
            if check_specs is True:
                e.add_field(
                    name="Special Role",
                    value=f"<@&{get_sec_role}> — `{get_sec_role}`" if get_sec_role else "**None**",
                )
                spec_msg = ""
                for chan_id in get_sec_chans:
                    channel_name = f"<#{chan_id}>"
                    spec_msg += f"{channel_name} — `{chan_id}`\n"
                e.add_field(name="Special Channels", value=spec_msg)

            e.add_field(
                name="Channel Notification:",
                value="**Enabled**" if check_silent else "**Disabled**",
                inline=False,
            )
            e.set_author(name=ctx.guild.name, icon_url=guild.icon_url)
            e.set_footer(text="Lockdown Configuration")
            e_list.append(e)

        await menu(ctx, e_list, DEFAULT_CONTROLS)

    @lockdownset.command()
    async def addchan(self, ctx: commands.Context, channels: Greedy[discord.TextChannel]):
        """
        Adds channel to list of channels to lock/unlock
        You can add as many as needed
        IDs are also accepted.
        """
        if not channels:
            raise commands.BadArgument
        guild = ctx.guild
        chans = await self.config.guild(guild).channels()
        for chan in channels:
            if chan not in chans:
                chans.append(chan.id)
                await self.config.guild(guild).channels.set(chans)
            else:
                continue
        chan_count = len(chans)
        msg = ""
        for chan_id in chans:
            channel_name = f"<#{chan_id}>"
            msg += f"{chan_id} - {channel_name}\n"
        channel_list = sorted(msg)
        e_list = []
        for page in pagify(msg, shorten_by=1000):

            embed = discord.Embed(
                description="Channel List: {}\n{}".format(chan_count, page),
                colour=await ctx.embed_color(),
            )
            embed.set_author(name=guild.name, icon_url=guild.icon_url)
            embed.set_footer(text="Lockdown Channel Settings")
            e_list.append(embed)
        await ctx.send("Added to the list, here's your current channels")
        await menu(ctx, e_list, DEFAULT_CONTROLS)

    @lockdownset.command(name="addspecialchannel", aliases=["asc"])
    async def add_special_channel(
        self, ctx: commands.Context, channels: Greedy[discord.TextChannel]
    ):
        """
        Adds channel to list of channels to lock/unlock for special role
        """
        if not channels:
            raise commands.BadArgument
        guild = ctx.guild
        chans = await self.config.guild(guild).secondary_channels()
        for chan in channels:
            if chan not in chans:
                chans.append(chan.id)
                await self.config.guild(guild).secondary_channels.set(chans)
            else:
                continue
        chan_count = len(chans)
        msg = ""
        for chan_id in chans:
            channel_name = f"<#{chan_id}>"
            msg += f"{chan_id} - {channel_name}\n"
        channel_list = sorted(msg)
        e_list = []
        for page in pagify(msg, shorten_by=1000):

            embed = discord.Embed(
                description="Channel List: {}\n{}".format(chan_count, page),
                colour=await ctx.embed_color(),
            )
            embed.set_author(name=guild.name, icon_url=guild.icon_url)
            embed.set_footer(text="Secondary Channels")
            e_list.append(embed)

        nondefault = await self.config.guild(guild).nondefault()
        check_role = await self.config.guild(guild).secondary_role()
        if nondefault is False:
            if check_role is not None:
                await self.config.guild(guild).nondefault.set(value=True)
            else:
                await ctx.send(
                    "Make sure you add the role for this using `{}lds specrole <role>`".format(
                        ctx.prefix
                    )
                )

        await menu(ctx, e_list, DEFAULT_CONTROLS)

    @lockdownset.command(name="rmspecialchannel", aliases=["rsc"])
    async def remove_special_channel(self, ctx: commands.Context, channels: Greedy[int]):
        """
        Remove a channel to list of channels to lock/unlock for special roles
        """
        if not channels:
            raise commands.BadArgument
        guild = ctx.guild
        chans = await self.config.guild(guild).secondary_channels()
        for chan in channels:
            if chan in chans:
                chans.remove(chan)
                await self.config.guild(guild).secondary_channels.set(chans)

        chan_count = len(chans)
        msg = ""
        for chan_id in chans:
            channel_name = f"<#{chan_id}>"
            msg += f"{chan_id} - {channel_name}\n"
        channel_list = sorted(msg)
        e_list = []
        for page in pagify(msg, shorten_by=1000):

            embed = discord.Embed(
                description="Channel List: {}\n{}".format(chan_count, page),
                colour=await ctx.embed_color(),
            )
            embed.set_author(name=guild.name, icon_url=guild.icon_url)
            embed.set_footer(text="Lockdown Channel Sttings")
            e_list.append(embed)
        await ctx.send("Removed from the list, here's your current channels")
        await menu(ctx, e_list, DEFAULT_CONTROLS)
        nondefault = await self.config.guild(guild).nondefault()
        check_role = await self.config.guild(guild).secondary_role()
        if not chans:
            if nondefault is True:
                if not check_role:
                    await self.config.guild(guild).nondefault.set(value=False)
                    await ctx.send(
                        "Removed secondary configurations from this guild as there is no role or channels assigned"
                    )

    @lockdownset.command()
    async def rmchan(self, ctx: commands.Context, channels: Greedy[int]):
        """
        Remove a channel to list of channels to lock/unlock
        You can only remove one at a time otherwise run `[p]lds reset`
        """
        if not channels:
            raise commands.BadArgument
        guild = ctx.guild
        chans = await self.config.guild(guild).channels()
        for chan in channels:
            if chan in chans:
                chans.remove(chan)
                await self.config.guild(guild).channels.set(chans)

        chan_count = len(chans)
        msg = ""
        for chan_id in chans:
            channel_name = f"<#{chan_id}>"
            msg += f"{chan_id} - {channel_name}\n"
        channel_list = sorted(msg)
        e_list = []
        for page in pagify(msg, shorten_by=1000):

            embed = discord.Embed(
                description="Channel List: {}\n{}".format(chan_count, page),
                colour=await ctx.embed_color(),
            )
            embed.set_author(name=guild.name, icon_url=guild.icon_url)
            embed.set_footer(text="Lockdown Channel Sttings")
            e_list.append(embed)
        await ctx.send("Removed from the list, here's your current channels")
        await menu(ctx, e_list, DEFAULT_CONTROLS)

    @lockdownset.command(name="reset")
    async def clear_config(self, ctx: commands.Context):
        """
        Fully resets server configuation to default, and clears all channels from list
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(
            "Are you certain about this? This will wipe all settings/messages/channels in your servers configuration Type: `RESET THIS GUILD` to continue (must be typed exact)"
        )
        try:
            confirm_reset = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_reset.content != "RESET THIS GUILD":
                return await ctx.send("Okay, not resetting today")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply")
        await self.config.guild(ctx.guild).clear_raw()
        await ctx.send("Guild Reset, goodluck")

    @lockdownset.command()
    async def lockmsg(self, ctx: commands.Context, *, str=None):
        """
        Sets the lock message for your server
        """
        guild = ctx.guild
        msg = await self.config.guild(guild).lockdown_message()
        if msg is not None:
            await ctx.send(f"Your current message is {msg}")
        await self.config.guild(guild).lockdown_message.set(value=str)
        await ctx.send(f"Your lockdown message has been changed to:\n `{str}`")

    @lockdownset.command(name="unlockmsg")
    async def unlockmsg(self, ctx: commands.Context, *, str=None):
        """
        Sets the unlock message for your server
        """
        guild = ctx.guild
        msg = await self.config.guild(guild).unlockdown_message()
        if msg is not None:
            await ctx.send(f"Your current message is {msg}")
        await self.config.guild(guild).unlockdown_message.set(value=str)
        await ctx.send(f"Your unlock message has been changed to:\n `{str}`")

    @lockdownset.command(name="setvc")
    async def vc_setter(
        self, ctx: commands.Context, *, vc_channel: Greedy[discord.VoiceChannel],
    ):
        """
        Adds channel to list of voice chats to lock/unlock
        """
        if vc_channel is None:
            return await ctx.send_help()
        guild = ctx.guild
        vc_chans = await self.config.guild(guild).vc_channels()
        vc_chans.append(vc_channel.id)
        await self.config.guild(guild).vc_channels.set(vc_chans)
        await ctx.send(f"Added {vc_channel.name} to the list")

    @lockdownset.command(name="notify")
    async def notify_channels(self, ctx: commands.Context, *, option: bool = True):
        """
        Set whether to send channel notifications on lockdown and unlockdown to each effected channel
        """
        guild = ctx.guild
        confirm = await self.config.guild(guild).send_alert()
        if option is False:
            await self.config.guild(guild).send_alert.set(value=False)
            await ctx.send("Will silence the channel notifications on lockdown/unlockdown")
            return
        if confirm is True:
            await ctx.send(
                f"Currently you're set to send notification in channels that are locked/unlocked if there are messages set. To change this, run `{ctx.prefix}lockdownset notify false`"
            )
            return
        await self.config.guild(guild).send_alert.set(value=True)
        await ctx.send(
            "Will now send notification in each channel effected for lockdown/unlockdown"
        )

    @lockdownset.command(name="specrole")
    async def add_role(self, ctx: commands.Context, *, role: discord.Role):
        """
        Add a role to lock from sending messages instead of the @everyone role
        Make sure to add the channels that are applicable
        """
        if not role:
            return await ctx.send_help()

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        guild = ctx.guild
        nondefault = await self.config.guild(guild).nondefault()
        get_role = await self.config.guild(guild).secondary_role()
        if get_role:
            await ctx.send(f"You want to change <@&{get_role}> to {role.mention}? `[yes|no]`")
            try:
                confirm_change = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_change.content.lower() != "yes":
                    return await ctx.send(
                        f"Looks like we will keep <@&{get_role}> as your secondary role."
                    )
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply!")

        await self.config.guild(guild).secondary_role.set(role.id)
        await ctx.send(f"Added {role.mention} to your configuration")
        spec_chans = await self.config.guild(guild).secondary_channels()
        if nondefault is False:
            if spec_chans:
                await self.config.guild(guild).nondefault.set(value=True)
            else:
                return await ctx.send(
                    "Make sure you set up your channels for this role by doing `{}lds asc <..channels..>`".format(
                        ctx.prefix
                    )
                )

    @checks.mod_or_permissions(manage_channels=True)
    @commands.command()
    @commands.guild_only()
    async def lockvc(self, ctx: commands.Context):
        """
        Locks all voice channels
        """
        set_check = await self.config.guild(ctx.guild).vc_channels()
        if not set_check:
            await ctx.send("You need to set the channels using `{}lds setvc <channels>`".format(ctx.prefix))
        guild = ctx.guild
        author = ctx.author
        channel = ctx.guild.get_channel
        channel_ids = await self.config.guild(guild).vc_channels()
        role = guild.default_role
        for voice_channel in guild.channels:
            if voice_channel.id in channel_ids:
                overwrite = voice_channel.overwrites_for(role)
                overwrite.update(read_messages=True, connect=False, speak=False, stream=False)
                try:
                    await voice_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Locked Voice Chats. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Couldn't lock {}".format(voice_channel.mention))

        await ctx.send(":mute: Locked voice channels")

    @checks.mod_or_permissions(manage_channels=True)
    @commands.command()
    @commands.guild_only()
    async def unlockvc(self, ctx: commands.Context):
        """
        Unlocks all voice channels
        """
        set_check = await self.config.guild(ctx.guild).vc_channels()
        if not set_check:
            await ctx.send("You need to set the channels using `{}lds setvc <channels>`".format(ctx.prefix))
        guild = ctx.guild
        author = ctx.author
        channel = ctx.guild.get_channel
        channel_ids = await self.config.guild(guild).vc_channels()
        role = guild.default_role
        for voice_channel in guild.channels:
            if voice_channel.id in channel_ids:
                overwrite = voice_channel.overwrites_for(role)
                overwrite.update(read_messages=None, connect=None, speak=None, stream=None)
                try:
                    await voice_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Unlocked Voice Chats. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Couldn't unlock {}".format(voice_channel.mention))

        await ctx.send(":speaker: Voice channels unlocked.")

    @commands.command(aliases=["lockchan", "lockit"])
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def channellock(
        self,
        ctx: commands.Context,
        channel: Union[discord.TextChannel, discord.VoiceChannel] = None,
    ):
        """Locking down selected text/voice channel"""
        author = ctx.author
        role = ctx.guild.default_role
        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(role)
        bot_overwrite = channel.overwrites_for(self.bot.user)
        #   Checking channel type

        if channel.type == discord.ChannelType.text:
            if overwrite.send_messages is False:
                return await ctx.send(
                    "{} is already locked. To unlock, please use `{}channelunlock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            if not bot_overwrite.send_messages:
                bot_overwrite.update(send_messages=True)
            overwrite.update(send_messages=False)
        elif channel.type == discord.ChannelType.voice:
            if overwrite.connect is False:
                return await ctx.send(
                    "{} is already locked. To unlock, please use `{}channelunlock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(connect=False)
        try:
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason="Lockdown in effect. Requested by {} ({})".format(author.name, author.id),
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        await ctx.send("Done. Locked {}".format(channel.mention))

    @commands.command(aliases=["ulockchan", "unlockit"])
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def channelunlock(
        self,
        ctx: commands.Context,
        channel: Union[discord.TextChannel, discord.VoiceChannel] = None,
    ):
        """Unlocking down selected text/voice channel"""
        author = ctx.author
        role = ctx.guild.default_role
        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(role)

        #   Checking channel type
        if channel.type == discord.ChannelType.text:
            if overwrite.send_messages is None:
                return await ctx.send(
                    "{} is already unlocked. To lock, please use `{}channellock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(send_messages=None)
        elif channel.type == discord.ChannelType.voice:
            if overwrite.connect is None:
                return await ctx.send(
                    "{} is already unlocked. To lock, please use `{}channellock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(connect=None)

        try:
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason="Lockdown over. Requested by {} ({})".format(author.name, author.id),
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        await ctx.send("Unlocked {}".format(channel.mention))
