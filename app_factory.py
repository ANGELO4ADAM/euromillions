import os
import sqlite3
from flask import Flask
from flask_cors import CORS

from api import api_bp


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    cursor = conn.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cursor.fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def _ensure_index(conn: sqlite3.Connection, table: str, name: str, ddl: str) -> None:
    existing = {row[1] for row in conn.execute(f"PRAGMA index_list('{table}')")}
    if name not in existing:
        conn.execute(ddl)


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT 'user'
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numbers TEXT NOT NULL,
            stars TEXT NOT NULL,
            draw_date TEXT NOT NULL
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            strategy TEXT NOT NULL,
            numbers TEXT NOT NULL,
            stars TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS campagnes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            result TEXT
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);")
    _ensure_column(conn, "users", "salt", "salt TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "sessions", "expires_at", "expires_at TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "draws", "game", "game TEXT NOT NULL DEFAULT 'euromillions'")
    _ensure_column(conn, "favorites", "game", "game TEXT NOT NULL DEFAULT 'euromillions'")
    _ensure_column(conn, "campagnes", "game", "game TEXT NOT NULL DEFAULT 'euromillions'")

    _ensure_index(
        conn,
        "draws",
        "idx_draws_game_date",
        "CREATE INDEX IF NOT EXISTS idx_draws_game_date ON draws(game, draw_date)",
    )
    _ensure_index(
        conn,
        "draws",
        "idx_draws_date",
        "CREATE INDEX IF NOT EXISTS idx_draws_date ON draws(draw_date)",
    )
    _ensure_index(
        conn,
        "favorites",
        "idx_favorites_user_game",
        "CREATE INDEX IF NOT EXISTS idx_favorites_user_game ON favorites(user_id, game)",
    )
    _ensure_index(
        conn,
        "campagnes",
        "idx_campagnes_game",
        "CREATE INDEX IF NOT EXISTS idx_campagnes_game ON campagnes(game)",
    )

    # Backfill potential NULL/empty values after column introduction
    conn.execute(
        "UPDATE draws SET game = 'euromillions' WHERE game IS NULL OR game = ''"
    )
    conn.execute(
        "UPDATE favorites SET game = 'euromillions' WHERE game IS NULL OR game = ''"
    )
    conn.execute(
        "UPDATE campagnes SET game = 'euromillions' WHERE game IS NULL OR game = ''"
    )
    conn.commit()
    conn.close()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = os.environ.get("DB_PATH", "euromillions.db")
    app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "dev-secret")
    app.config["JWT_TTL_SECONDS"] = int(os.environ.get("JWT_TTL_SECONDS", 86_400))
    CORS(app)
    init_db(app.config["DB_PATH"])
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=8080, debug=True)
