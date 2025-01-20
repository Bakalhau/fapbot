import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = 'data/fapbot.db'):
        self.db_path = db_path
        self.setup_database()

    def get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn, conn.cursor()

    def setup_database(self):
        conn, cur = self.get_connection()
        
        # Create tables
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                faps INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                fapcoins INTEGER DEFAULT 0,
                last_daily TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, item_name)
            );

            CREATE TABLE IF NOT EXISTS user_succubus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                succubus_id TEXT,
                acquired_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, succubus_id)
            );
        """)
        
        conn.commit()
        conn.close()

    # User methods
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn, cur = self.get_connection()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        conn.close()
        return dict(result) if result else None

    def create_or_update_user(self, user_id: str, username: str):
        conn, cur = self.get_connection()
        cur.execute("""
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username = ?
        """, (user_id, username, username))
        conn.commit()
        conn.close()

    def update_user_score(self, user_id: str, faps: int, score: int):
        conn, cur = self.get_connection()
        cur.execute("""
            UPDATE users 
            SET faps = ?, score = ?
            WHERE user_id = ?
        """, (faps, score, user_id))
        conn.commit()
        conn.close()

    def get_scoreboard(self) -> List[Dict[str, Any]]:
        conn, cur = self.get_connection()
        cur.execute("""
            SELECT user_id, username, faps, score
            FROM users
            WHERE faps > 0
            ORDER BY score ASC, username ASC
        """)
        result = [dict(row) for row in cur.fetchall()]
        conn.close()
        return result

    # Item methods
    def get_user_items(self, user_id: str) -> Dict[str, int]:
        conn, cur = self.get_connection()
        cur.execute("""
            SELECT item_name, quantity
            FROM items
            WHERE user_id = ? AND quantity > 0
        """, (user_id,))
        items = {row['item_name']: row['quantity'] for row in cur.fetchall()}
        conn.close()
        return items

    def update_item_quantity(self, user_id: str, item_name: str, quantity: int):
        conn, cur = self.get_connection()
        cur.execute("""
            INSERT INTO items (user_id, item_name, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_name) 
            DO UPDATE SET quantity = quantity + ?
        """, (user_id, item_name, quantity, quantity))
        conn.commit()
        conn.close()

    # Fapcoin methods
    def get_fapcoins(self, user_id: str) -> int:
        conn, cur = self.get_connection()
        cur.execute("SELECT fapcoins FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        conn.close()
        return result['fapcoins'] if result else 0

    def update_fapcoins(self, user_id: str, amount: int):
        conn, cur = self.get_connection()
        cur.execute("""
            UPDATE users 
            SET fapcoins = fapcoins + ?
            WHERE user_id = ?
        """, (amount, user_id))
        conn.commit()
        conn.close()

    def update_daily_timestamp(self, user_id: str):
        conn, cur = self.get_connection()
        cur.execute("""
            UPDATE users 
            SET last_daily = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()
        conn.close()

    def get_last_daily(self, user_id: str) -> Optional[datetime]:
        conn, cur = self.get_connection()
        cur.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        conn.close()
        return datetime.fromisoformat(result['last_daily']) if result and result['last_daily'] else None

    # Succubus methods
    def add_available_succubus(self, succubus_data: Dict[str, Any]):
        conn, cur = self.get_connection()
        cur.execute("""
            INSERT INTO available_succubus 
            (succubus_id, name, image_url, ability, ability_description, 
             burden, burden_description, rarity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(succubus_id) DO UPDATE SET
                name = ?, image_url = ?, ability = ?, ability_description = ?,
                burden = ?, burden_description = ?, rarity = ?
        """, (
            succubus_data['id'], succubus_data['name'], succubus_data['image'],
            succubus_data['ability'], succubus_data['ability_description'],
            succubus_data['burden'], succubus_data['burden_description'],
            succubus_data['rarity'],
            succubus_data['name'], succubus_data['image'],
            succubus_data['ability'], succubus_data['ability_description'],
            succubus_data['burden'], succubus_data['burden_description'],
            succubus_data['rarity']
        ))
        conn.commit()
        conn.close()

    def get_user_succubus(self, user_id: str) -> List[Dict[str, Any]]:
        conn, cur = self.get_connection()
        cur.execute("""
            SELECT succubus_id, acquired_date
            FROM user_succubus
            WHERE user_id = ?
        """, (user_id,))
        result = [dict(row) for row in cur.fetchall()]
        conn.close()
        return result

    def add_user_succubus(self, user_id: str, succubus_id: str):
        conn, cur = self.get_connection()
        cur.execute("""
            INSERT INTO user_succubus (user_id, succubus_id)
            VALUES (?, ?)
            ON CONFLICT(user_id, succubus_id) DO NOTHING
        """, (user_id, succubus_id))
        conn.commit()
        conn.close()

    def get_succubus_by_rarity(self, rarity: str) -> List[Dict[str, Any]]:
        conn, cur = self.get_connection()
        cur.execute("""
            SELECT *
            FROM available_succubus
            WHERE rarity = ?
        """, (rarity,))
        result = [dict(row) for row in cur.fetchall()]
        conn.close()
        return result

    def get_all_succubus(self) -> List[Dict[str, Any]]:
        conn, cur = self.get_connection()
        cur.execute("SELECT * FROM available_succubus")
        result = [dict(row) for row in cur.fetchall()]
        conn.close()
        return result

    # Migration method
    def migrate_from_json(self, scoreboard_path: str, items_path: str, succubus_path: str):
        """Migrate existing JSON data to SQLite database"""
        # Load JSON data
        with open(scoreboard_path) as f:
            scoreboard = json.load(f)
        with open(items_path) as f:
            items_data = json.load(f)
        with open(succubus_path) as f:
            succubus_data = json.load(f)

        conn, cur = self.get_connection()

        # Migrate users and scores
        for username, data in scoreboard.items():
            cur.execute("""
                INSERT INTO users (user_id, username, faps, score, fapcoins)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    faps = ?, score = ?, fapcoins = ?
            """, (
                username, username, data['faps'], data['score'],
                items_data.get('fapcoins', {}).get(username, 0),
                data['faps'], data['score'],
                items_data.get('fapcoins', {}).get(username, 0)
            ))

        # Migrate items
        for username, items in items_data.get('items', {}).items():
            for item_name, quantity in items.items():
                cur.execute("""
                    INSERT INTO items (user_id, item_name, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, item_name) DO UPDATE SET quantity = ?
                """, (username, item_name, quantity, quantity))

        # Migrate succubus data
        for succubus_id, data in succubus_data['available_succubus'].items():
            cur.execute("""
                INSERT INTO available_succubus 
                (succubus_id, name, image_url, ability, ability_description,
                 burden, burden_description, rarity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                succubus_id, data['name'], data['image'],
                data['ability'], data['ability_description'],
                data['burden'], data['burden_description'],
                data['rarity']
            ))

        # Migrate user succubus
        for user_id, succubus_list in succubus_data['user_succubus'].items():
            for succubus_id, details in succubus_list.items():
                cur.execute("""
                    INSERT INTO user_succubus (user_id, succubus_id, acquired_date)
                    VALUES (?, ?, ?)
                """, (user_id, succubus_id, details['acquired_date']))

        conn.commit()
        conn.close()