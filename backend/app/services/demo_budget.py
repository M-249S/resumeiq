"""
Global daily budget for the unauthenticated demo endpoint.

Per-IP rate limits stop one visitor hammering the demo, but not many
visitors (or a spoofed address). This counter puts a hard ceiling on how
many guest analyses can reach the paid AI provider per UTC day, whatever
the source.

State is in memory, so it resets when the process restarts and is not
shared between instances. That is acceptable for a single small instance;
use Redis or the database if the service is ever scaled out.
"""
import os
import threading
from datetime import datetime, timezone


class DailyBudget:
    def __init__(self, limit: int):
        self.limit = limit
        self._lock = threading.Lock()
        self._day = self._today()
        self._used = 0

    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _roll_over(self) -> None:
        today = self._today()
        if today != self._day:
            self._day = today
            self._used = 0

    def try_consume(self) -> bool:
        with self._lock:
            self._roll_over()
            if self._used >= self.limit:
                return False
            self._used += 1
            return True

    def refund(self) -> None:
        """Give a unit back, e.g. when the AI call failed through no fault of the user."""
        with self._lock:
            self._roll_over()
            if self._used > 0:
                self._used -= 1


demo_budget = DailyBudget(int(os.getenv("DEMO_DAILY_LIMIT", "100")))
