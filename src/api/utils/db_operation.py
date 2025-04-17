from sqlalchemy.orm import Session


def commit_and_refresh(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
