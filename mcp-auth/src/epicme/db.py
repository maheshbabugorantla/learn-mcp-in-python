"""The EpicMe journal database — now with more than one user in it.

This file is infrastructure, not the lesson. You never need to edit it.

If you did the fundamentals course, this is the same little sqlite3 wrapper with
one change running through all of it: **every row belongs to a user, and every
method takes a `user_id`**. There is no way to ask this database for "all
entries" any more — only for *a user's* entries. That's deliberate. The whole
point of the course is that a journal with users in it must never hand one
person another person's data, and the cheapest way to guarantee that is to make
the unscoped query impossible to write.

    db.create_entry(user_id, ...)   db.get_entry(user_id, id)   db.get_entries(user_id)
    db.create_tag(user_id, ...)     db.get_tag(user_id, id)     db.get_tags(user_id)
    db.add_tag_to_entry(user_id, entry_id, tag_id)

The `user_id` you pass comes from the access token, which is the part you build.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass, field

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL,
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
    user_id     TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    description TEXT,
    UNIQUE (user_id, name)
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


def _entry_row(row: sqlite3.Row) -> dict:
    """Drop `user_id` — it's a storage detail, not part of the entry itself."""
    data = dict(row)
    data.pop("user_id", None)
    return data


class DB:
    """A tiny multi-user journal. Defaults to in-memory, which is what tests use."""

    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)

    # --- entries ---------------------------------------------------------

    def create_entry(
        self,
        user_id: str,
        title: str,
        content: str,
        mood: str | None = None,
        location: str | None = None,
        weather: str | None = None,
        is_private: int = 1,
        is_favorite: int = 0,
    ) -> Entry:
        cur = self._conn.execute(
            "INSERT INTO entries (user_id, title, content, mood, location, weather,"
            " is_private, is_favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, title, content, mood, location, weather, is_private, is_favorite),
        )
        self._conn.commit()
        entry = self.get_entry(user_id, cur.lastrowid)
        assert entry is not None
        return entry

    def get_entry(self, user_id: str, entry_id: int) -> Entry | None:
        # The `user_id` in the WHERE clause is the whole security model: asking
        # for someone else's entry by id returns None, exactly like an entry
        # that was never written.
        row = self._conn.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        ).fetchone()
        if row is None:
            return None
        return Entry(**_entry_row(row), tags=self.get_entry_tags(user_id, entry_id))

    def get_entries(self, user_id: str) -> list[Entry]:
        rows = self._conn.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()
        return [
            Entry(**_entry_row(r), tags=self.get_entry_tags(user_id, r["id"]))
            for r in rows
        ]

    def update_entry(self, user_id: str, entry_id: int, **fields) -> Entry | None:
        allowed = {
            "title", "content", "mood", "location", "weather",
            "is_private", "is_favorite",
        }
        updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if updates:
            assignments = ", ".join(f"{k} = ?" for k in updates)
            self._conn.execute(
                f"UPDATE entries SET {assignments} WHERE id = ? AND user_id = ?",
                (*updates.values(), entry_id, user_id),
            )
            self._conn.commit()
        return self.get_entry(user_id, entry_id)

    def delete_entry(self, user_id: str, entry_id: int) -> bool:
        cur = self._conn.execute(
            "DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)
        )
        self._conn.commit()
        return cur.rowcount > 0

    # --- tags ------------------------------------------------------------

    def create_tag(
        self, user_id: str, name: str, description: str | None = None
    ) -> Tag:
        cur = self._conn.execute(
            "INSERT INTO tags (user_id, name, description) VALUES (?, ?, ?)",
            (user_id, name, description),
        )
        self._conn.commit()
        tag = self.get_tag(user_id, cur.lastrowid)
        assert tag is not None
        return tag

    def get_tag(self, user_id: str, tag_id: int) -> Tag | None:
        row = self._conn.execute(
            "SELECT id, name, description FROM tags WHERE id = ? AND user_id = ?",
            (tag_id, user_id),
        ).fetchone()
        return Tag(**dict(row)) if row else None

    def get_tags(self, user_id: str) -> list[Tag]:
        rows = self._conn.execute(
            "SELECT id, name, description FROM tags WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
        return [Tag(**dict(r)) for r in rows]

    def update_tag(self, user_id: str, tag_id: int, **fields) -> Tag | None:
        updates = {
            k: v for k, v in fields.items()
            if k in {"name", "description"} and v is not None
        }
        if updates:
            assignments = ", ".join(f"{k} = ?" for k in updates)
            self._conn.execute(
                f"UPDATE tags SET {assignments} WHERE id = ? AND user_id = ?",
                (*updates.values(), tag_id, user_id),
            )
            self._conn.commit()
        return self.get_tag(user_id, tag_id)

    def delete_tag(self, user_id: str, tag_id: int) -> bool:
        cur = self._conn.execute(
            "DELETE FROM tags WHERE id = ? AND user_id = ?", (tag_id, user_id)
        )
        self._conn.commit()
        return cur.rowcount > 0

    # --- the join --------------------------------------------------------

    def add_tag_to_entry(self, user_id: str, entry_id: int, tag_id: int) -> bool:
        # Look both up as this user first, so you can't staple your tag onto
        # somebody else's entry by guessing its id.
        if self.get_entry(user_id, entry_id) is None:
            return False
        if self.get_tag(user_id, tag_id) is None:
            return False
        self._conn.execute(
            "INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
            (entry_id, tag_id),
        )
        self._conn.commit()
        return True

    def get_entry_tags(self, user_id: str, entry_id: int) -> list[Tag]:
        rows = self._conn.execute(
            "SELECT t.id, t.name, t.description FROM tags t"
            " JOIN entry_tags et ON et.tag_id = t.id"
            " WHERE et.entry_id = ? AND t.user_id = ? ORDER BY t.id",
            (entry_id, user_id),
        ).fetchall()
        return [Tag(**dict(r)) for r in rows]

    def seed(self, user_id: str) -> None:
        """Put a little data in one user's journal so there's something to look at."""
        if self.get_entries(user_id):
            return
        home = self.create_tag(user_id, "home", "Life at home")
        work = self.create_tag(user_id, "work", "Life at work")
        self.create_tag(user_id, "travel", "Trips and adventures")

        first = self.create_entry(
            user_id,
            title="A quiet morning",
            content="Woke up early, made coffee, watched the fog burn off the hills.",
            mood="calm",
            location="home",
            weather="foggy",
        )
        self.add_tag_to_entry(user_id, first.id, home.id)

        second = self.create_entry(
            user_id,
            title="Shipped the thing",
            content="The deploy went out clean. Nobody noticed, which is the point.",
            mood="proud",
            location="office",
            weather="clear",
            is_favorite=1,
        )
        self.add_tag_to_entry(user_id, second.id, work.id)
