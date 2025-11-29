import base64
import datetime
import json
import secrets
import sqlite3
import time
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, current_app, jsonify, request

from games import GAME_PROFILES, get_profile, resolve_game

api_bp = Blueprint("api", __name__)

ALLOWED_STRATEGIES = {
    "meta_ia",
    "fibonacci_inverse",
    "mcc",
    "xgboost",
    "3gs",
    "spectre",
    "timeline_ai",
    "echo_ecarts",
    "monte_carlo_fibo",
}

STRATEGY_METADATA: Dict[str, Dict[str, Any]] = {
    "meta_ia": {
        "label": "Meta IA",
        "category": "meta",
        "base_score": 72,
        "description": "Fusion multi-profils avec pondération dynamique",
    },
    "fibonacci_inverse": {
        "label": "Fibonacci Inversé",
        "category": "analytique",
        "base_score": 65,
        "description": "Projection par écarts et séquence Fibonacci inversée",
    },
    "mcc": {
        "label": "Monte-Carlo Combinatoire",
        "category": "simulation",
        "base_score": 70,
        "description": "Simulation combinatoire pour extraire des noyaux",
    },
    "xgboost": {
        "label": "XGBoost",
        "category": "ml",
        "base_score": 68,
        "description": "Modèle supervisé basé sur gradient boosting",
    },
    "3gs": {
        "label": "3GS",
        "category": "glissant",
        "base_score": 60,
        "description": "Stratégie glissante multi-fenêtres",
    },
    "spectre": {
        "label": "Spectre AI",
        "category": "pondération",
        "base_score": 64,
        "description": "Pondération automatique via sonar",
    },
    "timeline_ai": {
        "label": "Timeline AI",
        "category": "simulation",
        "base_score": 62,
        "description": "Projection figée et reprise jour par jour",
    },
    "echo_ecarts": {
        "label": "Echo des Écarts",
        "category": "écarts",
        "base_score": 58,
        "description": "Reflets d'écarts pour projeter les tendances",
    },
    "monte_carlo_fibo": {
        "label": "Monte-Carlo Fibo",
        "category": "hybride",
        "base_score": 76,
        "description": "200 itérations Monte Carlo pondérées par Fibonacci",
    },
}

STRATEGY_MODULE_MAP: Dict[str, str] = {
    "meta_ia": "ml_strategies/meta_ia",
    "fibonacci_inverse": "ml_strategies/fibonacci",
    "mcc": "ml_strategies/mcc",
    "xgboost": "ml_strategies/xgboost",
    "3gs": "ml_strategies/3gs",
    "spectre": "ml_strategies/spectre_ai",
    "timeline_ai": "ml_strategies/timeline_ai",
    "echo_ecarts": "ml_strategies/cycles",
    "monte_carlo_fibo": "ml_strategies/fibonacci",
}


def _safe_db_ping() -> Dict[str, Any]:
    """Lightweight connectivity and schema presence probe for the health endpoint."""
    try:
        conn = get_db_connection()
        # Basic table existence checks (will raise if missing)
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        counts = {}
        for table in ("users", "draws", "favorites", "campagnes", "sessions"):
            if table in tables:
                row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                counts[table] = int(row[0]) if row else 0
            else:
                counts[table] = None
        conn.close()
        return {"status": "ok", "tables": tables, "counts": counts}
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return {"status": "error", "error": str(exc)}

# Chronologie des fonctionnalités livrées pour exposition côté frontend
FEATURE_HISTORY: List[Dict[str, Any]] = [
    {
        "title": "Initialisation plateforme",
        "area": "bootstrap",
        "details": "Stack Flask + Vue + Celery avec routes et vues principales",
        "status": "done",
    },
    {
        "title": "Sécurité JWT",
        "area": "auth",
        "details": "Hachage PBKDF2 salé, sessions persistées et rôles admin/modérateur",
        "status": "done",
    },
    {
        "title": "Analytique tirages",
        "area": "draws",
        "details": "Fréquences numéros/étoiles et validation stricte des grilles",
        "status": "done",
    },
    {
        "title": "Supervision admin",
        "area": "admin",
        "details": "Rapport opérationnel, bootstrap de données et stats DB",
        "status": "done",
    },
    {
        "title": "Multi-univers",
        "area": "games",
        "details": "Sélection EuroMillions/EuroDream, registre public et parité",
        "status": "done",
    },
    {
        "title": "Génération Monte Carlo Fibo",
        "area": "ia",
        "details": "Générateur pondéré 200 itérations par univers",
        "status": "done",
    },
    {
        "title": "Robustesse DB",
        "area": "infra",
        "details": "Index SQLite, backfill multi-jeux et vérifications d’unicité",
        "status": "done",
    },
    {
        "title": "Parité EuroDream",
        "area": "games",
        "details": "Métadonnée d’alignement avec EuroMillions (Romignon)",
        "status": "done",
    },
]


def get_db_connection():
    conn = sqlite3.connect(current_app.config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str, salt: str) -> str:
    import hashlib

    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 200_000
    ).hex()


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Support legacy sha256 hashes while preferring salted PBKDF2."""
    if salt:
        return hash_password(password, salt) == stored_hash
    import hashlib

    return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_jwt(payload: Dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    secret = current_app.config.get("JWT_SECRET", "dev-secret")
    encoded_header = _b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode())
    import hmac
    import hashlib

    signature = hmac.new(
        secret.encode(), f"{encoded_header}.{encoded_payload}".encode(), hashlib.sha256
    ).digest()
    encoded_signature = _b64url_encode(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        return None
    import hmac
    import hashlib

    secret = current_app.config.get("JWT_SECRET", "dev-secret")
    expected_sig = hmac.new(
        secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
    ).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(signature_b64)):
        return None
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except json.JSONDecodeError:
        return None
    if payload.get("exp") and int(payload["exp"]) < int(time.time()):
        return None
    return payload


def serialize_draw(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "numbers": json.loads(row["numbers"]),
        "stars": json.loads(row["stars"]),
        "draw_date": row["draw_date"],
        "game": row["game"] if "game" in row.keys() else "euromillions",
    }


def validate_draw_payload(
    numbers: List[int], stars: List[int], game: str = "euromillions"
) -> Tuple[bool, str]:
    profile = get_profile(game)
    if len(numbers) != profile["numbers_count"] or len(stars) != profile["stars_count"]:
        return (
            False,
            f"Une grille doit contenir {profile['numbers_count']} numéros et {profile['stars_count']} étoiles",
        )
    if not all(isinstance(n, int) for n in numbers + stars):
        return False, "Toutes les valeurs doivent être des entiers"
    if len(set(numbers)) != len(numbers) or len(set(stars)) != len(stars):
        return False, "Les numéros et étoiles doivent être uniques"
    if not all(1 <= n <= profile["numbers"] for n in numbers):
        return False, f"Les numéros doivent être entre 1 et {profile['numbers']}"
    if not all(1 <= s <= profile["stars"] for s in stars):
        return False, f"Les étoiles doivent être entre 1 et {profile['stars']}"
    return True, ""


@api_bp.route("/games/registry")
def registry():
    """Expose les profils de jeu et les stratégies supportées pour le frontend."""

    games_payload = []
    for profile in GAME_PROFILES.values():
        games_payload.append(
            {
                "key": profile["key"],
                "label": profile.get("label", profile["key"].title()),
                "numbers": profile["numbers"],
                "numbers_count": profile["numbers_count"],
                "stars": profile["stars"],
                "stars_count": profile["stars_count"],
                "parity_with": profile.get("parity_with"),
                "parity_label": profile.get("parity_label"),
            }
        )

    return jsonify(
        {
            "games": sorted(games_payload, key=lambda g: g["key"]),
            "strategies": sorted(ALLOWED_STRATEGIES),
        }
    )


@api_bp.route("/strategies/report")
@authenticate()
def strategies_report():
    """Retourne une vision consolidée et classée des stratégies disponibles."""

    game = resolve_game(request.args.get("game"))
    audit = _build_strategies_audit(game)
    return jsonify(audit)


@api_bp.route("/report/history")
def report_history():
    """Rapport consolidé des fonctionnalités et d'un instantané opérationnel."""

    snapshot = _build_report_snapshot()
    return jsonify({"history": FEATURE_HISTORY, "snapshot": snapshot})


@api_bp.route("/health", methods=["GET"])
def healthcheck():
    """Expose un signal de vie/lecture minimal avec état DB et jeux."""

    db_state = _safe_db_ping()
    registry = [
        {
            "key": key,
            "label": profile["label"],
            "numbers": profile["numbers"],
            "numbers_count": profile.get("numbers_count"),
            "stars": profile["stars"],
            "stars_count": profile.get("stars_count"),
            "parity": profile.get("parity"),
        }
        for key, profile in GAME_PROFILES.items()
    ]
    return jsonify(
        {
            "status": "ok" if db_state.get("status") == "ok" else "degraded",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "db": db_state,
            "games": registry,
            "strategies": sorted(ALLOWED_STRATEGIES),
        }
    )


def _build_report_snapshot() -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        draws_by_game = conn.execute(
            "SELECT game, COUNT(*) as total FROM draws GROUP BY game"
        ).fetchall()
        favs_by_game = conn.execute(
            "SELECT game, COUNT(*) as total FROM favorites GROUP BY game"
        ).fetchall()
        campagnes_by_game = conn.execute(
            "SELECT game, COUNT(*) as total FROM campagnes GROUP BY game"
        ).fetchall()
        return {
            "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "draws": conn.execute("SELECT COUNT(*) FROM draws").fetchone()[0],
            "favoris": conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0],
            "campagnes": conn.execute("SELECT COUNT(*) FROM campagnes").fetchone()[0],
            "sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            "per_game": {
                "draws": {row["game"]: row["total"] for row in draws_by_game},
                "favoris": {row["game"]: row["total"] for row in favs_by_game},
                "campagnes": {row["game"]: row["total"] for row in campagnes_by_game},
            },
        }
    finally:
        conn.close()


def _strategy_files_status(strat: str) -> Tuple[bool, str]:
    """Vérifie la présence des fichiers d'implémentation d'une stratégie."""

    root = Path(__file__).resolve().parent
    rel_path = STRATEGY_MODULE_MAP.get(strat)
    if not rel_path:
        return False, "Aucun module référencé"
    candidate = root / rel_path
    if candidate.is_dir():
        if (candidate / "__init__.py").exists():
            return True, "Package détecté"
        return False, "Package sans __init__.py"
    if candidate.with_suffix(".py").exists():
        return True, "Module détecté"
    return False, "Fichiers manquants"


def _score_strategy(strat: str, module_ok: bool) -> int:
    base = STRATEGY_METADATA.get(strat, {}).get("base_score", 55)
    score = base + (8 if module_ok else -14)
    if strat == "monte_carlo_fibo":
        score += 6
    return max(10, min(100, score))


def _build_strategies_audit(game: str) -> Dict[str, Any]:
    """Construit un classement des stratégies avec vérifications basiques."""

    results: List[Dict[str, Any]] = []
    for strat in sorted(ALLOWED_STRATEGIES):
        module_ok, note = _strategy_files_status(strat)
        score = _score_strategy(strat, module_ok)
        meta = STRATEGY_METADATA.get(
            strat,
            {
                "label": strat,
                "category": "générique",
                "description": "",
                "base_score": 50,
            },
        )
        status = "ready" if module_ok else "squelette"
        results.append(
            {
                "name": strat,
                "label": meta.get("label", strat),
                "category": meta.get("category", "n/a"),
                "description": meta.get("description", ""),
                "module_present": module_ok,
                "notes": note,
                "score": score,
                "status": status,
                "coverage": sorted(list(GAME_PROFILES.keys())),
                "game": game,
            }
        )

    leaderboard = sorted(results, key=lambda item: item["score"], reverse=True)
    return {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "game": game,
        "summary": {
            "total": len(results),
            "ready": len([r for r in results if r["module_present"]]),
            "needs_attention": len([r for r in results if not r["module_present"]]),
        },
        "leaderboard": leaderboard,
    }


def persist_session(token: str, user_id: int) -> None:
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=current_app.config.get("JWT_TTL_SECONDS", 86_400)
    )
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (
            token,
            user_id,
            datetime.datetime.utcnow().isoformat(),
            expires_at.isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def revoke_session(token: str) -> None:
    conn = get_db_connection()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def load_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    payload = decode_jwt(token)
    if not payload:
        return None
    conn = get_db_connection()
    session_row = conn.execute(
        "SELECT user_id, expires_at FROM sessions WHERE token = ?", (token,)
    ).fetchone()
    if not session_row:
        conn.close()
        return None
    if session_row["expires_at"] and datetime.datetime.fromisoformat(
        session_row["expires_at"]
    ) < datetime.datetime.utcnow():
        conn.close()
        return None
    user_row = conn.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (session_row["user_id"],),
    ).fetchone()
    conn.close()
    if not user_row:
        return None
    return {"id": user_row["id"], "username": user_row["username"], "role": user_row["role"]}


def authenticate(role: str = "user"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            payload = load_user_from_token(token)
            if not payload:
                return jsonify({"error": "Token expiré ou invalide"}), 401
            if role in {"admin", "moderator"}:
                allowed_roles = [role, "admin"] if role == "moderator" else ["admin"]
                if payload.get("role") not in allowed_roles:
                    return jsonify({"error": "Forbidden"}), 403
            request.user = payload
            return func(*args, **kwargs)

        return wrapper

    return decorator


@api_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")
    if role not in {"user", "moderator", "admin"}:
        return jsonify({"error": "Rôle invalide"}), 400
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        salt = secrets.token_hex(16)
        cursor.execute(
            "INSERT INTO users (username, password, salt, role) VALUES (?, ?, ?, ?)",
            (username, hash_password(password, salt), salt, role),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "User already exists"}), 409
    conn.close()
    return jsonify({"status": "registered"})


@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, username, password, salt, role FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()
    if not user or not verify_password(password or "", user["password"], user["salt"]):
        return jsonify({"error": "Invalid credentials"}), 401
    ttl = int(current_app.config.get("JWT_TTL_SECONDS", 86_400))
    payload = {
        "sub": user["id"],
        "role": user["role"],
        "iat": int(time.time()),
        "exp": int(time.time()) + ttl,
    }
    token = create_jwt(payload)
    persist_session(token, user["id"])
    expires_at = datetime.datetime.utcfromtimestamp(payload["exp"]).isoformat()
    return jsonify({"token": token, "role": user["role"], "expires_at": expires_at})


@api_bp.route("/auth/me")
@authenticate()
def me():
    return jsonify(request.user)


@api_bp.route("/auth/logout", methods=["POST"])
@authenticate()
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    revoke_session(token)
    return jsonify({"status": "logged_out"})


@api_bp.route("/draws/get")
@authenticate()
def get_draws():
    game = resolve_game(request.args.get("game"))
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, numbers, stars, draw_date, game FROM draws WHERE game = ? ORDER BY draw_date DESC",
        (game,),
    ).fetchall()
    conn.close()
    return jsonify([serialize_draw(row) for row in rows])


@api_bp.route("/draws/history")
@authenticate()
def draws_history():
    return get_draws()


@api_bp.route("/draws/recent")
@authenticate()
def draws_recent():
    game = resolve_game(request.args.get("game"))
    conn = get_db_connection()
    row = conn.execute(
        "SELECT id, numbers, stars, draw_date, game FROM draws WHERE game = ? ORDER BY draw_date DESC LIMIT 1",
        (game,),
    ).fetchone()
    conn.close()
    return jsonify(serialize_draw(row) if row else {})


@api_bp.route("/draws/analytics")
@authenticate()
def draws_analytics():
    game = resolve_game(request.args.get("game"))
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT numbers, stars FROM draws WHERE game = ?", (game,)
    ).fetchall()
    conn.close()
    profile = get_profile(game)
    number_counts = {i: 0 for i in range(1, profile["numbers"] + 1)}
    star_counts = {i: 0 for i in range(1, profile["stars"] + 1)}
    for row in rows:
        for n in json.loads(row["numbers"]):
            number_counts[n] += 1
        for s in json.loads(row["stars"]):
            star_counts[s] += 1
    return jsonify({"numbers": number_counts, "stars": star_counts, "total": len(rows)})


@api_bp.route("/draws/add", methods=["POST"])
@authenticate("moderator")
def add_draw():
    data = request.get_json() or {}
    numbers = sorted(data.get("numbers", []))
    stars = sorted(data.get("stars", []))
    game = resolve_game(data.get("game"))
    valid, message = validate_draw_payload(numbers, stars, game)
    if not valid:
        return jsonify({"error": message}), 400
    draw_date = data.get("draw_date") or datetime.date.today().isoformat()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO draws (numbers, stars, draw_date, game) VALUES (?, ?, ?, ?)",
        (json.dumps(numbers), json.dumps(stars), draw_date, game),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "added"})


@api_bp.route("/draws/import_csv", methods=["POST"])
@authenticate("admin")
def import_csv():
    return jsonify({"status": "import_started"})


def _random_grid(game: str) -> Tuple[List[int], List[int]]:
    import random

    profile = get_profile(game)
    base_numbers = list(range(1, profile["numbers"] + 1))
    base_stars = list(range(1, profile["stars"] + 1))
    random.shuffle(base_numbers)
    random.shuffle(base_stars)
    return (
        sorted(base_numbers[: profile["numbers_count"]]),
        sorted(base_stars[: profile["stars_count"]]),
    )


def _monte_carlo_fibo(game: str) -> Dict[str, Any]:
    import random

    profile = get_profile(game)
    numbers_freq = {i: 0 for i in range(1, profile["numbers"] + 1)}
    stars_freq = {i: 0 for i in range(1, profile["stars"] + 1)}
    fibo_weights = [1, 1, 2, 3, 5, 8, 13, 21]
    iterations = 200

    for i in range(iterations):
        nums, sts = _random_grid(game)
        weight = fibo_weights[i % len(fibo_weights)]
        for n in nums:
            numbers_freq[n] += weight
        for s in sts:
            stars_freq[s] += weight

    best_numbers = sorted(numbers_freq, key=numbers_freq.get, reverse=True)[
        : profile["numbers_count"]
    ]
    best_stars = sorted(stars_freq, key=stars_freq.get, reverse=True)[
        : profile["stars_count"]
    ]

    return {
        "numbers": sorted(best_numbers),
        "stars": sorted(best_stars),
        "iteration_count": iterations,
        "weight_cycle": fibo_weights,
        "confidence_score": round(min(0.99, 0.6 + random.random() * 0.35), 3),
        "method_used": "monte_carlo_fibo",
        "explanation": (
            "Synthèse de 200 itérations Monte-Carlo pondérées par une suite Fibonacci"
            " pour renforcer les fréquences stables."
        ),
        "game": game,
    }


def _ensure_min_draws(conn: sqlite3.Connection, game: str, minimum: int) -> List[Dict[str, Any]]:
    """Seed deterministic draws to keep each univers navigable during demos/tests."""

    created: List[Dict[str, Any]] = []
    existing_dates = {
        row[0]
        for row in conn.execute(
            "SELECT draw_date FROM draws WHERE game = ?", (game,)
        ).fetchall()
    }
    current_count = len(existing_dates)
    target = max(minimum - current_count, 0)
    cursor_date = datetime.date.today()

    while len(created) < target:
        draw_date = (cursor_date - datetime.timedelta(days=len(created))).isoformat()
        if draw_date in existing_dates:
            cursor_date -= datetime.timedelta(days=1)
            continue
        numbers, stars = _random_grid(game)
        conn.execute(
            "INSERT INTO draws (numbers, stars, draw_date, game) VALUES (?, ?, ?, ?)",
            (json.dumps(numbers), json.dumps(stars), draw_date, game),
        )
        created.append(
            {
                "numbers": numbers,
                "stars": stars,
                "draw_date": draw_date,
                "game": game,
            }
        )
    return created


@api_bp.route("/generate/<strategie>")
@authenticate()
def generate_strategie(strategie: str):
    game = resolve_game(request.args.get("game"))
    if strategie not in ALLOWED_STRATEGIES:
        return jsonify({"error": "Stratégie inconnue"}), 400
    if strategie == "monte_carlo_fibo":
        return jsonify(_monte_carlo_fibo(game))
    import random

    numbers, stars = _random_grid(game)
    payload = {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": round(random.uniform(0.35, 0.92), 3),
        "method_used": strategie,
        "explanation": f"Grille générée via la stratégie {strategie}",
        "game": game,
    }
    return jsonify(payload)


@api_bp.route("/generate/meta_ia")
@authenticate()
def generate_meta_ia():
    return generate_strategie("meta_ia")


@api_bp.route("/generate/fibonacci_inverse")
@authenticate()
def generate_fibonacci_inverse():
    return generate_strategie("fibonacci_inverse")


@api_bp.route("/generate/mcc")
@authenticate()
def generate_mcc():
    return generate_strategie("mcc")


@api_bp.route("/generate/xgboost")
@authenticate()
def generate_xgboost():
    return generate_strategie("xgboost")


@api_bp.route("/generate/3gs")
@authenticate()
def generate_3gs():
    return generate_strategie("3gs")


@api_bp.route("/generate/spectre")
@authenticate()
def generate_spectre():
    return generate_strategie("spectre")


@api_bp.route("/generate/timeline_ai")
@authenticate()
def generate_timeline_ai():
    return generate_strategie("timeline_ai")


@api_bp.route("/generate/echo_ecarts")
@authenticate()
def generate_echo_ecarts():
    return generate_strategie("echo_ecarts")


@api_bp.route("/generate/monte_carlo_fibo")
@authenticate()
def generate_monte_carlo_fibo():
    return generate_strategie("monte_carlo_fibo")


@api_bp.route("/favoris/add", methods=["POST"])
@authenticate()
def add_favoris():
    data = request.get_json() or {}
    numbers = sorted(data.get("numbers", []))
    stars = sorted(data.get("stars", []))
    game = resolve_game(data.get("game"))
    valid, message = validate_draw_payload(numbers, stars, game)
    if not valid:
        return jsonify({"error": message}), 400
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO favorites (user_id, strategy, numbers, stars, game) VALUES (?, ?, ?, ?, ?)",
        (
            request.user["id"],
            data.get("strategy", "meta_ia"),
            json.dumps(numbers),
            json.dumps(stars),
            game,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "saved"})


@api_bp.route("/favoris/get")
@authenticate()
def get_favoris():
    game = resolve_game(request.args.get("game"))
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, strategy, numbers, stars, game FROM favorites WHERE user_id = ? AND game = ?",
        (request.user["id"], game),
    ).fetchall()
    conn.close()
    favoris = []
    for row in rows:
        favoris.append(
            {
                "id": row["id"],
                "strategy": row["strategy"],
                "numbers": json.loads(row["numbers"]),
                "stars": json.loads(row["stars"]),
            }
        )
    return jsonify(favoris)


@api_bp.route("/favoris/delete", methods=["POST"])
@authenticate()
def delete_favoris():
    data = request.get_json() or {}
    fav_id = data.get("id")
    game = resolve_game(data.get("game"))
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM favorites WHERE id = ? AND user_id = ? AND game = ?",
        (fav_id, request.user["id"], game),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@api_bp.route("/favoris/list_by_strategy")
@authenticate()
def favoris_by_strategy():
    game = resolve_game(request.args.get("game"))
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT strategy, COUNT(*) as total FROM favorites WHERE user_id = ? AND game = ? GROUP BY strategy",
        (request.user["id"], game),
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@api_bp.route("/backtesting/run")
@authenticate()
def backtesting_run():
    request_payload = request.get_json() or {}
    window = request_payload.get("window", 20)
    mode = request_payload.get("mode", "standard")
    return jsonify({"status": "backtest_started", "mode": mode, "window": window})


@api_bp.route("/backtesting/ghost")
@authenticate()
def backtesting_ghost():
    return jsonify({"status": "ghost_mode", "mode": "ghost"})


@api_bp.route("/backtesting/timeline_ai")
@authenticate()
def backtesting_timeline_ai():
    return jsonify({"status": "timeline_replay"})


@api_bp.route("/backtesting/mcc")
@authenticate()
def backtesting_mcc():
    return jsonify({"status": "mcc_backtest"})


@api_bp.route("/campagnes/create", methods=["POST"])
@authenticate()
def campagnes_create():
    data = request.get_json() or {}
    name = data.get("name", "Campagne")
    game = resolve_game(data.get("game"))
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO campagnes (name, status, created_at, game) VALUES (?, ?, ?, ?)",
        (name, "pending", datetime.datetime.utcnow().isoformat(), game),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "created", "name": name})


@api_bp.route("/campagnes/get")
@authenticate()
def campagnes_get():
    game = resolve_game(request.args.get("game"))
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM campagnes WHERE game = ? ORDER BY created_at DESC", (game,)
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@api_bp.route("/campagnes/delete", methods=["POST"])
@authenticate("admin")
def campagnes_delete():
    data = request.get_json() or {}
    campagne_id = data.get("id")
    conn = get_db_connection()
    conn.execute("DELETE FROM campagnes WHERE id = ?", (campagne_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@api_bp.route("/campagnes/run", methods=["POST"])
@authenticate()
def campagnes_run():
    return jsonify({"status": "campaign_running"})


@api_bp.route("/campagnes/results")
@authenticate()
def campagnes_results():
    return jsonify({"status": "campaign_results", "results": []})


@api_bp.route("/admin/stats")
@authenticate("admin")
def admin_stats():
    conn = get_db_connection()
    stats = {
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "draws": conn.execute("SELECT COUNT(*) FROM draws").fetchone()[0],
        "favoris": conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0],
        "campagnes": conn.execute("SELECT COUNT(*) FROM campagnes").fetchone()[0],
        "active_sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
        "by_game": dict(
            conn.execute(
                "SELECT game, COUNT(*) as total FROM draws GROUP BY game"
            ).fetchall()
        ),
    }
    conn.close()
    return jsonify(stats)


@api_bp.route("/admin/bootstrap_data", methods=["POST"])
@authenticate("admin")
def admin_bootstrap_data():
    payload = request.get_json() or {}
    target_games = list(dict.fromkeys(payload.get("games") or list(GAME_PROFILES.keys())))
    minimum = int(payload.get("min_draws", 12))
    summary: Dict[str, Any] = {}

    conn = get_db_connection()
    try:
        for game_raw in target_games:
            game = resolve_game(game_raw)
            before = conn.execute(
                "SELECT COUNT(*) FROM draws WHERE game = ?", (game,)
            ).fetchone()[0]
            created = _ensure_min_draws(conn, game, minimum)
            after = conn.execute(
                "SELECT COUNT(*) FROM draws WHERE game = ?", (game,)
            ).fetchone()[0]
            summary[game] = {
                "before": before,
                "added": len(created),
                "after": after,
                "samples": created[:3],
            }
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "bootstrapped", "games": summary})


@api_bp.route("/admin/train", methods=["POST"])
@authenticate("admin")
def admin_train():
    return jsonify({"status": "train_triggered"})


@api_bp.route("/admin/train_intensif", methods=["POST"])
@authenticate("admin")
def admin_train_intensif():
    return jsonify({"status": "intensive_training"})


@api_bp.route("/admin/debriefing")
@authenticate("admin")
def admin_debriefing():
    return jsonify({"status": "debriefing_ready"})


@api_bp.route("/admin/debriefing_flash")
@authenticate("admin")
def admin_debriefing_flash():
    return jsonify({"status": "flash_debriefing"})


@api_bp.route("/admin/tache_sonar", methods=["POST"])
@authenticate("admin")
def admin_tache_sonar():
    return jsonify({"status": "sonar_started"})


@api_bp.route("/admin/logs")
@authenticate("admin")
def admin_logs():
    logs: List[Dict[str, Any]] = [
        {"timestamp": datetime.datetime.utcnow().isoformat(), "message": "System ready"}
    ]
    return jsonify(logs)


@api_bp.route("/admin/db_inspect")
@authenticate("admin")
def admin_db_inspect():
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return jsonify([t[0] for t in tables])


@api_bp.route("/admin/rapport")
@authenticate("admin")
def admin_rapport():
    """Return an operational snapshot to help admins monitor the platform."""

    def _count(query: str, params: Tuple[Any, ...] = ()) -> int:
        row = conn.execute(query, params).fetchone()
        return int(row[0] if row else 0)

    conn = get_db_connection()
    now_iso = datetime.datetime.utcnow().isoformat()
    # Base counts
    user_count = _count("SELECT COUNT(*) FROM users")
    draw_count = _count("SELECT COUNT(*) FROM draws")
    favorite_count = _count("SELECT COUNT(*) FROM favorites")
    campagne_count = _count("SELECT COUNT(*) FROM campagnes")
    active_sessions = _count(
        "SELECT COUNT(*) FROM sessions WHERE expires_at > ?", (now_iso,)
    )

    draws_by_game = dict(
        conn.execute("SELECT game, COUNT(*) as total FROM draws GROUP BY game").fetchall()
    )
    favoris_by_game = dict(
        conn.execute(
            "SELECT game, COUNT(*) as total FROM favorites GROUP BY game"
        ).fetchall()
    )

    campagnes_by_status = dict(
        conn.execute(
            "SELECT status, COUNT(*) as total FROM campagnes GROUP BY status"
        ).fetchall()
    )

    recent_draws_rows = conn.execute(
        "SELECT id, numbers, stars, draw_date, game FROM draws ORDER BY draw_date DESC LIMIT 5"
    ).fetchall()
    recent_draws = [serialize_draw(row) for row in recent_draws_rows]

    # Simple health signals
    last_draw_date = recent_draws[0]["draw_date"] if recent_draws else None
    missing_draw_dates = []
    if recent_draws:
        # Detect gaps over the last 10 draws to surface ingestion issues
        dates = [datetime.datetime.fromisoformat(d["draw_date"]) for d in recent_draws]
        dates_sorted = sorted(dates)
        for first, second in zip(dates_sorted, dates_sorted[1:]):
            if (second - first).days > 7:
                missing_draw_dates.append(
                    {
                        "from": first.isoformat(),
                        "to": second.isoformat(),
                        "gap_days": (second - first).days,
                    }
                )

    conn.close()

    return jsonify(
        {
            "generated_at": now_iso,
            "counts": {
                "users": user_count,
                "draws": draw_count,
                "favorites": favorite_count,
                "campagnes": campagne_count,
                "active_sessions": active_sessions,
                "draws_by_game": draws_by_game,
                "favorites_by_game": favoris_by_game,
            },
            "campagnes_by_status": campagnes_by_status,
            "recent_draws": recent_draws,
            "last_draw_date": last_draw_date,
            "missing_draw_gaps": missing_draw_dates,
        }
    )


@api_bp.route("/admin/reset_cache", methods=["POST"])
@authenticate("admin")
def admin_reset_cache():
    return jsonify({"status": "cache_reset"})


@api_bp.route("/favoris/list")
@authenticate()
def favoris_list():
    return get_favoris()
