from app.domain.models import journal_models
from app.domain.models import footlab_models
from app.domain.commands import ReadJournal
from app.domain.events import journal_events, scraper_events
import yaml
from datetime import datetime, UTC
from logging import Logger


class ScraperError(Exception):
    pass


class NoResultsFromScraper(Exception):
    pass


def read_journal(cmd: ReadJournal, collected_events: list, logger: Logger = None):
    with open(cmd.path) as stream:
        try:
            config_file: dict = yaml.safe_load(stream)
            journal = config_file["journal"]
            tournaments: list[journal_models.Tournament] = []
            for tournament in journal["tournaments"]:
                tournament["name"] = get_enum_competition_name(tournament["name"])
                tournament["type"] = get_enum_competition_type(tournament["type"])
                tournaments.append(journal_models.Tournament(**tournament))

            rounds = {}
            assert isinstance(journal["rounds"], dict)
            for name, round_list in journal["rounds"].items():
                rounds[get_enum_competition_name(name)] = round_list

        except yaml.YAMLError as exc:
            print(exc)
            raise exc
        except Exception as e:
            print(e)
            raise e
        else:
            collected_events.append(
                journal_events.JournalRetrieved(
                    journal=journal_models.Journal(
                        tournaments=tournaments, rounds=rounds
                    )
                )
            )


# translate the journal into commands
def process_journal(
    evt: journal_events.JournalRetrieved,
    base_api_url: str,
    collected_events: list,
    logger: Logger = None,
):
    # Check the next available timestamp to know if we need to start scraping
    now_utc = datetime.now(UTC).timestamp()
    for tournament in evt.journal.tournaments:
        if tournament.next_available_utc_timestamp <= now_utc:
            # Create a GAME scraping event
            collected_events.append(
                scraper_events.ScrapeRequestReceived(
                    url=get_game_url(base_api_url, tournament, evt.journal.rounds),
                    season=tournament.season_human,
                    category=footlab_models.FootlabCategory.GAMES,
                )
            )
    return


def get_game_url(
    base_api_url: str, tournament: journal_models.Tournament, rounds: dict
):
    return f"{base_api_url}/unique-tournament/{tournament.id}/season/{tournament.season_id}/events/round/{get_round_endpoint(tournament, rounds)}"


def get_enum_competition_name(name: str):
    try:
        return journal_models.TournamentNameEnum(name)
    except ValueError:
        return None


def get_enum_competition_type(type: str):
    try:
        return journal_models.TournamentTypeEnum(type)
    except ValueError:
        return None


def get_round_endpoint(tournament: journal_models.Tournament, rounds: dict):
    if tournament.type == journal_models.TournamentTypeEnum.NATIONAL_LEAGUE:
        return tournament.start_round

    rounds_list = rounds.get(tournament.name)
    return rounds_list[tournament.start_round]
