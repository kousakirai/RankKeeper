from discord.ext import commands
import traceback
import discord
from logging import getLogger
import wavelink
import os


LOG = getLogger(__name__)


class RKCore(commands.Bot):
    def __init__(self, token, prefix, intents):
        super().__init__(command_prefix=prefix, intents=intents)
        self.token = token
        self.invites = None
        self.log_channel = self.get_channel(829866679949328444)\

    async def setup_hook(self):
        nodes = [wavelink.Node(uri='http://lavalink:2333', password=os.environ.get('LAVALINK_SERVER_PASSWORD'))]
        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)
        await self._load_cogs()
        await self.tree.sync()
        self.tree.copy_global_to(guild=discord.Object(811206817942208514))
        LOG.info("CommandTree Setup Complete.")

    async def _load_cogs(self):
        EXTENSIONS = ['cogs.music', 'cogs.shuffle', 'cogs.dev', 'cogs.bump']
        for extension in EXTENSIONS:
            try:
                await self.load_extension("rank_keeper." + extension)
            except Exception as e:
                traceback.print_exc()
                LOG.error(f"Failed to load extension {extension}")
                LOG.error(f"Error: {e}")
            else:
                LOG.info(f"Successfully loaded extension {extension}")
        await self.load_extension("jishaku")
        LOG.info("All cogs were loaded.")

    async def on_ready(self):
        self.invites = self.get_guild(811206817942208514).invites
        LOG.info(f"Logged in as {self.user}")
        LOG.info(f"Guilds: {len(self.guilds)}")
        LOG.info(f"Users: {len(self.users)}")
        LOG.info(f"discord.py version: {discord.__version__}")

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        LOG.info("Wavelink Node connected: %r | Resumed: %s", payload.node, payload.resumed)

    async def run(self):
        try:
            await self.start(self.token)
        except KeyboardInterrupt:
            LOG.info("Shutdown...")
            await self.close()

        except discord.LoginFailure:
            LOG.error("BOT_TOKEN is invalid.")

        else:
            traceback.print_exc()
