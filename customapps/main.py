import asyncio
import datetime as dt  # lgtm [py/import-and-import-from]

# silencing this flag will rework at final
import logging
from datetime import datetime, timedelta
from typing import Any, Literal

import discord
from discord.utils import get
from redbot.core import Config, checks, commands
from redbot.core.utils.antispam import AntiSpam
from redbot.core.utils.predicates import MessagePredicate

Cog: Any = getattr(commands, "Cog", object)

log = logging.getLogger("red.kablekogs.customapps")


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
    "answer8": [],
    "answer9": [],
    "answer10": [],
    "answer11": [],
    "answer12": [],
    "finalcomments": [],
    "raw_app": {},
}

guild_defaults = {
    "app_questions": {
        "name": "What name do you prefer to be called?",
        "timezone": "What timezone are you located in? (Use google if you don't know)",
        "age": "What year were you born? RESPOND ONLY THE 4 DIGIT YEAR",
        "days": "What days can you be active in the server?",
        "hours": "How many hours per day can you be active?",
        "experience": "Do you have any previous experience? If so, please describe.",
        "reasonforinterest": "Why do you want to be a member of our staff?",
        "question8": None,
        "question9": None,
        "question10": None,
        "question11": None,
        "question12": None,
        "finalcomments": "Do you have any final comments for the admins?",
    },
    "applicant_id": None,
    "accepter_id": None,
    "channel_id": None,
    "positions_available": None,
}  # for the sake of saving time for now. add agnostic before merge
# TODO-

# Originally from https://github.com/elijabesu/SauriCogs
class CustomApps(Cog):
    """Customize Staff apps for your server"""

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int):
        # pylint: disable=E1120
        await self.config.member_from_ids(user_id).clear()

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=73837383738,
            force_registration=True,
        )
        self.config.register_member(**default)
        self.config.register_guild(**guild_defaults)
        self.antispam = {}
        self.spam_control = commands.CooldownMapping.from_cooldown(
            1, 300, commands.BucketType.user
        )

    async def save_application(self, embed: discord.Embed, applicant: discord.Member):
        e = embed
        await self.config.member(applicant).raw_app.set(e.to_dict())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not isinstance(error, commands.MaxConcurrencyReached):
            return  # don't care about other errors

        bucket = self.spam_control.get_bucket(ctx.message)
        current = ctx.message.created_at.replace(tzinfo=dt.timezone.utc).timestamp()
        retry_after = bucket.update_rate_limit(current)
        author_id = ctx.message.author.id
        if retry_after and author_id != self.bot.owner_ids:
            return  # don't care about users spamming the shit

        await ctx.send(
            f"{ctx.author.mention} this command is at it's max allowed processing queue.",
            delete_after=20,
        )
        # insight

    @commands.command(cooldown_after_parsing=True)
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True, manage_channels=True, manage_webhooks=True)
    @commands.max_concurrency(10, per=commands.BucketType.guild, wait=False)
    async def apply(self, ctx: commands.Context):
        """Apply to be a staff member."""
        role_add = get(ctx.guild.roles, name="Staff Applicant")
        app_data = await self.config.guild(ctx.guild).app_questions.all()
        user_data = self.config.member(ctx.author)

        channel = get(ctx.guild.text_channels, name="staff-applications")
        if ctx.guild not in self.antispam:
            self.antispam[ctx.guild] = {}
        if ctx.author not in self.antispam[ctx.guild]:
            self.antispam[ctx.guild][ctx.author] = AntiSpam([(timedelta(days=2), 1)])
        if self.antispam[ctx.guild][ctx.author].spammy:
            return await ctx.send(
                f"{ctx.author.mention} uh you're doing this way too frequently, and we don't need more than one application from you. Don't call us, we will maybe call you...LOL",
                delete_after=10,
            )
        if role_add is None:
            return await ctx.send("Uh oh. Looks like your Admins haven't added the required role.")
        if role_add.position > ctx.guild.me.top_role.position:
            return await ctx.send(
                "The staff applicant role is above me, and I need it below me if I am to assign it on completion. Tell your admins"
            )

        if channel is None:
            return await ctx.send(
                "Uh oh. Looks like your Admins haven't added the required channel."
            )
        available_positions = await self.config.guild(ctx.guild).positions_available()
        if available_positions is None:
            fill_this = "Reply with the position you are applying for to continue."
        else:
            list_positions = "\n".join(available_positions)
            fill_this = "Reply with the desired position from this list to continue\n`{}`".format(
                list_positions
            )
        try:
            await ctx.author.send(
                f"Let's do this! You have maximum of __5 minutes__ for each question.\n{fill_this}\n\n*To cancel at anytime respond with `cancel`*\n\n*DISCLAIMER: Your responses are stored for proper function of this feature*"
            )
        except discord.Forbidden:
            return await ctx.send(
                f"{ctx.author.mention} I can't DM you. Do you have them closed?", delete_after=10
            )
        await ctx.send(f"Okay, {ctx.author.mention}, I've sent you a DM.", delete_after=7)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        try:
            position = await self.bot.wait_for("message", timeout=300, check=check)
            if position.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.position.set(position.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["name"])
        try:
            name = await self.bot.wait_for("message", timeout=300, check=check)
            if name.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.name.set(name.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["timezone"])
        try:
            timezone = await self.bot.wait_for("message", timeout=300, check=check)
            if timezone.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.timezone.set(timezone.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["age"])
        try:
            age = await self.bot.wait_for("message", timeout=300, check=check)
            if age.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            a = age.content
            b = str(datetime.today())
            c = b[:4]
            d = int(c)
            try:
                e = int(a)
                yearmath = d - e
                total_age = f"YOB: {a}\n{yearmath} years old"
            except Exception:
                total_age = f"Recorded response of `{a}`. Could not calculate age."

            await user_data.age.set(total_age)

        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return

        await ctx.author.send(app_data["days"])
        try:
            days = await self.bot.wait_for("message", timeout=300, check=check)
            if days.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.days.set(days.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["hours"])
        try:
            hours = await self.bot.wait_for("message", timeout=300, check=check)
            if hours.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.hours.set(hours.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["experience"])
        try:
            experience = await self.bot.wait_for("message", timeout=300, check=check)
            if experience.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.experience.set(experience.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        await ctx.author.send(app_data["reasonforinterest"])
        try:
            reasonforinterest = await self.bot.wait_for("message", timeout=300, check=check)
            if reasonforinterest.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.reasonforinterest.set(reasonforinterest.content)
        except asyncio.TimeoutError:
            try:
                await ctx.author.send("You took too long. Try again, please.")
            except discord.HTTPException:
                return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
            return
        check_8 = app_data["question8"]
        if check_8 is not None:
            await ctx.author.send(app_data["question8"])
            try:
                answer8 = await self.bot.wait_for("message", timeout=300, check=check)
                if answer8.content.lower() == "cancel":
                    return await ctx.author.send("Application has been canceled.")
                await user_data.answer8.set(answer8.content)
            except asyncio.TimeoutError:
                try:
                    await ctx.author.send("You took too long. Try again, please.")
                except discord.HTTPException:
                    return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
                return
        check_9 = app_data["question9"]
        if check_9 is not None:
            await ctx.author.send(app_data["question9"])
            try:
                answer9 = await self.bot.wait_for("message", timeout=300, check=check)
                if answer9.content.lower() == "cancel":
                    return await ctx.author.send("Application has been canceled.")
                await user_data.answer9.set(answer9.content)
            except asyncio.TimeoutError:
                try:
                    await ctx.author.send("You took too long. Try again, please.")
                except discord.HTTPException:
                    return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
                return
        check_10 = app_data["question10"]
        if check_10 is not None:
            await ctx.author.send(app_data["question10"])
            try:
                answer10 = await self.bot.wait_for("message", timeout=300, check=check)
                if answer10.content.lower() == "cancel":
                    return await ctx.author.send("Application has been canceled.")
                await user_data.answer10.set(answer10.content)
            except asyncio.TimeoutError:
                try:
                    await ctx.author.send("You took too long. Try again, please.")
                except discord.HTTPException:
                    return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
                return
        check_11 = app_data["question11"]
        if check_11 is not None:
            await ctx.author.send(app_data["question11"])
            try:
                answer11 = await self.bot.wait_for("message", timeout=300, check=check)
                if answer11.content.lower() == "cancel":
                    return await ctx.author.send("Application has been canceled.")
                await user_data.answer11.set(answer11.content)
            except asyncio.TimeoutError:
                try:
                    await ctx.author.send("You took too long. Try again, please.")
                except discord.HTTPException:
                    return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
                return
        check_12 = app_data["question12"]
        if check_12 is not None:
            await ctx.author.send(app_data["question12"])
            try:
                answer12 = await self.bot.wait_for("message", timeout=300, check=check)
                if answer12.content.lower() == "cancel":
                    return await ctx.author.send("Application has been canceled.")
                await user_data.answer12.set(answer12.content)
            except asyncio.TimeoutError:
                try:
                    await ctx.author.send("You took too long. Try again, please.")
                except discord.HTTPException:
                    return await ctx.send(f"Thanks for nothing, {ctx.author.mention}")
                return

        await ctx.author.send(app_data["finalcomments"])
        try:
            finalcomments = await self.bot.wait_for("message", timeout=300, check=check)
            if finalcomments.content.lower() == "cancel":
                return await ctx.author.send("Application has been canceled.")
            await user_data.finalcomments.set(finalcomments.content)
        except asyncio.TimeoutError:
            return await ctx.author.send("You took too long. Try again, please.")

        embed = discord.Embed(color=await ctx.embed_colour(), timestamp=datetime.utcnow())
        embed.set_author(
            name=f"Applicant: {ctx.author.name} | ID: {ctx.author.id}",
            icon_url=ctx.author.avatar_url,
        )
        embed.set_footer(
            text=f"{ctx.author.name}#{ctx.author.discriminator} UserID: {ctx.author.id}"
        )
        embed.title = f"Application for {position.content}"
        embed.add_field(
            name="Applicant Name:",
            value=f"Mention: {ctx.author.mention}\nPreferred: " + name.content,
            inline=True,
        )
        embed.add_field(
            name="Age",
            value=total_age,
            inline=True,
        )
        embed.add_field(name="Timezone:", value=timezone.content, inline=True)
        embed.add_field(name="Desired position:", value=position.content, inline=True)
        embed.add_field(name="Active days/week:", value=days.content, inline=True)
        embed.add_field(name="Active hours/day:", value=hours.content, inline=True)
        embed.add_field(
            name="{}...".format(app_data["reasonforinterest"][:197]).replace("$", "\\$"),
            value=reasonforinterest.content,
            inline=False,
        )
        embed.add_field(name="Previous experience:", value=experience.content, inline=False)

        if check_8 is not None:
            embed.add_field(
                name="{}...".format(app_data["question8"][:197]).replace("$", "\\$"),
                value=answer8.content,
                inline=False,
            )
        if check_9 is not None:
            embed.add_field(
                name="{}...".format(app_data["question9"][:197]).replace("$", "\\$"),
                value=answer9.content,
                inline=False,
            )
        if check_10 is not None:
            embed.add_field(
                name="{}...".format(app_data["question10"][:197]).replace("$", "\\$"),
                value=answer10.content,
                inline=False,
            )
        if check_11 is not None:
            embed.add_field(
                name="{}...".format(app_data["question11"][:197]).replace("$", "\\$"),
                value=answer11.content,
                inline=False,
            )
        if check_12 is not None:
            embed.add_field(
                name="{}...".format(app_data["question12"][:197]).replace("$", "\\$"),
                value=answer12.content,
                inline=False,
            )
        embed.add_field(name="Final Comments", value=finalcomments.content, inline=False)
        try:
            webhook = None
            for hook in await channel.webhooks():
                if hook.name == ctx.guild.me.name:
                    webhook = hook
            if webhook is None:
                webhook = await channel.create_webhook(name=ctx.guild.me.name)

            await webhook.send(
                embed=embed, username=ctx.guild.me.display_name, avatar_url=ctx.guild.me.avatar_url
            )
        except Exception as e:
            log.info(f"{e} occurred in {ctx.author.name} | {ctx.author.id} application")
            try:
                return await ctx.author.send(
                    "Seems your responses were too verbose. Let's try again, but without the life stories."
                )
            except Exception:
                return
        # except discord.HTTPException:
        #     return await ctx.author.send(
        #         "Your final application was too long to resolve as an embed. Give this another shot, keeping answers a bit shorter."
        #     )
        # except commands.CommandInvokeError:
        #     return await ctx.author.send(
        #         "You need to start over but this time when it asks for year of birth, respond only with a 4 digit year i.e `1999`"
        #     )
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
        # lets save the embed instead of calling on it again
        await self.save_application(embed=embed, applicant=ctx.author)

        await self.config.member(ctx.author).app_check.set(True)

    @checks.admin_or_permissions(manage_guild=True)
    @commands.group(name="appq", aliases=["appquestions"])
    @commands.guild_only()
    async def app_questions(self, ctx: commands.Context):
        """Set/see the custom questions for the applications in your server"""
        app_questions = await self.config.guild(ctx.guild).app_questions.get_raw()
        question_1 = app_questions["name"]
        question_2 = app_questions["timezone"]
        question_3 = app_questions["age"]
        question_4 = app_questions["days"]
        question_5 = app_questions["hours"]
        question_6 = app_questions["experience"]
        question_7 = app_questions["reasonforinterest"]
        question_8 = app_questions["question8"]
        question_9 = app_questions["question9"]
        question_10 = app_questions["question10"]
        question_11 = app_questions["question11"]
        question_12 = app_questions["question12"]
        question_13 = app_questions["finalcomments"]

        await ctx.send(
            "There are 13 questions in this application feature, with a few preloaded already for you.\nHere is the current configuration:"
        )
        e = discord.Embed(colour=await ctx.embed_colour())
        e.add_field(
            name="Question 1", value=f"{question_1}" if question_1 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 2", value=f"{question_2}" if question_2 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 3", value=f"{question_3}" if question_3 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 4", value=f"{question_4}" if question_4 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 5", value=f"{question_5}" if question_5 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 6", value=f"{question_6}" if question_6 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 7", value=f"{question_7}" if question_7 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 8", value=f"{question_8}" if question_8 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 9", value=f"{question_9}" if question_9 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 10", value=f"{question_10}" if question_10 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 11", value=f"{question_11}" if question_11 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 12", value=f"{question_12}" if question_12 else "Not Set", inline=False
        )
        e.add_field(
            name="Question 13", value=f"{question_13}" if question_13 else "Not Set", inline=False
        )
        await ctx.send(embed=e)

    @app_questions.command(name="set")
    async def set_questions(self, ctx: commands.Context):
        """Set up custom questions for your server"""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(
            "Let's set up those questions we've not pre-filled:\nYou will be setting questions 8-12. You can view the preloaded questions by passing `{}appq`. To begin, reply with `admin abuse` *spelled exact*".format(
                ctx.prefix
            )
        )
        try:
            confirmation = await ctx.bot.wait_for("message", check=check, timeout=20)
            if confirmation.content.lower() != "admin abuse":
                return await ctx.send("Alright, let's do these later then")
        except asyncio.TimeoutError:
            return await ctx.send(
                "Took to long to respond, gotta be smarter than the users you're hiring for sure."
            )

        app_questions = await self.config.guild(ctx.guild).app_questions.get_raw()
        question_8 = app_questions["question8"]
        question_9 = app_questions["question9"]
        question_10 = app_questions["question10"]
        question_11 = app_questions["question11"]
        question_12 = app_questions["question12"]
        await ctx.send(
            "Alright, let's start with question 8: You have 5min to decide and respond with question you'd like, or respond with cancel to do this later"
        )

        if question_8 is not None:
            await ctx.send(
                f"Looks like question 8 is currently `{question_8}`:\n Do you want to change this? Type `no` to skip or the question you wish to change to if you want to change."
            )
            try:
                submit_8 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_8.content.lower() != "no":
                    if len(submit_8.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question8.set(
                        submit_8.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )

        if question_8 is None:
            try:
                submit_8 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_8.content.lower() != "cancel":
                    if len(submit_8.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question8.set(
                        submit_8.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 9: Please respond with your next app question")

        if question_9 is not None:
            await ctx.send(
                f"Looks like question 9 is currently `{question_9}`:\n Do you want to change this? Type `no` to skip or the question you wish to change to if you want to change."
            )
            try:
                submit_9 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_9.content.lower() != "no":
                    if len(submit_9.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question9.set(
                        submit_9.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 10: Please respond with your next app question")

        if question_9 is None:
            try:
                submit_9 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_9.content.lower() != "cancel":
                    if len(submit_9.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question9.set(
                        submit_9.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 10: Please respond with your next app question")

        if question_10 is not None:
            await ctx.send(
                f"Looks like question 10 is currently `{question_10}`:\n Do you want to change this? Type `no` to skip or the question you wish to change to if you want to change."
            )
            try:
                submit_10 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_10.content.lower() != "no":
                    if len(submit_10.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question10.set(
                        submit_10.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 11: Please respond with your next app question")

        if question_10 is None:
            try:
                submit_10 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_10.content.lower() != "cancel":
                    if len(submit_10.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question10.set(
                        submit_10.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 11: Please respond with your next app question")

        if question_11 is not None:
            await ctx.send(
                f"Looks like question 11 is currently `{question_11}`:\n Do you want to change this? Type `no` to skip or the question you wish to change to if you want to change."
            )
            try:
                submit_11 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_11.content.lower() != "no":
                    if len(submit_11.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question11.set(
                        submit_11.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 12: Please respond with your next app question")

        if question_11 is None:
            try:
                submit_11 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_11.content.lower() != "cancel":
                    if len(submit_11.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question11.set(
                        submit_11.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )
            await ctx.send("Moving to question 12: Please respond with your next app question")

        if question_12 is not None:
            await ctx.send(
                f"Looks like question 12 is currently `{question_12}`:\n Do you want to change this? Type `no` to skip or the question you wish to change to if you want to change."
            )
            try:
                submit_12 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_12.content.lower() != "no":
                    if len(submit_12.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question12.set(
                        submit_12.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )

        if question_12 is None:
            try:
                submit_12 = await ctx.bot.wait_for("message", check=check, timeout=300)
                if submit_12.content.lower() != "cancel":
                    if len(submit_12.content) > 750:
                        return await ctx.send(
                            "Talkitive are we? Too many characters to fit in final embed, shorten the question some"
                        )
                    await self.config.guild(ctx.guild).app_questions.question12.set(
                        submit_12.content
                    )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Took too long bud. Let's be coherent for this and try again."
                )

        await ctx.send(
            "That's all the questions and your apps are set *maybe, if you answered, anyway*. Check this with `{}appq`".format(
                ctx.prefix
            )
        )

    @checks.mod_or_permissions(manage_roles=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    async def appcheck(self, ctx: commands.Context, user_id: discord.Member):
        """
        *Not Functioning*
        Pull an application that was completed by a user
        """
        return await ctx.send(
            "This command is currently being reworked, follow updates in The Kompound"
        )

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def applysetup(self, ctx: commands.Context):
        """Go through the initial setup process."""
        pred = MessagePredicate.yes_or_no(ctx)
        role = MessagePredicate.valid_role(ctx)

        applicant = get(ctx.guild.roles, name="Staff Applicant")
        channel = get(ctx.guild.text_channels, name="staff-applications")

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
                    "staff-applications",
                    overwrites=overwrites,
                    reason="Application cog setup",
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
        if (
            not accepter
            and not ctx.author.guild_permissions.administrator
            or accepter
            and accepter not in ctx.author.roles
        ):
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

    @app_questions.command(name="reset")
    async def clear_config(self, ctx: commands.Context):
        """
        Fully resets server configuation to default, and clears all custom app questions
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(
            "Are you certain about this? This will wipe all settings/custom questions in your server's configuration\nType: `RESET THIS GUILD` to continue (must be typed exact)"
        )
        try:
            confirm_reset = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_reset.content != "RESET THIS GUILD":
                return await ctx.send("Okay, not resetting today")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply")
        await self.config.guild(ctx.guild).app_questions.clear_raw()
        await ctx.send("Guild Reset, goodluck")
