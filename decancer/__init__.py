# from .dehoister import Decancer
from .decancer import Decancer

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)


def setup(bot):
    bot.add_cog(Decancer(bot))
