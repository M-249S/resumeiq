"""
Per-user daily allowance for the AI-backed endpoints.

The per-IP rate limit stops bursts, but nothing stops one signed-in user
(or a script holding one account) from making a few thousand AI calls a
day, and sign-up is free. This counter caps how many AI requests a single
account can make per UTC day, whatever address it comes from, so one
account cannot use up the shared free AI allowance.

State is in memory, so it resets when the process restarts and is not
shared between instances. That is acceptable for a single small instance;
move the counters to the database or Redis if the service is ever scaled
out.
"""
import os
import threading
from datetime import datetime, timezone


class UserDailyQuota:
    def __init__(self, limit: int):
        self.limit = limit
        self._lock = threading.Lock()
        self._day = self._today()
        self._used: dict[int, int] = {}

    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _roll_over(self) -> None:
        today = self._today()
        if today != self._day:
            self._day = today
            self._used = {}

    def try_consume(self, user_id: int) -> bool:
        with self._lock:
            self._roll_over()
            used = self._used.get(user_id, 0)
            if used >= self.limit:
                return False
            self._used[user_id] = used + 1
            return True

    def refund(self, user_id: int) -> None:
        """Give a unit back when the request did not reach the AI provider or failed."""
        with self._lock:
            self._roll_over()
            used = self._used.get(user_id, 0)
            if used > 1:
                self._used[user_id] = used - 1
            else:
                self._used.pop(user_id, None)


user_quota = UserDailyQuota(int(os.getenv("USER_DAILY_AI_LIMIT", "30")))
