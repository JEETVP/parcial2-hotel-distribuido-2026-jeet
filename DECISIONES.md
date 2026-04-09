# Decisiones técnicas

> Documenten brevemente las decisiones que tomaron resolviendo el examen. No copien del enunciado: expliquen con sus palabras qué hicieron y por qué. La intención es que al revisar pueda entender el razonamiento, no que repitan el problema.

---

## Bugs arreglados (Tier 1)

### B1 — Routing key
Encontramos que el booking-api enviaba la reserva con un nombre de ruta incorrecto

cambie la ruta, en vez de "booking 
.create" pusimos "booking.requested"

Era un problema por que availability-service no recibia el mensaje y no procesaba la reserva

---

### B2 — Manejo de error en publish

Qué encontré:

El codigo mandaba falsos positivos por qué incluia manejos de errores, ya qué la publicación en RabbitMQ podría fallar pero el usuario aún así iba a recibir un 202, por lo qué ni siquiera contaba con un log qué mostrara el error, no contando con trazabilidad.

Cómo lo arreglé:
Incorporamos una estructura con try/except en la cual gestionamos primero qué se haga la publicación en redis, y la construcción del payload para mandarlo a rabbitMQ.Luego, ya qué se vaya a hacer la publicación, dentro del try ponemos:await publish_booking(payload) para qué intente publicar en Redis, si no puede manda error a los logs con logger de 503,  y en caso de qué logre la publicación manda un bookingcreated. Finalmente cerramos redis para no dejar recursos abiertos.

Por qué esto era un problema:
Es un error por qué al generar falsos positivos, un usuario intentando hacer una reserva podría creer qué si esta guardando un cambio, cuando ningún microservicio va a procesar su reserva, y no va a persistir su información en RabbitMQ ni en las etapas posteriores.


### B3 — Ack manual
Encontramos que availability-service confirmaba el mensaje demasiado pronto y podia perderlo si fallaba

Se solucionó cambiando el consumer a confirmación manual usando auto_ack=false y haciendo ack solo al terminar bien

Era un problema porque si el servicio fallaba mientras procesaba, el mensaje ya estaba marcado como recibido y se perdia

---

### B6 — Credenciales en env vars

---

## notification-service completado

**Qué TODOs había:**

**Cómo los implementé:**

**Decisiones de diseño que tomé:**

---

## Bugs arreglados (Tier 2)

### B4 — Overlap de fechas

### B5 — Race condition con `with_for_update()`

### B7 — Idempotencia

---

## Bonus que implementé (si aplica)

---

## Cosas que decidí NO hacer

(Ej: "no agregué tests porque preferí enfocarme en el flujo end-to-end", "no implementé saga porque no me dio tiempo", etc.)

---

## Si tuviera más tiempo, lo siguiente que mejoraría sería:
