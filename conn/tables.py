from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import String, BigInteger, Integer, DateTime, text


class Base(DeclarativeBase):
    pass


class User(Base):  # Parent
    __tablename__ = "users"
    __table_args__ = {'comment': 'Данные пользователя из ТГ'}

    id = mapped_column(BigInteger, primary_key=True, unique=True, nullable=False, index=True, comment='ID пользователя')
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='Время создания')
    message_num = mapped_column(Integer, nullable=False, server_default='0', comment='Номер отправленного сообщения')
    status = mapped_column(String(20), nullable=True, server_default=text('alive'), comment='Статус пользователя')
    status_updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='Время обновления')

    def __repr__(self) -> str:
        return (f"User("
                f"id={self.id!r}, "
                f"created_at={self.created_at!r}, "
                f"message_num={self.message_num!r}, "
                f"status={self.status!r}, "
                f"status_updated_at={self.status_updated_at!r})"
                )


if __name__ == "__main__":
    pass
