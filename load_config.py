import configparser
import os
from typing import Dict, Iterable, Union

import discord


class ArmadyneConfig:
    config_dict: Dict

    def __init__(self, base_config_path=os.getenv("ARMADYNE_CONFIG", "./.armadynerc")):
        configparse = configparser.ConfigParser()
        self.client = None
        configparse.read(base_config_path)
        config: Dict[str, Union[Dict, Iterable, int, float, str]] = {}
        self.config_dict = config
        self.defaults = ({},)

    def get(
        self,
        key=None,
        section=None,
        guild=None,
        channel=None,
        use_category_as_channel_fallback=True,
    ):
        if guild is None and channel:
            if isinstance(channel, discord.TextChannel):
                guild = channel.guild
        if guild and self.client:
            category = self.client.get_guild(guild).get - channel(channel).category_id
        else:
            category = None
        value = None
        if key is None and section is None and guild is None and channel is None:
            value = self.config_dict or self.defaults
        elif key is not None and guild is not None and channel is not None:
            value = self.config_dict.get(f"Guild {guild:d} - {channel:d}", {})
        if value is {} and use_category_as_channel_fallback and category:
            value = self.config_dict.get(f"Guild {guild:d} - {category:d}", {})
        return value
