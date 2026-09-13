from __future__ import annotations

import json
import math
import re
import sqlite3
from collections import deque
from pathlib import Path
from typing import Any

from .models import Evidence

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


class EvidenceStore:
    def __init__(self, evidence_source: Path | list[Evidence] | list[dict[str, Any]]):
        if isinstance(evidence_source, Path):
            raw = json.loads(evidence_source.read_text())
        else:
            raw = evidence_source

        self.evidence: list[Evidence] = []
        for item in raw:
            if isinstance(item, Evidence):
                self.evidence.append(item)
            else:
                self.evidence.append(
                    Evidence(
                        evidence_id=item["evidence_id"],
                        entity=item["entity"],
                        text=item["text"],
                        event_time=item["event_time"],
                        observed_time=item["observed_time"],
                        source=item["source"],
                        links=tuple(item.get("links", [])),
                        tags=tuple(item.get("tags", [])),
                    )
                )
        self.by_id = {item.evidence_id: item for item in self.evidence}
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            "CREATE VIRTUAL TABLE evidence_fts USING fts5(evidence_id UNINDEXED, entity, text, tags)"
        )
        self.conn.executemany(
            "INSERT INTO evidence_fts(evidence_id, entity, text, tags) VALUES (?, ?, ?, ?)",
            [(item.evidence_id, item.entity, item.text, " ".join(item.tags)) for item in self.evidence],
        )

    def exact(self, query: str, limit: int = 4) -> list[Evidence]:
        q = query.lower()
        matches = [
            item
            for item in self.evidence
            if item.entity.lower() in q or item.evidence_id.lower() in q
        ]
        return matches[:limit]

    def lexical(self, query: str, limit: int = 4) -> list[Evidence]:
        terms = sorted(_tokens(query) - {"the", "a", "an", "is", "was", "in", "of", "to"})
        if not terms:
            return []
        fts_query = " OR ".join(f'"{term}"' for term in terms)
        rows = self.conn.execute(
            "SELECT evidence_id FROM evidence_fts WHERE evidence_fts MATCH ? LIMIT ?",
            (fts_query, limit),
        ).fetchall()
        return [self.by_id[row[0]] for row in rows]

    def vector(self, query: str, limit: int = 4) -> list[Evidence]:
        q_tokens = _tokens(query)
        ranked: list[tuple[float, Evidence]] = []
        for item in self.evidence:
            e_tokens = _tokens(f"{item.entity} {item.text} {' '.join(item.tags)}")
            overlap = len(q_tokens & e_tokens)
            denom = math.sqrt(max(1, len(q_tokens)) * max(1, len(e_tokens)))
            score = overlap / denom
            if score:
                ranked.append((score, item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1].evidence_id))
        return [item for _, item in ranked[:limit]]

    def temporal(self, items: list[Evidence], as_of: str | None, limit: int = 4) -> list[Evidence]:
        if not items:
            items = list(self.evidence)
        if as_of:
            items = [item for item in items if item.event_time <= as_of]
        items.sort(key=lambda item: (item.event_time, item.observed_time, item.evidence_id), reverse=True)
        return items[:limit]

    def graph(self, seeds: list[Evidence], depth: int = 3, limit: int = 8) -> list[Evidence]:
        if not seeds:
            return []
        seen = {item.evidence_id for item in seeds}
        out = list(seeds)
        queue = deque((item.evidence_id, 0) for item in seeds)
        while queue and len(out) < limit:
            current_id, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            current = self.by_id[current_id]
            for linked in current.links:
                if linked in self.by_id and linked not in seen:
                    seen.add(linked)
                    out.append(self.by_id[linked])
                    queue.append((linked, current_depth + 1))
                    if len(out) >= limit:
                        break
        return out
