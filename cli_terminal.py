from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


class InteractiveTerminal(object):
    def __init__(self):
        self.session = PromptSession(history=InMemoryHistory())

    def prompt(self, message):
        return self.session.prompt(message).strip()


terminal = InteractiveTerminal()