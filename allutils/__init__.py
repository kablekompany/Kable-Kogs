from .main import AllUtils

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)


# majorly source from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py and modified to work with Red
def setup(bot):
    bot.add_cog(AllUtils(bot))
