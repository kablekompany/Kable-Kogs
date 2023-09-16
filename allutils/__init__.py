from redbot.core.bot import Red

from .main import AllUtils

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)


# majorly source from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py and modified to work with Red
async def setup(bot: Red) -> None:
    cog = AllUtils(bot)
    await bot.add_cog(cog)
