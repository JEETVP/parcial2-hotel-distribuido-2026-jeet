# Evidencia esperada

Suban aquí los siguientes archivos. Sin esta evidencia se pierden puntos de la sección de evidencia.

## Obligatorios

### 1. Capturas del Management UI de RabbitMQ
(`http://localhost:15672`, usuario: guest, password: guest)

- `rabbitmq-exchanges.png` — captura de la pestaña Exchanges mostrando el exchange `hotel`
- `rabbitmq-queues.png` — captura de la pestaña Queues mostrando las queues que su sistema creó (availability.requests, payment.requests, notifications)
- `rabbitmq-bindings.png` — captura de los bindings de la queue `notifications` (debe mostrar los dos routing keys: `payment.completed` y `payment.failed`)

### 2. Logs del flujo end-to-end exitoso
- `flujo-completo.log` — salida de `docker compose logs` al hacer un `POST /bookings`, mostrando los 4 servicios procesando en cadena
- `servicios.png` — captura del flujo completo entre `booking-api`, `availability-service`, `payment-service` y `notification-service`

![Flujo end-to-end](./servicios.png)


### 3. Ejemplo de curl
- `curl.png` — captura del `curl` usado para crear una reserva de prueba
- `ps.png` — captura de `docker compose ps` mostrando los servicios levantados correctamente

![Curl de prueba](./curl.png)

![Servicios levantados](./ps.png)


## Opcionales (suman si están)

- `tests-output.txt` — salida de pytest si agregaron tests
- `concurrency-test.log` — evidencia de que arreglaron la race condition (B5): dos curl simultáneos y solo uno pasa
- `notas.md` — cualquier nota adicional sobre el proceso

## Cómo capturar logs

```bash
# Levanta todo
docker compose up --build -d

# En otra terminal, sigue los logs
docker compose logs -f > evidence/flujo-completo.log

# En otra más, dispara el flujo
curl -X POST http://localhost:8000/bookings \
  -H "Content-Type: application/json" \
  -d '{"guest": "Test", "room_type": "double", "check_in": "2026-05-01", "check_out": "2026-05-05"}'
```
