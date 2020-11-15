from .main import CustomApps

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)


def setup(bot):
    cog = CustomApps(bot)
    bot.add_cog(cog)
