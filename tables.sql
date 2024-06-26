CREATE TABLE IF NOT EXISTS sunset_reminder (
    user_id INTEGER NOT NULL PRIMARY KEY ASC
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS rent_status (
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    rent_paid BOOLEAN NOT NULL,
    PRIMARY KEY (year, month)
);

CREATE TABLE IF NOT EXISTS rent_reminders (
    date TEXT PRIMARY KEY
);