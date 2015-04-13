from pubsub import pub

CURRENT_SCRUM_LISTENERS = {}
SCRUMS = {}

class DuplicateScrumError(Exception):
    pass


class UnknownScrumError(Exception):
    pass


class ScrumMessageListener(object):
    def __init__(self, owner, user):
        self.owner = owner
        self.user = user

    def __call__(self, message):
        SCRUMS.setdefault(self.owner, []).append(
            (self.user, message)
        )


def start(owner, *users):
    if owner in CURRENT_SCRUM_LISTENERS and CURRENT_SCRUM_LISTENERS[owner]:
        raise DuplicateScrumError

    listeners = []
    for user in users:
        listener = ScrumMessageListener(owner, user)
        listeners.append((user, listener))
        pub.subscribe(
            listener,
            user
        )

    CURRENT_SCRUM_LISTENERS[owner] = listeners

def message(user, message):
    pub.sendMessage(user, message=message)

def close(owner):
    if owner not in CURRENT_SCRUM_LISTENERS:
        raise UnknownScrumError
    for topic, listener in CURRENT_SCRUM_LISTENERS[owner]:
        pub.unsubscribe(listener, topic)
    rows = sorted(SCRUMS[owner], key=lambda row: row[0])
    scrum_report = ['<{user}>: {message}'.format(
        user=user,
        message=message
    ) for user, message in rows]

    del SCRUMS[owner]
    del CURRENT_SCRUM_LISTENERS[owner]
    return scrum_report
