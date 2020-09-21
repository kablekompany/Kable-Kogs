import asyncio
import logging
from datetime import datetime
from os.path import exists
from typing import Optional, Union

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils import menus
from redbot.core.utils.chat_formatting import box, pagify

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
            "embed_set": False,
            "send_alert": True,
            "nondefault": False,
        }

        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("kko.cogs.lockitup")

    async def red_delete_data_for_user(self, **kwargs):
        """This cog does not store user data"""
        return

    @commands.command()
    @checks.mod_or_permissions(manage_channels=True)
    async def lockdown(self, ctx):
        """
        Lockdown a server
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        lock_check = await self.config.guild(ctx.guild).locked()
        if lock_check is True:
            return await ctx.send("You're already locked")
        guild = ctx.guild
        channel_ids = await self.config.guild(guild).channels()
        if not channel_ids:
            await ctx.send("You need to set this up by running `;;lockdownset addchan` first!")
            return

        await ctx.send("You sure you wanna lock up? `[yes|no]`")

        try:
            confirm_lockdown = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_lockdown.content.lower() != "yes":
                return await ctx.send("Okay. Stop wasting my time")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        author = ctx.author
        role = guild.default_role
        conf = self.config.guild(ctx.guild)
        msg = await self.config.guild(guild).lockdown_message()
        color1 = 0xF50A0A
        color2 = 0x2FFFFF
        e = discord.Embed(
            color=discord.Color(color1),
            title=f"Server Lockdown :lock:",
            description=msg,
            timestamp=ctx.message.created_at,
        )
        e.set_footer(text=f"{guild.name}")
        bot_override = ctx.bot.user

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
                    confirm = await self.config.guild(guild).send_alert()
                    if confirm is True:
                        try:
                            await guild_channel.send(embed=e)
                        except discord.Forbidden:
                            self.log.info(
                                "Could not send message to {}".format(guild_channel.name)
                            )

        await ctx.send(
            "We're locked up, fam. Revert this by running `{}unlockdown`".format(ctx.prefix)
        )
        await self.config.guild(guild).locked.set(True)

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def unlockdown(self, ctx):
        """
        Ends the lockdown for the guild
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        lock_check = await self.config.guild(ctx.guild).locked()
        if lock_check is False:
            return await ctx.send("You're not locked")
        guild = ctx.guild
        channel_ids = await self.config.guild(guild).channels()
        if not channel_ids:
            await ctx.send("You need to set this up by running `;;lockdownset addchan` first!")
            return

        await ctx.send("U Sure About that? `[yes|no]`")
        try:
            confirm_unlockdown = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_unlockdown.content.lower() != "yes":
                return await ctx.send("Okay. Won't unlock the guild.")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        check_embed = await self.config.guild(guild).embed_set()
        author = ctx.author
        role = guild.default_role
        msg = await self.config.guild(guild).unlockdown_message()
        color2 = 0x2FFFFF
        e = discord.Embed(
            color=discord.Color(color2),
            title=f"Server Unlocked :unlock:",
            description=msg,
            timestamp=ctx.message.created_at,
        )
        e.set_footer(text=ctx.guild.name)
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite.update(send_messages=None)
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown ended. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Couldn't unlock {}".format(guild_channel.mention))
                if msg is not None:
                    confirm = await self.config.guild(guild).send_alert()
                    if confirm is True:
                        if check_embed is False:
                            try:
                                await guild_channel.send(content=msg)
                            except discord.Forbidden:
                                self.log.info(
                                    "Could not send message to {}".format(guild_channel.name)
                                )
                        else:
                            try:
                                await guild_channel.send(embed=e)
                            except discord.Forbidden:
                                self.log.info(
                                    "Could not send messages in {}".format(guild_channel.name)
                                )
                # await asyncio.sleep(4)
                # await message.edit(content=f"<a:HehWellCyaNever:708582524309471252>")

        await ctx.send("Guild is now unlocked.")
        await self.config.guild(guild).locked.set(False)

    @commands.group(aliases=["lds"])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def lockdownset(self, ctx):
        """
        Settings for lockdown
        For each setting, pass one ID each invocation. So if you need to add multiple channels, run the commands to do so multiple times (same for removal, duh)
        """
        pass

    @lockdownset.command(name="showsettings")
    async def show_settings(self, ctx):
        """See Guild Configuration"""
        guild = ctx.guild
        get_channel = await self.config.guild(guild).channels()
        get_lock = await self.config.guild(guild).lockdown_message()
        get_unlock = await self.config.guild(guild).unlockdown_message()
        check_embed = await self.config.guild(guild).embed_set()
        check_silent = await self.config.guild(guild).send_alert()
        # get_role = await self.config.guild(guild).roles()
        # role = ""
        embed_list = []
        chan = ""
        for channel in get_channel:
            chan += "'{}' - <#{}>\n".format(channel, channel)
        
        #channel_embed = list(pagify(chan, page_length=1000))
        #for idx, page in enumerate(channel_embed, start=1): #from sharky lockdown - to add on potential bot relaunch 
        e = discord.Embed(
                color=await ctx.embed_color(), title="Lockdown Config:", description=chan,
        )

        # e.add_field(name="Channels", value=chan, inline=False)
        e.add_field(name="Lock Message:", value=get_lock, inline=False)
        e.add_field(name="Unlock Message:", value=get_unlock, inline=False)
        e.add_field(name="Unlock Embed", value=check_embed, inline=False)
        e.set_footer(text=f"{guild.name}")
            #embed_list.append(e)

        await ctx.send(embed=e)
        # e.add_field(name="Non-Default Roles", value=role, inline=False)

        #await ctx.send(embed=e)

    @lockdownset.command("embed")
    async def send_embed(self, ctx: commands.Context, *, default: bool = None):
        """
        Indicate if you would like to send an embed or not on unlock
        """
        guild = ctx.guild
        embed_check = await self.config.guild(guild).embed_set()
        if default is None:
            await ctx.send(
                "Pass True or False. True sends an embed on unlock, False silences the embed and sends plain text on unlock. It's false by default"
            )
            return
        if default is False:
            await ctx.send(
                "Alright, will send unlock message in plain text if it's set (`;;lockdownset unlockmsg`)"
            )
            await self.config.guild(guild).embed_set.set(default)
            return
        await self.config.guild(guild).embed_set.set(default)
        await ctx.send(
            "Will send an embed with your unlock message as the body, if you've set it up"
        )

    @lockdownset.command()
    async def addchan(self, ctx: commands.Context, *channel: discord.TextChannel):
        """
        Adds channel to list of channels to lock/unlock
        You can add as many as needed
        Example: `;;lds addchan general support bot-commands`
        IDs are also accepted.
        """
        if not channel:
            await ctx.send_help()
            return
        guild = ctx.guild
        chans = await self.config.guild(guild).channels()
        for chan in channel:
            if chan not in chans:
                chans.append(chan.id)
                await self.config.guild(guild).channels.set(chans)
            else:
                continue
        get_channel = await self.config.guild(guild).channels()
        chan = ""
        for channel in get_channel:
            chan += "<#{}>\n".format(channel)
        await ctx.send("**Channel List:**\n{}".format(chan))

    @lockdownset.command()
    async def rmchan(self, ctx: commands.Context, *channel: int):
        """
        Remove a channel to list of channels to lock/unlock
        You can only remove one at a time otherwise run `[p]lds reset`
        """
        if not channel:
            await ctx.send("Give me a channel ID to remove it from this servers configuration")
            return
        guild = ctx.guild
        chans = await self.config.guild(guild).channels()
        for chan in channel:
            if chan not in chans:
                chans.remove(chan)
                await self.config.guild(guild).channels.set(chans)

        await ctx.send(f"{channel} removed")

    @lockdownset.command(name="reset")
    async def clear_config(self, ctx):
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
        self, ctx: commands.Context, *, vc_channel: Optional[discord.VoiceChannel] = None,
    ):
        """
        Adds channel to list of voice chats to lock/unlock
        """
        if vc_channel is None:
            await ctx.send("Give a channel to me idiot")
            return
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

    @lockdownset.command(name="addrole")
    async def add_role(self, ctx: commands.Context, *, role: discord.Role):
        """
        NOTE: This does not implement yet!
        Add a role to lock from sending messages instead of the @everyone role
        """
        guild = ctx.guild
        role_list = await self.config.guild(guild).roles()
        role_list.append(role.id)
        await self.config.guild(guild).roles.set(role_list)
        await ctx.send(
            f"{role.name} added to the config. Any locks/unlocks will now effect this role for channels in your configuration"
        )
        await self.config.guild(guild).nondefault.set(value=True)

    @checks.mod_or_permissions(manage_channels=True)
    @commands.command()
    async def lockvc(self, ctx):
        """
        Locks all voice channels
        """
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

    @checks.mod()
    @commands.command()
    async def unlockvc(self, ctx):
        """
        Unlocks all voice channels
        """
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

    @commands.command(aliases=["lockchan"])
    @checks.mod_or_permissions(manage_messages=True)
    async def channellock(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Locking down selected text/voice channel"""
        author = ctx.author
        role = ctx.guild.default_role
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

    @commands.command(aliases=["ulockchan"])
    @checks.mod_or_permissions(manage_messages=True)
    async def channelunlock(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Unlocking down selected text/voice channel"""
        author = ctx.author
        role = ctx.guild.default_role
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
