import os
from sqlalchemy import create_engine
from conn.tables import Base

db_name = "my_database.db"
engine = create_engine(f"sqlite:///{db_name}")  # , echo=True


def check_tables():
    Base.metadata.create_all(engine)


def rebuild_tables():
    """
        Удалить и создать базу заново
        :return:
        """

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    pass
