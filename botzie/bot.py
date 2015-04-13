from twisted.internet import protocol, threads
from twisted.python import log
from twisted.words.protocols import irc

from botzie.scrum import start as start_scrum, message as send_message, close as close_scrum, UnknownScrumError


class ConnectionConfig(object):

    def __init__(self, con, channel, nic, name, password):
        self.con = con
        self.nic = nic
        self.channel = channel
        self.name = name
        self.password = password


class ScrumBot(object, irc.IRCClient):

    def connectionMade(self):
        """Called when a connection is made."""
        self.nickname = self.factory.nickname
        self.name = self.factory.name
        self.channel = self.factory.channel
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        log.msg("connectionMade")

    def signedOn(self):
        """Called when bot has successfully signed on to server."""
        if self.nickname != self.factory.nickname:
            log.msg('Your nickname was already occupied, actual nickname is '
                    '"{}".'.format(self.nickname))
        self.join(self.factory.channel)

    def joined(self, channel):
        """Called when the bot joins the channel."""
        log.msg("[{nick} has joined {channel}]"
                .format(nick=self.nickname, channel=self.factory.channel,))

    def privmsg(self, user, channel, message):
        """Called when the bot receives a message."""
        user_name = user.split('!', 1)[0]
        log.msg("inbound message [{}]-[{}] ".format(message, self.nickname + ':'))

        if message.startswith(self.nickname + ':'):
            if message.lower().endswith('lets scrum!'):
                self.start_scrum_message(user_name, message[9:-11])
            elif message.lower().endswith('end scrum'):
                log.msg('Ending Scrum')
                self.end_scrum_message(user_name)
            else:
                threads.deferToThread(self.print_usage, user_name)
        else:
            send_message(user_name, message)

    def start_scrum_message(self, user, message):
        message = message.replace(',', ' ')
        names = message.split()
        names.append(user)
        names = set(names)
        start_scrum(user, *list(names))
        threads.deferToThread(self.print_messages, self.channel, [
            'starting a scrum for {names} let the scrum begin.'.format(
                names=names)
        ])

    def end_scrum_message(self, user):
        log.msg('Ending Scrum')
        try:
            messages = close_scrum(user)
        except UnknownScrumError:
            self.msg(user, 'No Scrum found for your user')
            threads.deferToThread(self.print_usage, user)
        else:
            threads.deferToThread(self.print_messages, user, messages)

    def print_messages(self, chan, messages):
        for message in messages:
            self.msg(chan, message)

    def print_usage(self, user):
        self.msg(user, 'Usage: starting a scrum, ending a scrum')
        self.msg(
            user,
            'starting a scrum "{bot_name}: nick1 nick2 nick3, nick4 start scrum!"'.format(
                bot_name=self.nickname)
        )
        self.msg(
            user,
            'ending a scrum "{bot_name}: end scrum"'.format(
                bot_name=self.nickname)
        )


class IRCConnectionFactory(protocol.ClientFactory):
    protocol = ScrumBot

    def __init__(self, conf):
        self.conf = conf

    @property
    def nickname(self):
        return self.conf.nic

    @property
    def name(self):
        return self.conf.name

    @property
    def channel(self):
        return self.conf.channel

    @property
    def password(self):
        return self.conf.password
