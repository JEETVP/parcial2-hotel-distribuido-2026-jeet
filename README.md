# HotelBook — Sistema Distribuido de Reservas

> **Examen Parcial 2 — Sistemas Distribuidos**
> Primavera 2026

## Bienvenida

¡Bienvenidos al equipo de **HotelBook**! Acaban de incorporarse como **desarrolladores junior**. El equipo anterior dejó el sistema con varios bugs, mensajería mal configurada, una race condition, falta de idempotencia y un servicio sin terminar.

Su trabajo durante las próximas horas: **diagnosticar, arreglar y completar** el sistema, y entregar evidencia de que funciona end-to-end.

Antes de empezar, **lean `INSTRUCCIONES.md`**. Ahí está la lista completa de tareas, divididas en tiers, con pistas claras sobre dónde buscar.

## Trabajo en parejas

Este examen se entrega **en parejas (2 personas)**. Antes de empezar a tocar código:

1. Llenen `INTEGRANTES.md` con sus nombres completos, matrículas y correos.
2. Acuerden cómo se van a dividir el trabajo (por servicio, por tier, por tipo de bug, como prefieran).
3. Vayan documentando en `INTEGRANTES.md` qué hizo cada quien — esto es parte de la calificación.
4. **Ambos integrantes deben hacer commits con su propio usuario de Git**. Una entrega donde el 100% de los commits son de una sola persona pierde puntos.

## Arquitectura actual (rota)

```
                            ┌─────────────────┐
              ┌────────────►│  Postgres       │
              │             │  hotel_db       │
              │             └─────────────────┘
              │
┌─────────────┴─┐    booking.requested    ┌────────────────────┐
│  booking-api  │────────────────────────►│ availability-svc   │
│  (FastAPI)    │      RabbitMQ topic     │  (pika sync)       │
└───────────────┘       exchange          └─────────┬──────────┘
       │                                            │ booking.confirmed
       │                                            │ booking.rejected
       │                                            ▼
       │                                  ┌────────────────────┐
       │                                  │  payment-service   │
       │                                  │   (aio-pika)       │
       │                                  └─────────┬──────────┘
       │                                            │ payment.completed
       │                                            │ payment.failed
       │                                            ▼
       │                                  ┌────────────────────┐
       │                                  │ notification-svc   │
       │                                  │   (NO EXISTE AÚN)  │
       │                                  └────────────────────┘
       │
       ▼
   Redis (estado de la reserva)
```

Ver diagramas Mermaid en `docs/arquitectura-actual.md` y `docs/arquitectura-objetivo.md`.

## Stack

- **Python 3.12**
- **FastAPI** + **aio-pika** (booking-api)
- **pika** sync (availability-service)
- **aio-pika** (payment-service)
- **pika** (notification-service skeleton)
- **PostgreSQL 16** + SQLAlchemy
- **Redis 7**
- **RabbitMQ 3** (con management plugin)
- **Docker Compose**

## Cómo correrlo

```bash
# 1. Copia las variables de entorno
cp .env.example .env

# 2. Levanta todo
docker compose up --build

# 3. (En otra terminal) prueba el endpoint
curl -X POST http://localhost:8000/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "guest": "Ana López",
    "room_type": "double",
    "check_in": "2026-05-01",
    "check_out": "2026-05-05"
  }'
```

UI de RabbitMQ en `http://localhost:15672` (usuario: `guest`, password: `guest`).

## Bonus y validacion

Se agregaron tests con `pytest`  para validar de forma aislada sin depender del broker o de la base de datos.

Para correrlos:

```bash
python -m pytest availability-service/tests
```

## ¿Por dónde empiezan?

1. Lean este archivo (ya lo están haciendo, ¡bien!)
2. **Llenen `INTEGRANTES.md`** antes de cualquier otra cosa
3. **Lean `INSTRUCCIONES.md` completo**
4. Levanten el sistema con `docker compose up --build`
5. Hagan un POST de prueba con curl y observen qué pasa (o qué NO pasa)
6. Ataquen **Tier 1** primero — son bugs con pistas claras
7. Pasen a **Tier 2** cuando todo lo de Tier 1 funcione
8. Si les queda tiempo, **Tier 3** para puntos bonus
9. Llenen `evidence/`, `PROMPTS.md`, `DECISIONES.md`, `INTEGRANTES.md`
10. Push final + suban el link de su fork a Moodle

## Reglas

- **Hacer fork público** del repositorio del examen
- **Commits frecuentes y descriptivos** (no `wip`, no `fix`, no `cambios`)
- **Ambos integrantes** deben hacer commits con su propia identidad de Git
- Si usan IA (Claude/ChatGPT/Copilot): **deben declararlo en `PROMPTS.md`**. No hacerlo y que se detecte = penalización
- **No copiar** entre parejas distintas (los commits dejan rastro)
- Entrega: **link del fork público en Moodle antes del jueves 23:59**

## Calificación

Ver `RUBRICA.md`. Resumen:

- **70 pts** — Código (Tier 1: 45, Tier 2: 20, Tier 3 bonus: 5)
- **30 pts** — Commits + evidencia + INTEGRANTES.md + DECISIONES.md + PROMPTS.md

¡Mucho éxito! El examen está calibrado para que con esfuerzo razonable la pareja saque una buena nota.
