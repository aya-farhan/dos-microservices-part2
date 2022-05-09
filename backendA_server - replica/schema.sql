DROP TABLE IF EXISTS books;

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    topic text NOT NULL,
    cost INTEGER NOT NULL,
    number_of_items INTEGER NOT NULL
);


