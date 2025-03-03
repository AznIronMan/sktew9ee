class PictureDirectories:
    BANNER_FOLDER: str = "Banners"
    BROADCASTER_FOLDER: str = "Broadcasters"
    DEFAULTS_FOLDER: str = "Defaults"
    EVENTS_FOLDER: str = "Events"
    LOGO_BACKS_FOLDER: str = "Logo_Backdrops"
    LOGOS_FOLDER: str = "Logos"
    NARRATIVES_FOLDER: str = "Random"
    STABLE_BACKS_FOLDER: str = "Stable_Backdrops"
    STABLES_FOLDER: str = "Stables"
    TITLES_FOLDER: str = "Belts"
    TV_FOLDER: str = "TV"
    WORKER_FOLDER: str = "People"

    @classmethod
    def get_all_folders(cls) -> list[str]:
        return [
            cls.BANNER_FOLDER,
            cls.BROADCASTER_FOLDER,
            cls.DEFAULTS_FOLDER,
            cls.EVENTS_FOLDER,
            cls.LOGO_BACKS_FOLDER,
            cls.LOGOS_FOLDER,
            cls.NARRATIVES_FOLDER,
            cls.STABLE_BACKS_FOLDER,
            cls.STABLES_FOLDER,
            cls.TITLES_FOLDER,
            cls.TV_FOLDER,
            cls.WORKER_FOLDER,
        ]


__all__ = ["PictureDirectories"]
