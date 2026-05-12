"""
Smart Medical AI — Antigravity RBAC Engine
Système de gestion des rôles et permissions (5 niveaux)
"""

from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass, field


class RoleLevel(Enum):
    PATIENT   = 1
    ASSISTANT = 2
    SECRETARY = 3
    DOCTOR    = 4
    ADMIN     = 5


@dataclass
class Permission:
    """Représente une permission granulaire."""
    id: str           # ex: "doctor:view_own_patients"
    name: str
    resource: str     # patients, consultations, etc.
    action: str       # view, create, edit, delete, manage
    scope: str = "own"   # own, team, all, self, basic
    level: int = 1
    description: str = ""


@dataclass
class Role:
    """Représente un rôle avec ses permissions."""
    id: int
    name: str
    level: int
    description: str = ""
    permissions: List[Permission] = field(default_factory=list)

    def has_permission(self, permission_id: str) -> bool:
        """Vérifie si ce rôle possède une permission donnée."""
        return any(p.id == permission_id for p in self.permissions)

    def can_perform(self, resource: str, action: str) -> bool:
        """Vérifie si ce rôle peut effectuer une action sur une ressource."""
        return any(
            p.resource == resource and (p.action == action or p.action == "manage")
            for p in self.permissions
        )

    def get_permission_ids(self) -> List[str]:
        return [p.id for p in self.permissions]


class AntigravityRBAC:
    """
    Moteur RBAC Antigravity — MediERP.

    Gère les rôles et permissions pour les 5 niveaux :
    PATIENT (1) < ASSISTANT (2) < SECRETARY (3) < DOCTOR (4) < ADMIN (5)
    """

    def __init__(self, db):
        self.db = db
        self._roles: Dict[str, Role] = {}        # name → Role
        self._roles_by_id: Dict[int, Role] = {}  # id → Role
        self._user_perm_cache: Dict[int, List[str]] = {}
        self._load()

    # ================================================================
    # INITIALISATION
    # ================================================================

    def _load(self) -> None:
        """Charge tous les rôles et permissions depuis la BD."""
        try:
            roles_data = self.db.fetch_all("SELECT * FROM roles ORDER BY level")
            for row in roles_data:
                perms = self._load_role_permissions(row["id"])
                role = Role(
                    id=row["id"],
                    name=row["name"],
                    level=row["level"],
                    description=row.get("description", ""),
                    permissions=perms
                )
                self._roles[row["name"]] = role
                self._roles_by_id[row["id"]] = role
            print(f"[RBAC] ✅ {len(self._roles)} rôles chargés")
        except Exception as e:
            print(f"[RBAC] ⚠️  Erreur chargement rôles: {e}")
            self._load_defaults()

    def _load_role_permissions(self, role_id: int) -> List[Permission]:
        """Charge les permissions d'un rôle depuis role_permissions_v2."""
        try:
            query = """
                SELECT p.* FROM permissions p
                JOIN role_permissions_v2 rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
            """
            results = self.db.fetch_all(query, (role_id,))
            permissions = []
            for row in results:
                perm = Permission(
                    id=row["id"],
                    name=row["name"],
                    resource=row.get("resource", ""),
                    action=row.get("action", ""),
                    scope=row.get("scope", "own"),
                    level=row.get("level", 1),
                    description=row.get("description", "")
                )
                permissions.append(perm)
            return permissions
        except Exception as e:
            print(f"[RBAC] ⚠️  Erreur permissions rôle {role_id}: {e}")
            return []

    def _load_defaults(self) -> None:
        """Fallback: définir les rôles en mémoire si la BD n'est pas prête."""
        default_roles = [
            Role(1, "PATIENT",   1, "Patient"),
            Role(2, "ASSISTANT", 2, "Assistant médical"),
            Role(3, "SECRETARY", 3, "Secrétaire"),
            Role(4, "DOCTOR",    4, "Médecin"),
            Role(5, "ADMIN",     5, "Administrateur"),
        ]
        for role in default_roles:
            self._roles[role.name] = role
            self._roles_by_id[role.id] = role
        print("[RBAC] ⚠️  Rôles par défaut chargés (sans permissions BD)")

    def reload(self) -> None:
        """Recharger les rôles depuis la BD (après migration)."""
        self._roles.clear()
        self._roles_by_id.clear()
        self._user_perm_cache.clear()
        self._load()

    # ================================================================
    # CONSULTATION ROLES / PERMISSIONS
    # ================================================================

    def get_user_roles(self, user_id: int) -> List[Role]:
        """Récupère les rôles d'un utilisateur (via user_roles + fallback role TEXT)."""
        roles = []

        # 1. Essai via table user_roles
        try:
            query = """
                SELECT r.* FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ?
            """
            rows = self.db.fetch_all(query, (user_id,))
            for row in rows:
                role_name = row["name"]
                if role_name in self._roles:
                    roles.append(self._roles[role_name])
        except Exception:
            pass

        # 2. Fallback : lire le champ role TEXT de users
        if not roles:
            try:
                user = self.db.fetch_one(
                    "SELECT role FROM users WHERE id = ?", (user_id,)
                )
                if user and user["role"] in self._roles:
                    roles.append(self._roles[user["role"]])
            except Exception:
                pass

        return roles

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Retourne toutes les permission IDs d'un utilisateur (avec cache)."""
        if user_id in self._user_perm_cache:
            return self._user_perm_cache[user_id]

        roles = self.get_user_roles(user_id)
        perm_ids = set()
        for role in roles:
            perm_ids.update(role.get_permission_ids())

        result = list(perm_ids)
        self._user_perm_cache[user_id] = result
        return result

    def get_user_role_name(self, user_id: int) -> str:
        """Retourne le nom du rôle principal (le plus haut niveau)."""
        roles = self.get_user_roles(user_id)
        if not roles:
            return "UNKNOWN"
        # Retourner le rôle avec le niveau le plus élevé
        return max(roles, key=lambda r: r.level).name

    def get_user_level(self, user_id: int) -> int:
        """Retourne le niveau de permission maximal de l'utilisateur."""
        roles = self.get_user_roles(user_id)
        if not roles:
            return 0
        return max(r.level for r in roles)

    # ================================================================
    # VÉRIFICATION PERMISSIONS
    # ================================================================

    def has_permission(self, user_id: int, permission_id: str) -> bool:
        """Vérifie si l'utilisateur possède une permission donnée."""
        return permission_id in self.get_user_permissions(user_id)

    def can_perform(self, user_id: int, resource: str, action: str) -> bool:
        """Vérifie si l'utilisateur peut effectuer une action sur une ressource."""
        roles = self.get_user_roles(user_id)
        return any(role.can_perform(resource, action) for role in roles)

    def enforce_permission(self, user_id: int, permission_id: str) -> None:
        """Lève PermissionError si l'utilisateur n'a pas la permission."""
        if not self.has_permission(user_id, permission_id):
            raise PermissionError(
                f"[RBAC] Accès refusé: l'utilisateur {user_id} "
                f"ne possède pas la permission '{permission_id}'"
            )

    def is_admin(self, user_id: int) -> bool:
        return self.get_user_level(user_id) >= 5

    def is_doctor(self, user_id: int) -> bool:
        return self.get_user_level(user_id) >= 4

    def is_secretary(self, user_id: int) -> bool:
        return self.get_user_level(user_id) >= 3

    def is_assistant(self, user_id: int) -> bool:
        return self.get_user_level(user_id) >= 2

    # ================================================================
    # GESTION RÔLES
    # ================================================================

    def assign_role(self, user_id: int, role_name: str) -> bool:
        """Assigne un rôle à un utilisateur."""
        if role_name not in self._roles:
            raise ValueError(f"[RBAC] Rôle '{role_name}' introuvable")

        role = self._roles[role_name]
        try:
            self.db.execute(
                "INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)",
                (user_id, role.id)
            )
            # Mettre à jour le champ role TEXT aussi (rétrocompatibilité)
            self.db.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (role_name, user_id)
            )
            # Invalider le cache
            self._user_perm_cache.pop(user_id, None)
            return True
        except Exception as e:
            print(f"[RBAC] Erreur assign_role: {e}")
            return False

    def revoke_role(self, user_id: int, role_name: str) -> bool:
        """Révoque un rôle d'un utilisateur."""
        if role_name not in self._roles:
            return False
        role = self._roles[role_name]
        try:
            self.db.execute(
                "DELETE FROM user_roles WHERE user_id = ? AND role_id = ?",
                (user_id, role.id)
            )
            self._user_perm_cache.pop(user_id, None)
            return True
        except Exception as e:
            print(f"[RBAC] Erreur revoke_role: {e}")
            return False

    def change_role(self, user_id: int, new_role_name: str) -> bool:
        """Change le rôle principal d'un utilisateur (révoque tous, assigne nouveau)."""
        try:
            self.db.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
            self._user_perm_cache.pop(user_id, None)
            return self.assign_role(user_id, new_role_name)
        except Exception as e:
            print(f"[RBAC] Erreur change_role: {e}")
            return False

    # ================================================================
    # INTROSPECTION
    # ================================================================

    def get_all_roles(self) -> List[Role]:
        """Retourne tous les rôles triés par niveau."""
        return sorted(self._roles.values(), key=lambda r: r.level)

    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self._roles.get(name)

    def get_permissions_for_role(self, role_name: str) -> List[Permission]:
        role = self._roles.get(role_name)
        return role.permissions if role else []

    def invalidate_cache(self, user_id: int = None) -> None:
        """Invalide le cache de permissions."""
        if user_id:
            self._user_perm_cache.pop(user_id, None)
        else:
            self._user_perm_cache.clear()
