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
                last_daily TIMESTAMP,
                active_succubus TEXT,
                last_succubus_activation TIMESTAMP
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

    def get_all_users(self) -> List[str]:
        conn, cur = self.get_connection()
        cur.execute("SELECT user_id FROM users")
        result = [row['user_id'] for row in cur.fetchall()]
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
        """
        Update the last_daily timestamp for a user.
        Using current UTC time for consistency.
        """
        current_time = datetime.utcnow().isoformat()
        conn, cur = self.get_connection()
        cur.execute("""
            UPDATE users 
            SET last_daily = ?
            WHERE user_id = ?
        """, (current_time, user_id))
        conn.commit()
        conn.close()

    def get_last_daily(self, user_id: str) -> Optional[datetime]:
        conn, cur = self.get_connection()
        cur.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        conn.close()
        
        last_daily = datetime.fromisoformat(result['last_daily']) if result and result['last_daily'] else None
        
        return last_daily

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
        
    # Active Succubus methods
    def activate_succubus(self, user_id: str, succubus_id: str) -> bool:
        """Ativa uma succubus para o usuário, retorna True se bem sucedido"""
        conn, cur = self.get_connection()
        
        # Verifica se o usuário possui essa succubus
        cur.execute("""
            SELECT COUNT(*) as count FROM user_succubus 
            WHERE user_id = ? AND succubus_id = ?
        """, (user_id, succubus_id))
        
        result = cur.fetchone()
        if not result or result['count'] == 0:
            conn.close()
            return False
        
        # Usar UTC para consistência
        current_time = datetime.utcnow().isoformat()
            
        # Ativa a succubus e atualiza o timestamp
        cur.execute("""
            UPDATE users 
            SET active_succubus = ?, 
                last_succubus_activation = ?
            WHERE user_id = ?
        """, (succubus_id, current_time, user_id))
        
        conn.commit()
        conn.close()
        return True
        
    def get_active_succubus(self, user_id: str) -> Optional[str]:
        """Retorna o ID da succubus ativa do usuário"""
        conn, cur = self.get_connection()
        cur.execute("""
            SELECT active_succubus, last_succubus_activation 
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cur.fetchone()
        conn.close()
        
        if not result or not result['active_succubus']:
            return None
            
        return result['active_succubus']
        
    def get_succubus_activation_time(self, user_id: str) -> Optional[datetime]:
        """Retorna o timestamp da última ativação de succubus"""
        conn, cur = self.get_connection()
        cur.execute("""
            SELECT last_succubus_activation 
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cur.fetchone()
        conn.close()
        
        if not result or not result['last_succubus_activation']:
            return None
        
        # Parse the ISO timestamp from the database
        activation_time = datetime.fromisoformat(result['last_succubus_activation'])
            
        return activation_time