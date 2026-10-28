import time
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import update
from sqlalchemy.orm import Session

import dto
from database import Base, SessionLocal, engine, get_db
from models import Order, Part

PENDING = "PENDING"
PROCESSING = "PROCESSING"
READY = "READY"
MACHINE_COUNT = 3
PROCESSING_SECONDS = 5
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Order & Conveyor System")


@app.post("/parts", response_model=dto.PartOut, status_code=201)
def create_part(data: dto.PartCreate, db: Session = Depends(get_db)):
    if db.query(Part.id).filter(Part.name == data.name).first():
        raise HTTPException(status_code=409, detail="Part already exists")
    part = Part(**data.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@app.get("/parts", response_model=list[dto.PartOut])
def list_parts(db: Session = Depends(get_db)):
    return db.query(Part).order_by(Part.name).all()


@app.post("/orders", response_model=dto.OrderOut, status_code=201)
def create_order(data: dto.OrderCreate, db: Session = Depends(get_db)):
    if not db.query(Part.id).filter(Part.id == data.part_id).first():
        raise HTTPException(status_code=404, detail="Part not found")

    reserved = db.execute(
        update(Part)
        .where(Part.id == data.part_id, Part.quantity >= data.quantity)
        .values(quantity=Part.quantity - data.quantity)
    ).rowcount
    if not reserved:
        db.rollback()
        raise HTTPException(status_code=409, detail="Not enough stock")

    order = Order(part_id=data.part_id, quantity=data.quantity, status=PENDING)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@app.get("/orders", response_model=list[dto.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id.desc()).all()


def simulate_machine(order_id: int):
    time.sleep(PROCESSING_SECONDS)
    with SessionLocal() as db:
        db.execute(update(Order).where(Order.id == order_id).values(status=READY))
        db.commit()


@app.put("/orders/{order_id}/start", response_model=dto.OrderOut)
def start_order(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    machine = f"Machine-{order_id % MACHINE_COUNT + 1}"
    started = db.execute(
        update(Order)
        .where(Order.id == order_id, Order.status == PENDING)
        .values(status=PROCESSING, machine=machine)
    ).rowcount
    db.commit()

    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if not started:
        raise HTTPException(status_code=409, detail="Order already started")

    background_tasks.add_task(simulate_machine, order_id)
    return order


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")