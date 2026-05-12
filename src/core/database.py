"""
Smart Medical AI - Database Manager (Flexible CRUD)
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = "./db/medierp_v2.db"):
        if self._initialized: return
        self.db_path = db_path
        self._connection = None
        self._initialize_database()
        self._initialized = True

    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=15.0)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def _initialize_database(self):
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../database/schema.sql"))
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema = f.read()
            conn = self._get_connection()
            try:
                conn.executescript(schema)
                conn.commit()
            except sqlite3.OperationalError as e:
                print(f"[Database] Avertissement lors de l'initialisation du schéma : {e}. (Ignoré si déjà initialisé)")

    @contextmanager
    def transaction(self):
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    # --- MÉTHODES FLEXIBLES ---

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        cursor = self._get_connection().execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Récupère un seul résultat à partir d'une requête SQL"""
        cursor = self._get_connection().execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_id(self, table: str, record_id: int) -> Optional[Dict]:
        """Méthode utilitaire pour récupérer par ID"""
        return self.fetch_one(f"SELECT * FROM {table} WHERE id = ?", (record_id,))

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        with self.transaction() as conn:
            cursor = conn.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def update(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        with self.transaction() as conn:
            cursor = conn.execute(query, tuple(data.values()) + (record_id,))
            return cursor.rowcount > 0

    def delete(self, table: str, record_id: int, hard: bool = False) -> bool:
        """Supprime un enregistrement. Tente un soft-delete par défaut si possible."""
        with self.transaction() as conn:
            if not hard:
                try:
                    # Tenter un soft delete (désactivation)
                    query = f"UPDATE {table} SET is_active = 0, deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
                    cursor = conn.execute(query, (record_id,))
                    if cursor.rowcount > 0:
                        return True
                except sqlite3.OperationalError:
                    # Si la colonne is_active n'existe pas, on passe au hard delete automatique
                    pass
            
            # Suppression réelle (Hard Delete)
            query = f"DELETE FROM {table} WHERE id = ?"
            cursor = conn.execute(query, (record_id,))
            return cursor.rowcount > 0

    def execute(self, query: str, params: Tuple = ()) -> int:
        """Exécute une requête SQL brute (INSERT/UPDATE/DELETE) et retourne lastrowid."""
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def apply_migration(self, migration_path: str) -> bool:
        """Applique un fichier de migration SQL."""
        import os
        if not os.path.exists(migration_path):
            print(f"[Database] Migration introuvable: {migration_path}")
            return False
        with open(migration_path, "r", encoding="utf-8") as f:
            sql = f.read()
        conn = self._get_connection()
        try:
            # Désactiver temporairement les FK pour permettre le drop/rename des tables
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.executescript(sql)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            print(f"[Database] Migration appliquee: {os.path.basename(migration_path)}")
            return True
        except Exception as e:
            conn.execute("PRAGMA foreign_keys = ON")
            print(f"[Database] Erreur migration: {e}")
            return False
