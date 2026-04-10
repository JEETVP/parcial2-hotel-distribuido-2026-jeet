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

Qué encontré:
Las credenciales estaban expuestas en la database_url, por lo que no se pueden cambiar sin modificar el codigo y estan harcodeadadas

Cómo lo arregle:
Los valores ahora al tenerlos cómo variables string separadas provienen desde el entorno, permitiendo qué puedan ser configurables, y escalables en diferentes de entornos de producción, pudiendo obtener los valores de otros envs qué pueden ser protegidos con un gitignore.

Por qué esto era un problema:
Es un problema por qué al tener la URL de base de datos, se puede generar acceso a información sensible, y podría haber robo o borrado de información, generando riesgos de mal uso del sistema.


## notification-service completado

En docker-compose.yml el notification service no aparecia declarado, por lo que no puede funcionar con Docker.

**Cómo los implementé:**
Reutilice la arquitectura de availability service, solo que como notificatio-service no utiliza base de datos no se coloca en el servicio.
**Decisiones de diseño que tomé:**
Es un problema por que no encontraría el host, no aparecería la conexión y rompería el flujo de la aplicación
## Bugs arreglados (Tier 2)

### B4 — Overlap de fechas
Qué encontré:
Encontramos que availability-service no detectaba correctamente cuando dos reservas se traslapaban en sus fechas

Cómo lo arregle:
Se corrigió la consulta para validar el solapamiento usando la condición completa entre check in y check out

Por qué esto era un problema:
Porque el sistema podia aceptar 2 reservas para la misma habitación en fechas que se encimaban


### B5 — Race condition con `with_for_update()`

Qué encontré:

El codigo realizaba dos sesiones distintas para acceder a la base de datos, por lo qué la validación de disponibilidad y la inserción a base de datos no estarían protegidos y fallarían haciendo qué varios puedan ver un falso disponible en una habitación en caso de qué haya accesos concurrentes.

Cómo lo arreglé:
Unificamos las dos sesiones para tener el SELECT e INSERT en una sola, y añadimos el with_for_update para bloquear hasta que se complete la transacción, haciendo que el acceso sea serializado para reservas existentes validando con las que esten disponibles al mismo tiempo. También incluye reintentos y muestra trazabilidad con exepción que genera el reintento, mandando el ACK hasta después de publicar.

Por qué esto era un problema:
Era un problema por que la operación no estaba contenida en una sola, y no protegía los datos al momento de insertarlos, lo que generaba que al haber procesos concurrentes, se pudieran crear reservas duplicadas.


### B7 — Idempotencia

Qué encontré:
Encontramos que payment-service podia procesar dos veces el mismo evento y generar cobros duplicados

Cómo lo arregle:
Se agregó un registro de eventos procesados para que se detecten antes de ser cobrados 

Por qué esto era un problema:
Porque si se reenviaba un mensaje, el sistema podia cobrar más de una vez la misma reserva

---

## Bonus que implementé (si aplica)
SAGA COMPENSATORIA

QUE ENCONTRE:
En availability-service, no podíamos revertir o cancelar cuando teníamos una reserva ya creada
En payment-service como solo había una routing key, solo se podía construir el evento de éxito o fallo en el pago.

QUE HICE:
En availability-service, añadimos la función cancel_booking en la cual en una sesión de base de datos, se realiza una query, en la que si muestra un estado diferente a cancelado, automáticamente cambia el status a cancelado, ahora puede revisar con el callback que tipo de evento esta procesando, reserva o cancelación, por lo que si recibe la routing key de booking.cancelled la manda como cancelación.Para esto fue necesaria añadir otro binding para escuchar en ambos casos

En payment-service, si el caso entra en el if not success, se añade la routing key de booking cancelled, y se devuleve un json con el evento de BOOKING_CANCELLED

POR QUE ERA UN PROBLEMA:

No es un problema, pero limita la experiencia del usuario a solo una opción, y no es tolerante a errores que pueda cometer, por lo que poder revertir el proceso representa un plus en caso de que haya un error. Y en el pago, permite que la reserva pase a cancelada y no solo avise si el pago paso o no, permitiendo una funcionalidad mas completa.

## Bonus pytest
Que encontré: 
Encontramos que no habia pruebas automaticas para validar la logica del overlap de fechas en availability-service

Como se arregló:
Se agregó un test con pytest para comprobar distintos casos de solapamiento entre reservs

por que es un problema: 
porque sin una prueba automatica era más fácil que esa logica se rompiera sin darnos cuenta



## Cosas que decidí NO hacer

Se trató de hacer todo lo que está en instrucciones, gracias a nuestra organización el tiempo no fue problema para nosotros.
---

## Si tuviera más tiempo, lo siguiente que mejoraría sería:

Si tuviera más tiempo, ademas de mejorar con más pytest en el sistema, agregaria una interfaz web sencilla para consultar el estado de las reservas sin depender de curl o de los logs y hacer más facil la interacción tanto para el cliente como para el programador. 
