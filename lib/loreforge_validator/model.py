"""Shared data structures for LoreForge validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def line(self) -> str:
        return f"{self.code}: {self.path}: {self.message}"
