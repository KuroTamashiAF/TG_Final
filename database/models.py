from sqlalchemy import func, DateTime, String, Float,Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column





class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated:Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())





class Product(Base):
    __tablename__ = "product"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name:Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description:Mapped[str] = mapped_column(Text)
    price:Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    image:Mapped[str] = mapped_column(String(150))

