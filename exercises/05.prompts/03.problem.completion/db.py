"""The EpicMe journal database.

This file is infrastructure, not the lesson. It's a small wrapper around
stdlib sqlite3 and it is identical in every exercise that uses it, so the
only thing that changes between steps is the MCP code you write.

You never need to edit this file. Skim it once so you know what's available:

    db.create_entry(...)      db.get_entry(id)      db.get_entries()
    db.create_tag(...)        db.get_tag(id)        db.get_tags()
    db.add_tag_to_entry(entry_id, tag_id)
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass, field

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    mood        TEXT,
    location    TEXT,
    weather     TEXT,
    is_private  INTEGER NOT NULL DEFAULT 1,
    is_favorite INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS entry_tags (
    entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    tag_id   INTEGER NOT NULL REFERENCES tags(id)    ON DELETE CASCADE,
    PRIMARY KEY (entry_id, tag_id)
);
"""


@dataclass
class Tag:
    id: int
    name: str
    description: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Entry:
    id: int
    title: str
    content: str
    mood: str | None = None
    location: str | None = None
    weather: str | None = None
    is_private: int = 1
    is_favorite: int = 0
    tags: list[Tag] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class DB:
    """A tiny journal database. Defaults to in-memory, which is what tests use."""

    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)

    # --- entries ---------------------------------------------------------

    def create_entry(
        self,
        title: str,
        content: str,
        mood: str | None = None,
        location: str | None = None,
        weather: str | None = None,
        is_private: int = 1,
        is_favorite: int = 0,
    ) -> Entry:
        cur = self._conn.execute(
            "INSERT INTO entries (title, content, mood, location, weather,"
            " is_private, is_favorite) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, content, mood, location, weather, is_private, is_favorite),
        )
        self._conn.commit()
        entry = self.get_entry(cur.lastrowid)
        assert entry is not None
        return entry

    def get_entry(self, entry_id: int) -> Entry | None:
        row = self._conn.execute(
            "SELECT * FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()
        if row is None:
            return None
        return Entry(**dict(row), tags=self.get_entry_tags(entry_id))

    def get_entries(self) -> list[Entry]:
        rows = self._conn.execute("SELECT * FROM entries ORDER BY id").fetchall()
        return [Entry(**dict(r), tags=self.get_entry_tags(r["id"])) for r in rows]

    def update_entry(self, entry_id: int, **fields) -> Entry | None:
        allowed = {
            "title", "content", "mood", "location", "weather",
            "is_private", "is_favorite",
        }
        updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if updates:
            assignments = ", ".join(f"{k} = ?" for k in updates)
            self._conn.execute(
                f"UPDATE entries SET {assignments} WHERE id = ?",
                (*updates.values(), entry_id),
            )
            self._conn.commit()
        return self.get_entry(entry_id)

    def delete_entry(self, entry_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self._conn.commit()
        return cur.rowcount > 0

    # --- tags ------------------------------------------------------------

    def create_tag(self, name: str, description: str | None = None) -> Tag:
        cur = self._conn.execute(
            "INSERT INTO tags (name, description) VALUES (?, ?)", (name, description)
        )
        self._conn.commit()
        tag = self.get_tag(cur.lastrowid)
        assert tag is not None
        return tag

    def get_tag(self, tag_id: int) -> Tag | None:
        row = self._conn.execute("SELECT * FROM tags WHERE id = ?", (tag_id,)).fetchone()
        return Tag(**dict(row)) if row else None

    def get_tags(self) -> list[Tag]:
        rows = self._conn.execute("SELECT * FROM tags ORDER BY id").fetchall()
        return [Tag(**dict(r)) for r in rows]

    def update_tag(self, tag_id: int, **fields) -> Tag | None:
        updates = {
            k: v for k, v in fields.items()
            if k in {"name", "description"} and v is not None
        }
        if updates:
            assignments = ", ".join(f"{k} = ?" for k in updates)
            self._conn.execute(
                f"UPDATE tags SET {assignments} WHERE id = ?",
                (*updates.values(), tag_id),
            )
            self._conn.commit()
        return self.get_tag(tag_id)

    def delete_tag(self, tag_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        self._conn.commit()
        return cur.rowcount > 0

    # --- the join --------------------------------------------------------

    def add_tag_to_entry(self, entry_id: int, tag_id: int) -> bool:
        self._conn.execute(
            "INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
            (entry_id, tag_id),
        )
        self._conn.commit()
        return True

    def get_entry_tags(self, entry_id: int) -> list[Tag]:
        rows = self._conn.execute(
            "SELECT t.* FROM tags t JOIN entry_tags et ON et.tag_id = t.id"
            " WHERE et.entry_id = ? ORDER BY t.id",
            (entry_id,),
        ).fetchall()
        return [Tag(**dict(r)) for r in rows]

    def seed(self) -> None:
        """Put a little data in the journal so there's something to look at."""
        if self.get_entries():
            return
        home = self.create_tag("home", "Life at home")
        work = self.create_tag("work", "Life at work")
        self.create_tag("travel", "Trips and adventures")

        first = self.create_entry(
            title="A quiet morning",
            content="Woke up early, made coffee, watched the fog burn off the hills.",
            mood="calm",
            location="home",
            weather="foggy",
        )
        self.add_tag_to_entry(first.id, home.id)

        second = self.create_entry(
            title="Shipped the thing",
            content="The deploy went out clean. Nobody noticed, which is the point.",
            mood="proud",
            location="office",
            weather="clear",
            is_favorite=1,
        )
        self.add_tag_to_entry(second.id, work.id)
