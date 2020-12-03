import asyncio
import logging
from typing import Union

import discord
from redbot.core import Config, checks, commands
from redbot.core.commands import Greedy
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu


# core functioning from Sharky-Cogs @https://github.com/SharkyTheKing/Sharky
class LockItUp(commands.Cog):
    """Lockdown a list of channels, a channel, or the whole server."""

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
            "music_channels": [],
            "send_alert": True,
            "nondefault": False,
            "secondary_role": None,
            "secondary_channels": [],
            "lock_role": None,
            "logging_channel": None,
        }

        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.kko-cogs.lockitup")

    async def red_delete_data_for_user(self, **kwargs):
        """This cog does not store user data"""
        return

    async def ack_lockdown(self, ctx: commands.Context, guild: discord.Guild):
        msg = await self.config.guild(guild).lockdown_message()
        color1 = 0xF50A0A
        e = discord.Embed(
            color=discord.Color(color1),
            title=f"Server Lockdown :lock:",
            description=msg,
            timestamp=ctx.message.created_at,
        )
        e.set_footer(text=f"{guild.name}")
        channel_ids = await self.config.guild(guild).channels()
        spec_check = await self.config.guild(guild).secondary_channels()
        if spec_check:
            channel_ids += spec_check
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                try:
                    await guild_channel.send(embed=e)
                    await asyncio.sleep(0.3)
                except discord.Forbidden:
                    self.log.info("Could not send message to {}".format(guild_channel.name))
                    await self.loggerhook(
                        guild,
                        error=f"Can't send messages in {guild_channel.mention} after lock down. Check bot perms.",
                    )

    async def reign_lockdown(self, ctx: commands.Context, guild: discord.Guild):
        bot_override = self.bot.user
        author = ctx.author
        channel_ids = await self.config.guild(guild).channels()
        role = guild.default_role
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite1 = guild_channel.overwrites_for(bot_override)
                overwrite1.update(send_messages=True, embed_links=True)
                try:
                    await guild_channel.set_permissions(
                        bot_override,
                        overwrite=overwrite1,
                        reason="Securing bot overrides for lockdown",
                    )
                    await asyncio.sleep(0.3)
                except Exception:
                    return await ctx.send(
                        "You'll need to give me permissions to send messages in the channels I am locking down, so I can manage that permissions for others. I failed trying to secure my own overrides. This lockdown will not resume. Best way to fix this is ensure my role in the server settings has send messages permission turned on."
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
                    await asyncio.sleep(0.2)
                except discord.Forbidden:
                    self.log.info("Could not lockdown {}".format(guild_channel.name))
                    await self.loggerhook(
                        guild,
                        error=f"Could not lockdown {guild_channel.name}. Check my permissions and make sure I can manage the channel",
                    )

        msg = await self.config.guild(guild).lockdown_message()
        if msg:
            notifier = await self.config.guild(guild).send_alert()
            if notifier is True:
                await self.ack_lockdown(ctx, guild)

    async def secondary_lockdown(self, ctx: commands.Context, guild: discord.Guild):
        bot_override = self.bot.user
        author = ctx.author
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
                        await asyncio.sleep(0.5)
                except Exception as er:
                    return await self.loggerhook(
                        guild,
                        error=f"Error on lock for {guild_channel.mention} in securing bot overrides. Make sure I have the ability to send messages in these channels so I can manage this permission for others. ERROR: {er}\nLockdown will not resume",
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
                    await asyncio.sleep(0.5)
                except discord.Forbidden as er:
                    self.log.info("In {}, could not lock {}".format(guild.id, guild_channel.name))
                    await self.loggerhook(
                        guild,
                        error=f"Error on lockdown for {guild_channel.mention}\n```diff\n+ ERROR:\n- {er}\n```",
                    )

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.guild)
    @checks.mod_or_permissions(manage_channels=True)
    @checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def lockdown(self, ctx: commands.Context, lockrole: bool = False):
        """
        Lockdown a server

        If you pass true, your @everyone role will also be denied permissions from within the role menu
        """
        guild = ctx.guild
        config_check = await self.config.guild(guild).channels()
        if not config_check:
            await ctx.send(
                "You need to set this up by running `{}lockdownset`, first and stepping through those configuration subcommands".format(
                    ctx.prefix
                )
            )
            return

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        lock_check = await self.config.guild(ctx.guild).locked()
        if lock_check is True:
            return await ctx.send("You're already locked")

        await ctx.send("You ready to lock up? `[yes|no]`")
        try:
            confirm_lock = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_lock.content.lower() != "yes":
                return await ctx.send("Looks like we aren't unlocking this thing today")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        await ctx.trigger_typing()
        nondefault_lock = await self.config.guild(guild).nondefault()
        if nondefault_lock is True:
            await self.secondary_lockdown(ctx, guild)

        # proceed to default lockdown
        await self.reign_lockdown(ctx, guild)

        if lockrole:
            perms = ctx.guild.get_role(ctx.guild.id).permissions
            perms.send_messages = False
            if not ctx.me.guild_permissions.manage_roles:
                await ctx.send(
                    "I'm missing the ability to manage roles so we will skip making changes to roles in the server settings"
                )
            try:
                await ctx.guild.default_role.edit(
                    permissions=perms, reason=f"Role Lockdown requested by {ctx.author.name}"
                )
                await self.config.guild(ctx.guild).lock_role.set(True)
            except Exception as e:
                await ctx.send(
                    f"Getting an error when attempting to edit role permissions in server settings:\n{e}\nSkipping..."
                )

        # finalize
        try:
            await ctx.send(
                "We're locked up, fam. Revert this by running `{}unlockdown`".format(ctx.prefix)
            )
        except Exception as er:
            self.log.info(
                f"Couldn't secure overrides in Guild {ctx.guild.name} ({ctx.guild.id}): Locked as requested."
            )
            await self.loggerhook(
                guild,
                error=f"Unable to send messages on lockdown to your channels due to the following error\n```diff\n+ ERROR:\n- {er}\n```",
            )

        await self.config.guild(guild).locked.set(True)  # write it to configs

    async def ack_unlockdown(self, ctx: commands.Context, guild: discord.Guild):
        msg = await self.config.guild(guild).unlockdown_message()
        color2 = 0x2FFFFF
        e = discord.Embed(
            color=discord.Color(color2),
            title=f"Server Unlock :unlock:",
            description=msg,
            timestamp=ctx.message.created_at,
        )
        e.set_footer(text=f"{guild.name}")

        channel_ids = await self.config.guild(guild).channels()
        spec_check = await self.config.guild(guild).secondary_channels()
        if spec_check:
            channel_ids += spec_check
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                try:
                    await guild_channel.send(embed=e)
                    await asyncio.sleep(0.3)
                except discord.Forbidden:
                    self.log.info("Could not send message to {}".format(guild_channel.name))
                    await self.loggerhook(
                        guild,
                        error=f"Can't send messages in {guild_channel.mention} after lock down. Check bot perms.",
                    )

    async def reign_unlockdown(self, ctx: commands.Context, guild: discord.Guild):
        author = ctx.author
        channel_ids = await self.config.guild(guild).channels()
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
                    await asyncio.sleep(0.2)
                except discord.Forbidden as er:
                    self.log.info("Could not unlock {}".format(guild_channel.name))
                    await self.loggerhook(
                        guild,
                        error=f"Error on unlock for {guild_channel.mention}\n```diff\n+ ERROR:\n- {er}\n```",
                    )

        msg = await self.config.guild(guild).unlockdown_message()
        if msg:
            notifier = await self.config.guild(guild).send_alert()
            if notifier is True:
                await self.ack_unlockdown(ctx, guild)

    async def secondary_unlockdown(self, ctx: commands.Context, guild: discord.Guild):
        author = ctx.author
        special_chans = await self.config.guild(guild).secondary_channels()
        spec_role = await self.config.guild(guild).secondary_role()
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
                    await asyncio.sleep(0.5)
                except discord.Forbidden as er:
                    self.log.info(
                        "In {}, could not unlock {}".format(guild.id, guild_channel.name)
                    )
                    await self.loggerhook(
                        guild,
                        error=f"Error on unlock for {guild_channel.mention}\n```diff\n+ ERROR:\n- {er}\n```",
                    )

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.guild)
    @checks.mod_or_permissions(manage_channels=True)
    @checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def unlockdown(self, ctx: commands.Context, lockrole: bool = False):
        """
        Unlock the server

        If you pass true, your @everyone role will also be allowed permissions from within the role menu to send messages
        """
        guild = ctx.guild

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        unlock_check = await self.config.guild(ctx.guild).locked()
        if unlock_check is False:
            return await ctx.send("You're not locked")

        await ctx.send("R U Sure About That? `[yes|no]`")
        try:
            confirm_unlock = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_unlock.content.lower() != "yes":
                return await ctx.send("Looks like we aren't unlocking this thing today")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        await ctx.trigger_typing()
        nondefault_lock = await self.config.guild(guild).nondefault()
        if nondefault_lock is True:
            await self.secondary_unlockdown(ctx, guild)

        # proceed to default unlockdown
        await self.reign_unlockdown(ctx, guild)

        if lockrole:
            perms = ctx.guild.get_role(ctx.guild.id).permissions
            perms.send_messages = True
            if not ctx.me.guild_permissions.manage_roles:
                await ctx.send(
                    "I'm missing the ability to manage roles so we will skip making changes to roles in the server settings"
                )
            try:
                await ctx.guild.default_role.edit(
                    permissions=perms, reason=f"Role Unlock requested by {ctx.author.name}"
                )
                await self.config.guild(ctx.guild).lock_role.set(True)
            except Exception as e:
                await ctx.send(
                    f"Getting an error when attempting to edit role permissions in server settings:\n{e}\nSkipping..."
                )

        # finalize
        try:
            await ctx.send("Server is unlocked")
        except discord.Forbidden:
            await self.loggerhook(
                guild,
                error="I lack perms to successfully unlock this server — please verify I have the send messagees permissions myself in the role menu",
            )
            return

        await self.config.guild(guild).locked.set(False)  # write it to configs

    @commands.group(aliases=["lds"])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    @checks.bot_has_permissions(embed_links=True)
    async def lockdownset(self, ctx: commands.Context):
        """
        Settings for lockdown
        """

    @lockdownset.command(name="logchan")
    @checks.admin_or_permissions(manage_guild=True)
    @checks.bot_has_permissions(manage_channels=True, manage_webhooks=True)
    async def logging_channel(self, ctx: commands.Context, logchannel: discord.TextChannel):
        """
        Set up logging channel to record what channels the bot couldn't successfully lock/unlock
        """
        guild = ctx.guild

        await self.config.guild(guild).logging_channel.set(logchannel.id)
        try:
            await self.loggerhook(
                guild,
                error="THIS IS A TEST\n```diff\n+ If you are seeing this, you have correctly set up error log for lock/unlock features\n```",
            )
        except Exception:
            self.log.info(f"Error'd on setup in {guild.id} for webhook logging")

        try:
            await ctx.send(
                f"Set up the logging — will send webhooks to {logchannel.mention} when there is a permissions error on lock/unlocks"
            )
        except Exception as e:
            self.log.info(f"Error setting up guild logs in {ctx.guild.id}: Error {e}")

    async def loggerhook(self, guild: discord.Guild, error: str):
        channel = guild.get_channel(await self.config.guild(guild).logging_channel())
        if not channel or not (channel.permissions_for(guild.me).manage_webhooks):
            await self.config.guild(guild).logging_channel.clear()
            return

        webhook = None
        for hook in await channel.webhooks():
            if hook.name == self.bot.user.name:
                webhook = hook
        if webhook is None:
            webhook = await channel.create_webhook(name=self.bot.user.name)

        await webhook.send(
            content=f"**LockItUp Error Log**\n{error}",
            username=self.bot.user.name,
            avatar_url=self.bot.user.avatar_url,
        )

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

        chan_count = len(get_channel)
        if not get_channel:
            e = discord.Embed(
                color=await ctx.embed_color(),
                title="Lockdown Settings:",
                description="No channels added",
            )
            check_specs = fetch_all["nondefault"]
            if check_specs:
                e.add_field(
                    name="Special Role",
                    value=f"<@&{get_sec_role}> — `{get_sec_role}`" if get_sec_role else "**None**",
                    inline=False,
                )
                spec_msg = ""
                for chan_id in get_sec_chans:
                    channel_name = f"<#{chan_id}>"
                    spec_msg += f"`{chan_id}` — {channel_name}\n"
                e.add_field(
                    name="Special Channels",
                    value=f"{spec_msg}" if get_sec_chans else "**None**",
                    inline=False,
                )
            e.add_field(name="Lock Message:", value=get_lock if get_lock else "**None**")
            e.add_field(name="Unlock Message:", value=get_unlock if get_unlock else "**None**")
            e.add_field(
                name="Channel Notification:",
                value="**Enabled**" if check_silent else "**Disabled**",
            )
            return await ctx.send(embed=e)
        else:
            msg = ""
            for chan_id in get_channel:
                channel_name = f"<#{chan_id}>"
                msg += f"`{chan_id}` — {channel_name}\n"

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
            if check_specs:
                e.add_field(
                    name="Special Role",
                    value=f"<@&{get_sec_role}> — `{get_sec_role}`" if get_sec_role else "**None**",
                    inline=False,
                )
                spec_msg = ""
                for chan_id in get_sec_chans:
                    channel_name = f"<#{chan_id}>"
                    spec_msg += f"`{chan_id}` — {channel_name}\n"
                e.add_field(
                    name="Special Channels",
                    value=f"{spec_msg}" if get_sec_chans else "**None**",
                    inline=False,
                )

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

        IDs are also accepted.
        """
        if not channels:
            raise commands.BadArgument
        guild = ctx.guild
        chans = await self.config.guild(guild).channels()
        if len(chans) > 50:
            return await ctx.send("Think you've added enough. Keep it under 50 please")
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
            msg += f"`{chan_id}` - {channel_name}\n"

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
        if len(chans) > 25:
            return await ctx.send("Think you've added enough. Keep it under 25 please")
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
            msg += f"`{chan_id}` - {channel_name}\n"

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

        Accepts only channel IDs
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
        if not chan_count:
            return await ctx.send(
                "After removing that, no more special channels exist in this server's configuration."
            )
        msg = ""
        for chan_id in chans:
            channel_name = f"<#{chan_id}>"
            msg += f"`{chan_id}` - {channel_name}\n"

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

        Accepts only channel IDs
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
        if not chan_count:
            return await ctx.send(
                "After removing that, no more channels are left in this server's configuration"
            )
        msg = ""
        for chan_id in chans:
            channel_name = f"<#{chan_id}>"
            msg += f"`{chan_id}` - {channel_name}\n"

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
        self,
        ctx: commands.Context,
        *,
        vc_channel: Greedy[discord.VoiceChannel],
    ):
        """
        Adds channel to list of voice chats to lock/unlock
        """
        if vc_channel is None:
            return await ctx.send_help()
        guild = ctx.guild
        vc_chans = await self.config.guild(guild).vc_channels()
        for chan in vc_channel:
            if chan.id not in vc_chans:
                vc_chans.append(chan.id)
                await self.config.guild(guild).vc_channels.set(vc_chans)

        await ctx.send(f"Added to the list")

    @lockdownset.command(name="setmusic")
    async def music_setter(
        self,
        ctx: commands.Context,
        *,
        vc_channel: Greedy[discord.VoiceChannel],
    ):
        """
        Adds channel to list of Music channels to lock/unlock

        Music channels are treated with different perms on unlock (forcing negative overrides for @everyone role to speak)
        """
        if vc_channel is None:
            return await ctx.send_help()
        guild = ctx.guild
        music_chans = await self.config.guild(guild).music_channels()
        for chan in vc_channel:
            if chan.id not in music_chans:
                music_chans.append(chan.id)
                await self.config.guild(guild).music_channels.set(music_chans)

        await ctx.send(f"Added to the list")

    @lockdownset.command(name="rmvc")
    async def vc_remove(
        self,
        ctx: commands.Context,
        *,
        vc_channel: Greedy[int],
    ):
        """
        Remove chat channel from list of voice chats

        Must use ID
        """
        if vc_channel is None:
            return await ctx.send_help()
        guild = ctx.guild
        vc_chans = await self.config.guild(guild).vc_channels()
        for chan in vc_channel:
            if chan in vc_chans:
                vc_chans.remove(chan)
                await self.config.guild(guild).vc_channels.set(vc_chans)
        await ctx.send(f"Added {vc_channel.name} to the list")

    @lockdownset.command(name="remusic")
    async def music_remove(
        self,
        ctx: commands.Context,
        *,
        vc_channel: Greedy[int],
    ):
        """
        Remove channel from list of music chats

        Music channels are treated with different perms on unlock (forcing negative overrides for @everyone role to speak)
        """
        if vc_channel is None:
            return await ctx.send_help()
        guild = ctx.guild
        music_chans = await self.config.guild(guild).music_channels()
        for chan in vc_channel:
            if chan.id in music_chans:
                music_chans.remove(chan.id)
                await self.config.guild(guild).music_channels.set(music_chans)

        await ctx.send(f"Removed from the list")

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

    async def voice_channel_lock(self, author: discord.Member, guild: discord.Guild):
        """Lock function for voice/music channels"""
        voice_channels = await self.config.guild(guild).vc_channels()
        music_channels = await self.config.guild(guild).music_channels()
        if not voice_channels or not music_channels:
            return await ctx.send("You need to add some channels to your configuration using `{}lds setvc|setmusic` to use this")
        role = guild.default_role
        if voice_channels is not None:
            for voice_channel in guild.channels:
                if voice_channel.id in voice_channels:
                    overwrite = voice_channel.overwrites_for(role)
                    overwrite.update(read_messages=True, connect=False, speak=False, stream=False)
                    try:
                        await voice_channel.set_permissions(
                            role,
                            overwrite=overwrite,
                            reason="Locked down Voice Chats at request of {} ({})".format(
                                author.name, author.id
                            ),
                        )
                    except discord.Forbidden:
                        await self.loggerhook.send(
                            guild=guild,
                            error="You gotta give me permissions to manage {} so I can lock it properly".format(voice_channel.mention),
                        )
            await ctx.send("Voice channels locked :mute:")

        # roll on with music channels for lock down
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        if music_channels is not None:
            message = await ctx.send("Detected music channels in your configuration, do you want to lock those too?")
            try:
                confirm_music_too = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_music_too.content.lower() != "yes":
                    return await ctx.send("Okay, won't bother locking those")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply, won't lock your music channels. You can lock those independently. Not sure why they're in your configuration in this case though.")
            for voice_channel in guild.channels:
                if voice_channel.id in music_channels:
                    overwrite = voice_channel.overwrites_for(role)
                    overwrite.update(read_messages=True, connect=False, speak=False, stream=False)
                    try:
                        await voice_channel.set_permissions(
                            role,
                            overwrite=overwrite,
                            reason="Locked down Music Channels at request of {} ({})".format(
                                author.name, author.id
                            ),
                        )
                    except discord.Forbidden:
                        await self.loggerhook.send(
                            guild=guild,
                            error="You gotta give me permissions to manage {} so I can lock it properly".format(voice_channel.mention),
                        )
        await message.edit(content="Music Channels are locked, too.")

    async def voice_channel_unlock(self, author: discord.Member, guild: discord.Guild):
        """Unlock function for voice/music channels"""
        voice_channels = await self.config.guild(guild).vc_channels()
        music_channels = await self.config.guild(guild).music_channels()
        if not voice_channels or not music_channels:
            return await ctx.send("You need to add some channels to your configuration using `{}lds setvc|setmusic` to use this")
        role = guild.default_role
        if voice_channels is not None:
            for voice_channel in guild.channels:
                if voice_channel.id in voice_channels:
                    overwrite = voice_channel.overwrites_for(role)
                    overwrite.update(read_messages=None, connect=None, speak=None, stream=None)
                    try:
                        await voice_channel.set_permissions(
                            role,
                            overwrite=overwrite,
                            reason="Unlocked Voice Chats at request of {} ({})".format(
                                author.name, author.id
                            ),
                        )
                    except discord.Forbidden:
                        await self.loggerhook.send(
                            guild=guild,
                            error="You gotta give me permissions to manage {} so I can lock it properly".format(voice_channel.mention),
                        )
            await ctx.send("Voice channels unlocked :unmute:")

        # roll on with music channels for lock down
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        if music_channels is not None:
            message = await ctx.send("Detected music channels in your configuration, do you want to unlock those too?")
            try:
                confirm_music_too = await ctx.bot.wait_for("message", check=check, timeout=30)
                if confirm_music_too.content.lower() != "yes":
                    return await ctx.send("Okay, won't bother unlocking those")
            except asyncio.TimeoutError:
                return await ctx.send("You took too long to reply, won't unlock your music channels. You can unlock those independently. Not sure why they're in your configuration in this case though.")
            for voice_channel in guild.channels:
                if voice_channel.id in music_channels:
                    overwrite = voice_channel.overwrites_for(role)
                    overwrite.update(read_messages=None, connect=None, speak=False, stream=False)
                    try:
                        await voice_channel.set_permissions(
                            role,
                            overwrite=overwrite,
                            reason="Unlocked Music Channels at request of {} ({})".format(
                                author.name, author.id
                            ),
                        )
                    except discord.Forbidden:
                        await self.loggerhook.send(
                            guild=guild,
                            error="You gotta give me permissions to manage {} so I can unlock it properly".format(voice_channel.mention),
                        )
            await message.edit(content="Music Channels are unlocked, too.")

    @checks.mod_or_permissions(manage_channels=True)
    @commands.command()
    @commands.guild_only()
    async def lockvc(self, ctx: commands.Context):
        """
        Locks all voice channels
        """
        set_check = await self.config.guild(ctx.guild).vc_channels()
        if not set_check:
            return await ctx.send(
                "You need to set the channels using `{}lds setvc <channels>`".format(ctx.prefix)
            )
        guild = ctx.guild
        author = ctx.author
        await self.voice_channel_lock(guild=guild, author=author)

    @checks.mod_or_permissions(manage_channels=True)
    @commands.command()
    @commands.guild_only()
    async def unlockvc(self, ctx: commands.Context):
        """
        Unlocks all voice channels
        """
        set_check = await self.config.guild(ctx.guild).vc_channels()
        if not set_check:
            return await ctx.send(
                "You need to set the channels using `{}lds setvc <channels>`".format(ctx.prefix)
            )
        guild = ctx.guild
        author = ctx.author

        await self.voice_channel_unlock(guild=guild, author=author)

    @commands.command(name="lockit", aliases=["lockchan"])
    @checks.mod_or_permissions(manage_messages=True)
    @checks.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def channellock(
        self,
        ctx: commands.Context,
        channel: Union[discord.TextChannel, discord.VoiceChannel] = None,
    ):
        """Lock selected text/voice channel"""
        author = ctx.author
        role = ctx.guild.default_role
        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(role)
        bot_overwrite = channel.overwrites_for(ctx.bot.user)
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
                ctx.bot.user,
                overwrite=bot_overwrite,
                reason=f"Securing overrides for {ctx.bot.user.name}",
            )
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason="Lockdown in effect. Requested by {} ({})".format(author.name, author.id),
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        await ctx.send("Done. Locked {}".format(channel.mention))

    @commands.command(name="unlockit", aliases=["ulockchan"])
    @checks.mod_or_permissions(manage_messages=True)
    @checks.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def channelunlock(
        self,
        ctx: commands.Context,
        channel: Union[discord.TextChannel, discord.VoiceChannel] = None,
    ):
        """Unlock selected text/voice channel"""
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
