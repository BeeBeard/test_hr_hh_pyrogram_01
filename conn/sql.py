from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from conn.engines import engine
from conn.tables import User


def get_user_data(user_id: int = None) -> [User, None]:
    """
    Получить данные пользователя user_id
    :return:
    """
    if not user_id:
        return None

    with engine.connect() as conn:
        try:

            stmt = (select(User).filter(User.id == user_id))
            result = conn.execute(stmt)
            return result.one_or_none()
        except Exception as e:
            print("ALERT get_user_data \n\n", e)
            return None


def get_user_data_by_time() -> [User, None]:
    """
    Получить данные всех пользователей
    :return:
    """

    with engine.connect() as conn:
        try:

            stmt = (
                select(User)
                .filter(
                    # User.created_at <= datetime.now() - timedelta(minutes=time_passed),
                    User.message_num <= 3
                ))
            result = conn.execute(stmt)
            return result.all()
        except Exception as e:
            print("ALERT get_user_data_by_time \n\n", e)
            return None


def update_user_data(**kwargs) -> [bool, int]:
    with engine.connect() as conn:

        try:
            stmt = insert(User).values(**kwargs)
            stmt = stmt.on_conflict_do_update(set_=dict(**kwargs))
            conn.execute(stmt)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)


if __name__ == "__main__":
    pass
