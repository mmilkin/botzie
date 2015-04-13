from unittest import TestCase
import mock

import botzie.scrum
from botzie.bot import ScrumBot


class BotTestCase(TestCase):

    def setUp(self):
        botzie.scrum.CURRENT_SCRUM_LISTENERS = {}
        botzie.scrum.SCRUMS = {}
        self.bot = ScrumBot()
        self.bot.nickname = 'scrumbot'
        self.bot.channel = 'user1'

    @mock.patch('botzie.bot.threads')
    def test_send_start_scrum(self, threads):
        self.bot.privmsg('user1!someplace', '#scrum', 'scrumbot: andy, bob lets scrum!')
        threads.deferToThread.assert_called_with(
            self.bot.print_messages,
            'user1',
            ["starting a scrum for set(['bob', 'andy', 'user1']) let the scrum begin."]
        )

    @mock.patch('botzie.bot.threads')
    def test_send_end_scrum_no_scrum(self, threads):
        botzie.scrum.SCRUMS = {'user1': ['user2', 'some message']}
        botzie.scrum.CURRENT_SCRUM_LISTENERS = {'user1': []}
        self.bot.privmsg('user1!someplace', '#scrum', 'scrumbot: end scrum')

        self.bot.msg.assert_called_with('user1', 'No Scrum found for your user')
        threads.deferToThread.assert_called_with(
            self.bot.print_messages,
            'user1',
            ['<user2>: some message']
        )

    @mock.patch('botzie.bot.threads')
    def test_send_end_scrum_no_scrum(self, threads):
        self.bot.msg = mock.Mock(name='send function')
        self.bot.privmsg('user1!someplace', '#scrum', 'scrumbot: end scrum')
        threads.deferToThread.assert_called_with(
            self.bot.print_usage,
            'user1',
        )

    @mock.patch('botzie.bot.threads')
    def test_unknown(self, threads):
        self.bot.privmsg('user1!someplace', '#scrum', 'scrumbot: some command')
        threads.deferToThread.assert_called_with(
            self.bot.print_usage,
            'user1',
        )
