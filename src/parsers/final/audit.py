"""Transformation helpers: stg_audit_line_raw -> 3NF audit-domain row payloads.

Each function reads from staging ORM rows (or a pre-fetched list) and returns
dicts ready for insertion into the corresponding 3NF table. The loader is
responsible for session management and insertion order.
"""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.final.host import Host
from src.models.staging.audit import StgAuditLineRaw

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Maps each audit event type to its 3NF subtype table name.
SUBTYPE_MAP: dict[str, str] = {
    # msg-bearing subtypes
    "CRED_ACQ": "audit_pam_event",
    "USER_ACCT": "audit_pam_event",
    "USER_START": "audit_pam_event",
    "USER_END": "audit_pam_event",
    "CRED_DISP": "audit_pam_event",
    "USER_AUTH": "audit_pam_event",
    "CRED_REFR": "audit_pam_event",
    "SERVICE_START": "audit_service_event",
    "SERVICE_STOP": "audit_service_event",
    "USER_LOGIN": "audit_user_login_event",
    "USER_CMD": "audit_user_cmd_event",
    # outer-field subtypes
    "LOGIN": "audit_login_event",
    "SYSCALL": "audit_syscall_event",
    "AVC": "audit_avc_event",
    "PROCTITLE": "audit_proctitle_event",
}

#: The 12 atomic attributes unpacked from the msg blob into audit_message.
_MSG_ATTRIBUTES = (
    "op",
    "acct",
    "exe",
    "hostname",
    "addr",
    "terminal",
    "res",
    "unit",
    "comm",
    "id",
    "cwd",
    "cmd",
)

# Outer-field columns sourced from staging for each outer-field subtype.
_LOGIN_FIELDS = ("old_auid", "old_ses", "tty", "res")
_SYSCALL_FIELDS = ("arch", "syscall", "success", "exit", "exe", "comm", "tty", "key")
_AVC_FIELDS = ("apparmor", "operation", "profile", "name", "info", "comm")
_PROCTITLE_FIELDS = ("proctitle",)

# key=value regex: handles key='val', key="val", key=bare
_KV_RE = re.compile(r"""(\w+)=(?:'([^']*)'|"([^"]*)"|(\S+))""")


# ---------------------------------------------------------------------------
# Host map
# ---------------------------------------------------------------------------


def build_host_map(session: Session) -> dict[str, int]:
    """Return {host_key: host_id} from the already-loaded final host table.

    Used to resolve stg_audit_line_raw.source_host -> audit_event.host_id.
    Must be called after the host domain load is complete.
    """
    rows = session.execute(select(Host.host_key, Host.host_id)).all()
    return {row.host_key: row.host_id for row in rows}


# ---------------------------------------------------------------------------
# msg unpacking (1NF resolution)
# ---------------------------------------------------------------------------


def parse_msg(msg: str | None) -> dict[str, str | int | None]:
    """Unpack one raw msg blob into the 12 atomic audit_message attributes.

    The msg field stores key=value pairs in a single cell, e.g.:
        op=PAM:accounting acct="root" exe="/usr/sbin/cron" hostname=? res=success

    Each pair is extracted and mapped to the 12 expected attribute names.
    Unknown keys are ignored. The '?' sentinel is normalised to None.
    Integer coercion is attempted for the `id` attribute only.

    Args:
        msg: Raw msg string from stg_audit_line_raw, or None / empty string.

    Returns:
        Dict with all 12 _MSG_ATTRIBUTES keys; missing values are None.
    """
    result: dict[str, str | int | None] = dict.fromkeys(_MSG_ATTRIBUTES)

    if not msg:
        return result

    for match in _KV_RE.finditer(msg):
        key = match.group(1).lower()
        value: str | None = next((g for g in match.groups()[1:] if g is not None), None)
        if value in ("?", ""):
            value = None
        if key in result:
            result[key] = value

    if result["id"] is not None:
        try:
            result["id"] = int(result["id"])  # type: ignore[arg-type]
        except (ValueError, TypeError):
            result["id"] = None

    return result


# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------


def transform_audit_events(session: Session, host_map: dict[str, int]) -> list[dict]:
    """Transform stg_audit_line_raw rows into audit_event rows.

    Args:
        session: Active DB session with staging data loaded.
        host_map: {host_key: host_id} from the final host table.

    Returns:
        List of dicts matching AuditEvent columns (excluding event_id).

    Raises:
        ValueError: If any staging row's source_host is not in host_map.

    Expected: 3,048 rows.
    """
    stg_rows = session.scalars(select(StgAuditLineRaw)).all()
    rows = []
    for r in stg_rows:
        host_id = host_map.get(r.source_host)
        if host_id is None:
            raise ValueError(
                f"Host lookup failed: source_host='{r.source_host}' "
                f"(line_number={r.line_number}) not found in host table. "
                f"Known hosts: {sorted(host_map)}"
            )
        rows.append(
            {
                "host_id": host_id,
                "line_number": r.line_number,
                "raw_line": r.raw_line,
                "type": r.type,
                "epoch": r.epoch,
                "serial": r.serial,
                "timestamp": r.timestamp,
                "pid": r.pid,
                "uid": r.uid,
                "auid": r.auid,
                "ses": r.ses,
            }
        )
    return rows


def extract_audit_messages(stg_rows: list, event_id_map: dict[tuple[int, int], int]) -> list[dict]:
    """Extract audit_message rows from staging rows that have a non-null msg.

    Resolves event_id via (host_id, line_number) -> event_id lookup built
    after audit_event insertion.

    Args:
        stg_rows: ORM rows from stg_audit_line_raw (pre-fetched by caller).
        event_id_map: {(host_id, line_number): event_id} from inserted audit_event rows.

    Returns:
        List of dicts matching AuditMessage columns.

    Expected: 2,614 rows (validated: events where msg is not null).
    """
    rows = []
    for r in stg_rows:
        if not r.msg:
            continue
        event_id = event_id_map.get((r.host_id_resolved, r.line_number))
        if event_id is None:
            raise ValueError(
                f"event_id lookup failed for msg-bearing row: "
                f"host_id_resolved={r.host_id_resolved}, "
                f"line_number={r.line_number}"
            )
        rows.append({"event_id": event_id, **parse_msg(r.msg)})
    return rows


def route_subtype(event_type: str) -> str:
    """Return the subtype table name for the given audit event type.

    Args:
        event_type: Value of stg_audit_line_raw.type (case-insensitive).

    Returns:
        Subtype table name string from SUBTYPE_MAP.

    Raises:
        ValueError: If event_type is not in SUBTYPE_MAP.
    """
    table = SUBTYPE_MAP.get(event_type.upper())
    if table is None:
        raise ValueError(
            f"Unknown audit event type '{event_type}'. Known types: {sorted(SUBTYPE_MAP)}"
        )
    return table


def extract_subtype_rows(
    stg_rows: list,
    event_id_map: dict[tuple[int, int], int],
    host_map: dict[str, int],
) -> dict[str, list[dict]]:
    """Route each staging row into its subtype table bucket.

    For msg-bearing subtypes (pam, service, user_login, user_cmd) the row
    contains only event_id; content lives in audit_message.
    For outer-field subtypes (login, syscall, avc, proctitle) columns are
    sourced directly from staging outer fields.

    Args:
        stg_rows: ORM rows from stg_audit_line_raw (pre-fetched by caller).
        event_id_map: {(host_id, line_number): event_id} from inserted audit_event rows.
        host_map: {host_key: host_id} used to reconstruct the lookup key.

    Returns:
        Dict mapping subtype table name -> list of row dicts.

    Expected total across all buckets: 3,048 rows (one per audit_event).
    """
    buckets: dict[str, list[dict]] = {t: [] for t in set(SUBTYPE_MAP.values())}

    for r in stg_rows:
        host_id = host_map.get(r.source_host)
        if host_id is None:
            raise ValueError(
                f"Host lookup failed in subtype routing: "
                f"source_host='{r.source_host}' (line_number={r.line_number}) "
                f"not found in host table. Known hosts: {sorted(host_map)}"
            )
        event_id = event_id_map.get((host_id, r.line_number))
        if event_id is None:
            raise ValueError(
                f"event_id lookup failed in subtype routing: "
                f"host_id={host_id}, line_number={r.line_number}"
            )

        # route_subtype raises ValueError for unknown types (total specialization)
        table = route_subtype(r.type)

        row: dict = {"event_id": event_id}

        if table == "audit_login_event":
            for col in _LOGIN_FIELDS:
                row[col] = getattr(r, col, None)
        elif table == "audit_syscall_event":
            for col in _SYSCALL_FIELDS:
                row[col] = getattr(r, col, None)
        elif table == "audit_avc_event":
            for col in _AVC_FIELDS:
                row[col] = getattr(r, col, None)
        elif table == "audit_proctitle_event":
            for col in _PROCTITLE_FIELDS:
                row[col] = getattr(r, col, None)
        # msg-bearing subtypes: event_id only

        buckets[table].append(row)

    return buckets
