import yaml
from app.scraper.domain.model import (
    Journal,
    Tournament,
    TournamentNameEnum,
    TournamentTypeEnum,
)
from app.scraper.domain.events import ScrapeRequestReceived
from datetime import datetime, UTC
from app.scraper.domain.model import ScraperCategory
from app.scraper.bootstrap import BASE_API
import app.scraper.bootstrap as bootstrap
from app.scraper.service_layer.messagebus import MessageBus

# Read the journal and get the latest game to scrape
JOURNAL_PATH = "app/journal.yml"


def get_enum_competition_name(name: str):
    try:
        return TournamentNameEnum(name)
    except ValueError:
        return None


def get_enum_competition_type(type: str):
    try:
        return TournamentTypeEnum(type)
    except ValueError:
        return None


def get_journal() -> Journal:
    with open(JOURNAL_PATH) as stream:
        try:
            config_file: dict = yaml.safe_load(stream)
            journal = config_file["journal"]
            tournaments: list[Tournament] = []
            for tournament in journal["tournaments"]:
                tournament["name"] = get_enum_competition_name(tournament["name"])
                tournament["type"] = get_enum_competition_type(tournament["type"])
                tournaments.append(Tournament(**tournament))

            rounds = {}
            assert isinstance(journal["rounds"], dict)
            for name, round_list in journal["rounds"].items():
                rounds[get_enum_competition_name(name)] = round_list

        except yaml.YAMLError as exc:
            print(exc)
        except Exception as e:
            print(e)
            raise e
        else:
            return Journal(tournaments=tournaments, rounds=rounds)


def get_round_endpoint(tournament: Tournament, rounds: dict):
    if tournament.type == TournamentTypeEnum.NATIONAL_LEAGUE:
        return tournament.start_round

    rounds_list = rounds.get(tournament.name)
    return rounds_list[tournament.start_round]


def get_complete_endpoint(tournament: Tournament, rounds: dict):
    # https://www.sofascore.com/api/v1/unique-tournament/23/season/76457/events/round/29
    return f"{BASE_API}/unique-tournament/{tournament.id}/season/{tournament.season_id}/events/round/{get_round_endpoint(tournament, rounds)}"


# translate the journal into commands
def generate_events(journal: Journal):
    # Check the next available timestamp to know if we need to start scraping
    now_utc = datetime.now(UTC).timestamp()
    commands_list = []
    for tournament in journal.tournaments:
        if tournament.next_available_utc_timestamp <= now_utc:
            # Create a GAME scraping event
            round_endpoint: str = get_complete_endpoint(tournament, journal.rounds)
            commands_list.append(
                ScrapeRequestReceived(
                    url=round_endpoint,
                    season=tournament.season_human,
                    category=ScraperCategory.GAMES,
                )
            )

    return commands_list


if __name__ == "__main__":
    bus: MessageBus = bootstrap.bootstrap()
    journal = get_journal()
    events = generate_events(journal)
    for evt in events:
        bus.handle(evt)
