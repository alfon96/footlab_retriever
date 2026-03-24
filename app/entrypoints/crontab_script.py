import app.domain.commands as commands
import app.bootstrap as bootstrap
from app.service_layer.messagebus import MessageBus


bus: MessageBus = bootstrap.bootstrap()


def send_read_journal_cmd():
    cmd = commands.ReadJournal(path=bus.journal_path)
    bus.handle(cmd)


if __name__ == "__main__":
    send_read_journal_cmd()
