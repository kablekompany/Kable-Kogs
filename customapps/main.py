import asyncio
from datetime import datetime, timedelta
from typing import Any, Literal

import discord
from discord.ext.commands import errors
from discord.utils import get
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.utils.antispam import AntiSpam
from redbot.core.utils.predicates import MessagePredicate

Cog: Any = getattr(commands, "Cog", object)


RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]
# thanks phen

default = {
    "app_check": False,
    "name": [],
    "timezone": [],
    "age": [],
    "days": [],
    "hours": [],
    "position": [],
    "experience": [],
    "reasonforinterest": [],
    "perkslinking": [],
    "commandcontrol": [],
    "coinsmissing": [],
    "botadvice": [],
    "botuse": [],
    "finalcomments": [],
}
# TODO - remove hard coded questions and application reference from DMO theme and make it agnostic
questions = {
    "question1": [],
    "question2": [],
    "question3": [],
    "question4": [],
    "question5": [],
    "question6": [],
    "question7": [],
    "question8": [],
    "question9": [],
    "question10": [],
    "question11": [],
    "question12": [],
    "question13": [],
    "applicant_id": None,
    "accepter_id": None,
    "channel_id": None,
}


class CustomApps(Cog):
    """
    Custom staff applications
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=73837383738, force_registration=True,)
        self.config.register_member(**default)
        self.config.register_guild(**questions)
        self.antispam = {}

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int):
        await self.config.member_from_ids(user_id).clear()

    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def apply(self, ctx: commands.Context):
        """Apply to be a staff member."""
        role_add = get(ctx.guild.roles, name="Applicant")
        app_data = await self.config.guild(ctx.guild).all()
        user_data = self.config.member(ctx.author)
        answers = []
        channel = get(ctx.guild.text_channels, name="staff-applications")
        if ctx.guild not in self.antispam:
            self.antispam[ctx.guild] = {}
        if ctx.author not in self.antispam[ctx.guild]:
            self.antispam[ctx.guild][ctx.author] = AntiSpam([(timedelta(days=2), 1)])
        if self.antispam[ctx.guild][ctx.author].spammy:
            return await ctx.send("Uh oh, you're doing this way too frequently.")
        if role_add is None:
            return await ctx.send("Uh oh. Looks like your Admins haven't added the required role.")
        if channel is None:
            return await ctx.send(
                "Uh oh. Looks like your Admins haven't added the required channel."
            )
        try:
            available_positions = "Moderator\nSupport Specialist\nGiveaway Manager\nHeist Manager"
            await ctx.author.send(
                f"Let's start right away! You have maximum of 5 minutes for each question.\nOur current available positions are {available_positions}\nReply with `mel cute` to continue"
            )
        except discord.Forbidden:
            return await ctx.send(f"{ctx.author.mention} I can't DM you. Do you have them closed?")
        await ctx.send(f"Okay, {ctx.author.mention}, I've sent you a DM.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        try:
            position = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.position.set(position.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question1"])
        try:
            name = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.name.set(name.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question2"])
        try:
            timezone = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.timezone.set(timezone.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question3"])
        try:
            age = await self.bot.wait_for("message", timeout=300, check=check)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        # try:
        #     a = int(age.content)
        # except commands.CommandInvokeError:
        #     return await ctx.author.send("Start over, and this time make sure the response for this question is what's asked for, LOL")
        await ctx.author.send(app_data["question4"])
        try:
            days = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.days.set(days.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question5"])
        try:
            hours = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.hours.set(hours.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question6"])
        try:
            experience = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.experience.set(experience.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question7"])
        try:
            reasonforinterest = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.reasonforinterest.set(reasonforinterest.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question8"])
        try:
            perkslinking = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.perkslinking.set(perkslinking.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question9"])
        try:
            commandcontrol = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.commandcontrol.set(commandcontrol.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question10"])
        try:
            coinsmissing = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.coinsmissing.set(coinsmissing.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question11"])
        try:
            botadvice = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.botadvice.set(botadvice.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question12"])
        try:
            botuse = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.botuse.set(botuse.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["question13"])
        try:
            finalcomments = await self.bot.wait_for("message", timeout=300, check=check)
            await user_data.finalcomments.set(finalcomments.content)
        except asyncio.TimeoutError:
            return await ctx.author.send("You took too long. Try again, please.")
        a = age.content
        b = 2020
        try:
            yearmath = b - int(a)
            total_age = f"{yearmath} years old"
            await user_data.age.set(total_age)
        except Exception:
            return await ctx.author.send(
                "Something fucked up. Make sure you answer only what is asked (Year of Birth usually)"
            )  # TODO: make less hacky
        # else:
        #     return
        user_data.app_check.set(True)
        embed = discord.Embed(color=await ctx.embed_colour(), timestamp=datetime.utcnow())
        embed.set_author(name="New application!", icon_url=ctx.author.avatar_url)
        embed.set_footer(
            text=f"{ctx.author.name}#{ctx.author.discriminator} UserID: {ctx.author.id})"
        )
        embed.title = f"User: {ctx.author.name}#{ctx.author.discriminator} | ID: ({ctx.author.id})"
        embed.add_field(name="Name:", value=f"{ctx.author.mention}\n" + name.content, inline=True)
        embed.add_field(
            name="Year of Birth:", value=age.content + f"\n{yearmath} years old", inline=True,
        )
        embed.add_field(name="Timezone:", value=timezone.content, inline=True)
        # embed.add_field(name="Desired position:", value=position.content, inline=True)
        embed.add_field(name="Active days/week:", value=days.content, inline=True)
        embed.add_field(name="Active hours/day:", value=hours.content, inline=True)
        embed.add_field(name="Used Dank Memer for:", value=botuse.content, inline=True)
        embed.add_field(name="Previous experience:", value=experience.content, inline=False)
        embed.add_field(name="Reason for interest:", value=reasonforinterest.content, inline=False)
        embed.add_field(name="Bot Perks don't work", value=perkslinking.content, inline=False)
        embed.add_field(name="Enable/Disable Commands", value=commandcontrol.content, inline=False)
        embed.add_field(
            name="Unsure what the answer is, what do you do?",
            value=botadvice.content,
            inline=False,
        )
        embed.add_field(
            name="User missing coins, what do?", value=coinsmissing.content, inline=False,
        )
        embed.add_field(name="Final Comments", value=finalcomments.content, inline=False)
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return await ctx.author.send(
                "Your final application was too long to resolve as an embed. Give this another shot, keeping answers a bit shorter."
            )
        except discord.ext.commands.CommandInvokeError:
            return await ctx.author.send(
                "You need to start over but this time when it asks for year of birth, respond only with a 4 digit year i.e `1999`"
            )
        await ctx.author.add_roles(role_add)

        try:
            await ctx.author.send(
                f"Your application has been sent to {ctx.guild.name} Admins! Thanks for your interest!"
            )
        except commands.CommandInvokeError:
            return await ctx.send(
                f"{ctx.author.mention} I sent your app to the admins. Thanks for closing dms early tho rude ass"
            )
        self.antispam[ctx.guild][ctx.author].stamp()

    @checks.mod_or_permissions(manage_roles=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    async def appcheck(self, ctx: commands.Context, user_id: discord.Member):
        """
        Pull an application that was completed by a user
        """
        if not user_id:
            return await ctx.send_help()

        load_data = await self.config.member(user_id).all()
        app_check_user = load_data["app_check"]
        if not app_check_user:
            return await ctx.send("That user hasn't filled out an application here")

        applicant_user = self.bot.get_user(user_id.id)
        embed = discord.Embed(color=await ctx.embed_colour(), timestamp=datetime.utcnow())
        embed.set_author(name="Member Application", icon_url=applicant_user.avatar_url)
        embed.set_footer(
            text=f"{applicant_user.name}#{applicant_user.discriminator} UserID: {applicant_user.id})"
        )
        embed.title = f"User: {applicant_user.name}#{applicant_user.discriminator} | ID: ({applicant_user.id})"
        embed.add_field(name="Name:", value=load_data["name"], inline=True)
        embed.add_field(
            name="Age", value=load_data["age"], inline=True,
        )
        embed.add_field(name="Timezone:", value=load_data["timezone"], inline=True)
        # embed.add_field(name="Desired position:", value=position.content, inline=True)
        embed.add_field(name="Active days/week:", value=load_data["days"], inline=True)
        embed.add_field(name="Active hours/day:", value=load_data["hours"], inline=True)
        embed.add_field(name="Used Dank Memer for:", value=load_data["botuse"], inline=True)
        embed.add_field(name="Previous experience:", value=load_data["experience"], inline=False)
        embed.add_field(
            name="Reason for interest:", value=load_data["reasonforinterest"], inline=False,
        )
        embed.add_field(name="Bot Perks don't work", value=load_data["perkslinking"], inline=False)
        embed.add_field(
            name="Enable/Disable Commands", value=load_data["commandcontrol"], inline=False,
        )
        embed.add_field(
            name="Unsure what the answer is, what do you do?",
            value=load_data["botadvice"],
            inline=False,
        )
        embed.add_field(
            name="User missing coins, what do?", value=load_data["coinsmissing"], inline=False,
        )
        embed.add_field(name="Final Comments", value=load_data["finalcomments"], inline=False)
        await ctx.send(embed=embed)

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def applysetup(self, ctx: commands.Context):
        """Go through the initial setup process."""
        pred = MessagePredicate.yes_or_no(ctx)
        role = MessagePredicate.valid_role(ctx)

        applicant = get(ctx.guild.roles, name="Staff Applicant")
        channel = get(ctx.guild.text_channels, name="applications")

        await ctx.send(
            "This will create required channel and role. Do you wish to continue? (yes/no)"
        )
        try:
            await self.bot.wait_for("message", timeout=30, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        if not pred.result:
            return await ctx.send("Setup cancelled.")
        if not applicant:
            try:
                applicant = await ctx.guild.create_role(
                    name="Staff Applicant", reason="Application cog setup"
                )
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh. Looks like I don't have permissions to manage roles."
                )
        if not channel:
            await ctx.send("Do you want everyone to see the applications channel? (yes/no)")
            try:
                await self.bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            if pred.result:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                }
            else:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                }
            try:
                channel = await ctx.guild.create_text_channel(
                    "staff-applications", overwrites=overwrites, reason="Application cog setup",
                )
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh. Looks like I don't have permissions to manage channels."
                )
        await ctx.send(f"What role can accept or reject applicants?")
        try:
            await self.bot.wait_for("message", timeout=30, check=role)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        accepter = role.result
        await self.config.guild(ctx.guild).applicant_id.set(applicant.id)
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await self.config.guild(ctx.guild).accepter_id.set(accepter.id)
        await ctx.send(
            "You have finished the setup! Please, move your new channel to the category you want it in."
        )

    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def accept(self, ctx: commands.Context, target: discord.Member):
        """Accept a staff applicant.
        <target> can be a mention or an ID."""
        try:
            accepter = get(ctx.guild.roles, id=await self.config.guild(ctx.guild).accepter_id())
        except TypeError:
            accepter = None
        if not accepter:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send("Uh oh, you cannot use this command.")
        else:
            if accepter not in ctx.author.roles:
                return await ctx.send("Uh oh, you cannot use this command.")
        try:
            applicant = get(ctx.guild.roles, id=await self.config.guild(ctx.guild).applicant_id())
        except TypeError:
            applicant = None
        if not applicant:
            applicant = get(ctx.guild.roles, name="Staff Applicant")
            if not applicant:
                return await ctx.send(
                    "Uh oh, the configuration is not correct. Ask the Admins to set it."
                )
        role = MessagePredicate.valid_role(ctx)
        if applicant in target.roles:
            await ctx.send(f"What role do you want to accept {target.name} as?")
            try:
                await self.bot.wait_for("message", timeout=30, check=role)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            role_add = role.result
            try:
                await target.add_roles(role_add)
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh, I cannot give them the role. It might be above all of my roles."
                )
            await target.remove_roles(applicant)
            await ctx.send(f"Accepted {target.mention} as {role_add}.")
            await target.send(f"You have been accepted as {role_add} in {ctx.guild.name}.")
        else:
            await ctx.send(f"Uh oh. Looks like {target.mention} hasn't applied for anything.")

    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def deny(self, ctx: commands.Context, target: discord.Member):
        """Deny a staff applicant.
        <target> can be a mention or an ID"""
        try:
            accepter = get(ctx.guild.roles, id=await self.config.guild(ctx.guild).accepter_id())
        except TypeError:
            accepter = None
        if not accepter:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send("Uh oh, you cannot use this command.")
        else:
            if accepter not in ctx.author.roles:
                return await ctx.send("Uh oh, you cannot use this command.")
        try:
            applicant = get(ctx.guild.roles, id=await self.config.guild(ctx.guild).applicant_id())
        except TypeError:
            applicant = None
        if not applicant:
            applicant = get(ctx.guild.roles, name="Staff Applicant")
            if not applicant:
                return await ctx.send(
                    "Uh oh, the configuration is not correct. Ask the Admins to set it."
                )
        if applicant in target.roles:
            await ctx.send("Would you like to specify a reason? (yes/no)")
            pred = MessagePredicate.yes_or_no(ctx)
            try:
                await self.bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            if pred.result:
                await ctx.send("Please, specify your reason now.")

                def check(m):
                    return m.author == ctx.author

                try:
                    reason = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                await target.send(
                    f"Your application in {ctx.guild.name} has been denied.\n*Reason:* {reason.content}"
                )
            else:
                await target.send(f"Your application in {ctx.guild.name} has been denied.")
            await target.remove_roles(applicant)
            await ctx.send(f"Denied {target.mention}'s application.")
        else:
            await ctx.send(f"Uh oh. Looks like {target.mention} hasn't applied for anything.")
