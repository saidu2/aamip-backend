from sqlalchemy.orm import Session
from app.models.market import AuditLog

def log_action(db: Session, user, action: str, target: str = None, ip: str = None):
    entry = AuditLog(
        user_id   = user.id,
        user_name = user.full_name,
        user_role = user.role,
        action    = action,
        target    = target,
        ip_address= ip,
    )
    db.add(entry)
    db.commit()
