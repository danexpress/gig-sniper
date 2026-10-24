from .remoteok import RemoteOKFetcher
from .weworkremotely import WeWorkRemotelyFetcher
from .wellfound import WellfoundFetcher

REGISTRY = {
    "remoteok": RemoteOKFetcher,
    "weworkremotely": WeWorkRemotelyFetcher,
    "wellfound": WellfoundFetcher,
}


def get_enabled_fetchers(enabled_names: list[str]) -> list:
    return [REGISTRY[name]() for name in enabled_names if name in REGISTRY]
