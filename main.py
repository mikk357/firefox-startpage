import dataclasses
import os
import random
import sqlite3
from urllib.parse import urlsplit
from typing import List

import jinja2
import toml


@dataclasses.dataclass
class Bookmark:
    title: str
    url: str

    def faviconurl(self) -> str:
        o = urlsplit(self.url)
        return f"{o.scheme}://{o.netloc}/favicon.ico"


@dataclasses.dataclass
class BookmarksFolder:
    name: str
    bookmarks: List[Bookmark]


# TODO: more classes with colors
css_classes = [
    "dev", "social", "other"
]


def random_class():
    return random.choice(css_classes)


class Main:
    def __init__(self):
        self.config = toml.load("config.toml")
        self.connection = sqlite3.connect(
            os.path.join(
                os.path.expandvars(self.config['profile']),
                "places.sqlite"
            ),
            detect_types=sqlite3.PARSE_COLNAMES
        )
        self.env = jinja2.Environment(
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True
        )
        with open("template.html", "r", encoding="utf-8") as fp:
            self.template = self.env.from_string(
                fp.read(),
                globals=dict(
                    title=self.config.get('title'),
                    random_class=random_class
                )
            )
        self.bookmarks = []

    def read_bookmarks(self):
        cur = self.connection.cursor()
        cur.execute(
            ("SELECT id as folder_id, title as folder_title "
             "FROM moz_bookmarks "
             "WHERE type = 2 AND parent = ( "
             "   SELECT id as parent_id "
             "   FROM moz_bookmarks "
             "   WHERE type = 2 AND title = ? )"),
            [self.config["bookmarks"]])
        folders = cur.fetchall()

        sql = (
            "SELECT url, moz_bookmarks.title AS title FROM moz_bookmarks "
            "LEFT JOIN moz_places ON fk=moz_places.id "
            "WHERE url <> '' AND moz_bookmarks.parent = ? "
            "ORDER BY moz_bookmarks.position"
        )
        for i, j in folders:
            cur.execute(sql, [i])
            self.bookmarks.append(
                BookmarksFolder(name=j, bookmarks=[
                    Bookmark(url=b[0], title=b[1]) for b in cur.fetchall()
                ])
            )

    def render(self):
        self.template.stream(
            folders=self.bookmarks,
        ).dump("index.html")


if __name__ == "__main__":
    main = Main()
    main.read_bookmarks()
    main.render()
