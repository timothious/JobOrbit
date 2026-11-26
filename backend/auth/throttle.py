import math
import time
from collections import defaultdict
from datetime import datetime, timedelta

from core.clock import Clock
from core.errors import AppError


class LoginThrottle:
    """NFR-015: at most 5 failed logins per 15 minutes per client IP, with a growing delay.

    State is in memory: the API runs as a single process on SQLite, and a restart only
    resets the counters.
    """

    def __init__(
        self,
        clock: Clock,
        max_failures: int = 5,
        window: timedelta = timedelta(minutes=15),
        delay_step_seconds: float = 0.5,
    ) -> None:
        self._clock = clock
        self._max_failures = max_failures
        self._window = window
        self._delay_step = delay_step_seconds
        self._failures: dict[str, list[datetime]] = defaultdict(list)

    def _recent(self, ip: str) -> list[datetime]:
        cutoff = self._clock.now() - self._window
        recent = [t for t in self._failures.get(ip, []) if t > cutoff]
        self._failures[ip] = recent
        return recent

    def check(self, ip: str) -> None:
        recent = self._recent(ip)
        if len(recent) >= self._max_failures:
            retry_after = recent[0] + self._window - self._clock.now()
            seconds = max(1, math.ceil(retry_after.total_seconds()))
            raise AppError(
                429,
                "rate_limited",
                "Too many failed login attempts. Try again later.",
                headers={"Retry-After": str(seconds)},
            )

    def record_failure(self, ip: str) -> None:
        recent = self._recent(ip)
        recent.append(self._clock.now())
        time.sleep(self._delay_step * len(recent))

    def reset(self, ip: str) -> None:
        self._failures.pop(ip, None)
