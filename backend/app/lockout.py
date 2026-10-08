from datetime import timedelta


def parse_tiers(raw: str) -> list[tuple[int, int]]:
    """'3:3,5:10' -> [(3, 3), (5, 10)] als (Fehlversuche, Minuten), aufsteigend."""
    tiers = []
    for part in raw.split(","):
        attempts, minutes = part.strip().split(":")
        tiers.append((int(attempts), int(minutes)))
    return sorted(tiers)


def lock_duration(failed_logins: int, tiers: list[tuple[int, int]]) -> timedelta | None:
    reached = [minutes for attempts, minutes in tiers if failed_logins >= attempts]
    return timedelta(minutes=reached[-1]) if reached else None
