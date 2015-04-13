import yaml

from twisted.application.service import IServiceMaker, Service
from twisted.internet.endpoints import clientFromString
from twisted.plugin import IPlugin
from twisted.python import usage, log
from zope.interface import implementer
from botzie.bot import IRCConnectionFactory


class Options(usage.Options):
    optParameters = [
        ['config', 'c', 'config.yaml', 'Configuration file.'],
    ]


class IRCBotService(Service):
    _bot = None

    def __init__(self, config):
        self.config = config

    def startService(self):
        """Construct a client & connect to server."""
        from twisted.internet import reactor

        def connected(bot):
            self._bot = bot

        def failure(err):
            log.err(err, _why='Could not connect to specified server.')
            reactor.stop()

        client = clientFromString(reactor, self.config.con)
        factory = IRCConnectionFactory(self.config)

        return client.connect(factory).addCallbacks(connected, failure)

    def stopService(self):
        """Disconnect."""
        if self._bot and self._bot.transport.connected:
            self._bot.transport.loseConnection()


@implementer(IServiceMaker, IPlugin)
class BotServiceMaker(object):
    tapname = 'botzie'
    description = 'IRC bot that provides scrum logging'
    options = Options

    def makeService(self, options):
        """Construct the talkbackbot service."""
        config = yaml.load(open(options['config'], 'r'))
        return IRCBotService(config['irc_connection'])


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = BotServiceMaker()
