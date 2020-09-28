from .main import Application


def setup(bot):
    cog = Application(bot)
    bot.add_cog(cog)
