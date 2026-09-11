from collections.abc import Callable, Collection
from threading import Lock

from app.identities import MockIdentity, Role


designated_approver_ids: set[str] = set()

# Designations are process-local demonstration state, matching the record
# store. The lock makes each check-and-transition atomic within the single
# supported application process; see backend/README.md for the single-worker
# deployment constraint.
_approver_designation_lock = Lock()


def change_approver_designation(
    identity_id: str,
    *,
    designated: bool,
    record_change: Callable[[], None],
) -> bool:
    with _approver_designation_lock:
        currently_designated = identity_id in designated_approver_ids
        if currently_designated == designated:
            return False
        record_change()
        if designated:
            designated_approver_ids.add(identity_id)
        else:
            designated_approver_ids.remove(identity_id)
        return True


def has_role(identity: MockIdentity, role: Role) -> bool:
    return role in identity.roles


def is_administrator(identity: MockIdentity) -> bool:
    return has_role(identity, Role.ADMINISTRATOR)


def is_designated_approver(identity: MockIdentity) -> bool:
    return identity.id in designated_approver_ids


def can_decide_proposal(identity: MockIdentity) -> bool:
    return is_designated_approver(identity)


def can_manage_replacements(identity: MockIdentity) -> bool:
    return is_administrator(identity)


def can_manage_approvers(identity: MockIdentity) -> bool:
    return is_administrator(identity)


def role_permissions(identity: MockIdentity) -> Collection[str]:
    permissions = {"view_records", "create_records", "add_comments"}
    if is_designated_approver(identity):
        permissions.update({"accept_proposals", "reject_proposals"})
    if is_administrator(identity):
        permissions.update(
            {
                "administer_approvers",
                "archive_records",
                "restore_records",
                "create_replacements",
                "abandon_replacements",
            }
        )
    return permissions
