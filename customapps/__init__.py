from .main import CustomApps


def setup(bot):
    cog = CustomApps(bot)
    bot.add_cog(cog)
