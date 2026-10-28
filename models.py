from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Part(Base):
    __tablename__ = "parts"
    __table_args__ = (CheckConstraint("quantity >= 0", name="ck_parts_quantity"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    machine = Column(String(50), nullable=True)
    part = relationship("Part", lazy="joined")

    @property
    def part_name(self):
        return self.part.name