# TODO: Wellfound (AngelList) has no stable public API and actively blocks
# scraping. Implement later with an authenticated session (e.g. Playwright
# + stored cookies), or drop it if the ToS risk isn't worth it.

NAME = "wellfound"


class WellfoundFetcher:
    name = NAME

    def fetch(self) -> list[dict]:
        return []
