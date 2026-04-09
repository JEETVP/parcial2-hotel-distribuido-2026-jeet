"""availability-service - consumer que valida disponibilidad y crea reservas."""

import json
import logging
import os
from datetime import date

import pika

from .db import SessionLocal, init_db
from .models import Booking, Room

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("availability-service")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def find_available_room(session, room_type: str, check_in: date, check_out: date) -> Room | None:
    """Busca una habitacion del tipo solicitado libre en el rango dado.

    Devuelve la primera habitacion disponible o None si ninguna lo esta.
    """
    candidates = (
        session.query(Room)
        .filter(Room.room_type == room_type)
        .with_for_update()
        .all()
    )
    for room in candidates:
        conflicts = (
            session.query(Booking)
            .filter(
                Booking.room_id == room.id,
                Booking.status == "CONFIRMED",
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
            .with_for_update()
            .all()
        )
        if not conflicts:
            return room
    return None


def process_booking(payload: dict) -> tuple[bool, str, int | None]:
    booking_id = payload["booking_id"]
    room_type = payload["room_type"]
    check_in = date.fromisoformat(payload["check_in"])
    check_out = date.fromisoformat(payload["check_out"])

    with SessionLocal() as session:
        room = find_available_room(session, room_type, check_in, check_out)
        if room is None:
            logger.info("Reserva %s rechazada: sin habitaciones %s", booking_id, room_type)
            return False, f"No hay habitaciones {room_type} disponibles", None

        booking = Booking(
            booking_id=booking_id,
            room_id=room.id,
            guest=payload["guest"],
            check_in=check_in,
            check_out=check_out,
            status="CONFIRMED",
        )
        session.add(booking)
        session.commit()
        logger.info("Reserva %s confirmada en habitacion %s", booking_id, room.room_number)
        return True, "", room.id


def cancel_booking(payload: dict) -> None:
    with SessionLocal() as session:
        booking = session.query(Booking).filter(Booking.booking_id == payload["booking_id"]).first()
        if booking and booking.status != "CANCELLED":
            booking.status = "CANCELLED"
            session.commit()
            logger.info("Reserva %s cancelada y habitacion liberada", payload["booking_id"])


def callback(ch, method, properties, body):
    payload = json.loads(body)
    booking_id = payload["booking_id"]
    logger.info("Recibido %s: %s", method.routing_key, booking_id)

    try:
        if method.routing_key == "booking.cancelled":
            cancel_booking(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        success, reason, room_id = process_booking(payload)
        if success:
            event = {**payload, "event": "BOOKING_CONFIRMED", "room_id": room_id}
            routing_key = "booking.confirmed"
        else:
            event = {**payload, "event": "BOOKING_REJECTED", "reason": reason}
            routing_key = "booking.rejected"

        ch.basic_publish(
            exchange="hotel",
            routing_key=routing_key,
            body=json.dumps(event).encode(),
            properties=pika.BasicProperties(content_type="application/json"),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Publicado %s para %s", routing_key, booking_id)
    except Exception as exc:
        logger.error("Error procesando %s: %s", booking_id, exc)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main() -> None:
    init_db()
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange="hotel", exchange_type="topic")
    result = channel.queue_declare(queue="availability.requests", durable=False)
    channel.queue_bind(exchange="hotel", queue=result.method.queue, routing_key="booking.requested")
    channel.queue_bind(exchange="hotel", queue=result.method.queue, routing_key="booking.cancelled")

    channel.basic_consume(
        queue=result.method.queue,
        on_message_callback=callback,
        auto_ack=False,
    )
    logger.info("availability-service esperando booking.requested y booking.cancelled...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
