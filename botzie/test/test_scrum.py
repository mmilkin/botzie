from unittest import TestCase
from botzie.scrum import DuplicateScrumError, UnknownScrumError, start, message, close
import botzie.scrum


class ScrumManagerTestCase(TestCase):

    def setUp(self):
        botzie.scrum.CURRENT_SCRUM_LISTENERS = {}
        botzie.scrum.SCRUMS = {}

    def test_run_scrum(self):
        start('myuser', *['user1', 'user2'])

        message('user1', u'user2, Hi Buddy')
        message('user2', u'user1, Im not your Buddy, Hi Pall')
        message('user1', u'user2, Im not your Pall, Friend')
        message('user2', u'user1, Im not your Friend, Buddy')
        messages = close('myuser')

        self.assertEqual(
            messages[0],
            u'<user1>: user2, Hi Buddy'
        )

        self.assertEqual(
            messages[1],
            u'<user1>: user2, Im not your Pall, Friend'
        )
        self.assertEqual(
            messages[2],
            u'<user2>: user1, Im not your Buddy, Hi Pall'
        )
        self.assertEqual(
            messages[3],
            u'<user2>: user1, Im not your Friend, Buddy'
        )

    def test_double_start(self):
        start('myuser', *['user1', 'user2'])

        with self.assertRaises(DuplicateScrumError):
            start('myuser', *['user3', 'user4'])

    def test_close(self):
        with self.assertRaises(UnknownScrumError):
            close('user1')

    def test_send_message_no_op(self):
        message('user1', u'user2, Hi Buddy')
