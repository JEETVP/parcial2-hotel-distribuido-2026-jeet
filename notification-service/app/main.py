"""notification-service – consumer que loggea notificaciones de pago.

ESTE SERVICIO ESTÁ INCOMPLETO. Tu trabajo es resolver los TODOs de abajo.

El servicio debe consumir eventos `payment.completed` y `payment.failed` del
exchange `hotel`, y por cada uno loggear de forma estructurada el "envío" de
la notificación. No se manda email real: solo se loggea con un formato
específico que se evalúa.

Formato del log esperado:
[NOTIFICATION] booking_id=<id> event=PAYMENT_COMPLETED guest=<name> channel=email status=SENT

Pista: copia el patrón de availability-service/app/main.py, pero adaptado a
los routing keys de pago. Usa ack manual.
"""

import json
import logging
import os

import pika

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("notification-service")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def callback(ch, method, properties, body):
    payload = json.loads(body)
    logger.info(
        "[NOTIFICATION] booking_id=%s event=%s guest=%s channel=email status=SENT",
        payload["booking_id"],
        payload["event"],
        payload["guest"],
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare(exchange="hotel", exchange_type="topic")
    result = channel.queue_declare(queue="notifications", durable=False)
    channel.queue_bind(exchange="hotel", queue=result.method.queue, routing_key="payment.completed")
    channel.queue_bind(exchange="hotel", queue=result.method.queue, routing_key="payment.failed")

    channel.basic_consume(
        queue=result.method.queue,
        on_message_callback=callback,
        auto_ack=False,
    )

    logger.info("notification-service esperando eventos de pago...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
