from sqlalchemy.orm import Session
import models
from security.auth import hash_password


def create_user(db: Session, username: str, password: str):

    hashed = hash_password(password)

    user = models.User(
        username=username,
        password=hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(db: Session, username: str):

    return db.query(models.User).filter(
        models.User.username == username
    ).first()


def create_trade(db: Session, topic: str, user_id: int):

    trade = models.Trade(
        topic=topic,
        user_id=user_id
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    return trade


def get_trades(db: Session):

    return db.query(models.Trade).all()


def delete_trade(db: Session, trade_id: int):

    trade = db.query(models.Trade).filter(
        models.Trade.id == trade_id
    ).first()

    if trade:
        db.delete(trade)
        db.commit()

    return trade