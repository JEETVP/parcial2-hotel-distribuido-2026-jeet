# Integrantes de la pareja

> **Llenen este archivo antes de empezar a tocar código**. Es parte de la calificación (4 pts) y la base para evaluar el balance de trabajo entre los dos.

## Integrante 1

- **Nombre completo:Anton Betak Licea**
- **Matrícula:190071**
- **Correo:anton.betak@iberopuebla.mx**
- **Usuario de Git que va a usar para sus commits:antonbetak**

## Integrante 2

- **Nombre completo:Roberto Villegas Ojeda**
- **Matrícula:190013**
- **Correo:190013@iberopuebla.mx**
- **Usuario de Git que va a usar para sus commits:JEETVP**

---

## División inicial del trabajo

> Antes de empezar, acuerden quién va a tomar qué. Pueden dividir por servicio, por tier, por bug, o como les acomode. Si después cambian, actualicen la tabla.

| Bug / Tarea | Responsable principal | Apoyo |
|---|---|---|
| B1 — routing key en booking-api |Anton | Roberto|
| B2 — manejo de error en publish |Roberto | Anton|
| B3 — auto_ack en availability-service |Anton |Roberto |
| B4 — overlap de fechas |Anton |
| B5 — race condition con `with_for_update()` |Roberto |Anton|
| B6 — credenciales hardcodeadas |Roberto |Anton |
| B7 — idempotencia en payment-service |Anton |Roberto |
| `notification-service` (TODOs) |Roberto |Anton |
| `notification-service` en docker-compose |Roberto |Anton |
| Capturas de RabbitMQ |Roberto |Anton |
| Logs end-to-end |Anton| |
| `DECISIONES.md` |Anton | |
| `PROMPTS.md` |Anton | |
| (otro) | | |
Bonus: 
Saga compensatoria: Roberto
Tests, observabilidad, mejoras: Anton


---

## Resumen final del trabajo

> Llenen esto al terminar. Una o dos frases por integrante explicando qué cosas hicieron principalmente. La idea no es competir, es que quede claro que ambos participaron.

### Lo que hizo Integrante 1
Se corrigieron bugs importantes en booking-api con su key, availability-service ahora valida correctamente la disponibilidad, payment-service evita la duplicación de cobros, se documentaron decisiones y logs para un mejor entendimiento del programa y a su vez se hizo un bonus con "test" el cual ayuda a probar y ahorrar tiempo


### Lo que hizo Integrante 2


---

## Notas sobre el trabajo en pareja

(Opcional) ¿Hubo algo difícil de coordinar? ¿Mejoras al flujo de trabajo en pareja para la próxima vez?

-Todo muy bien, sentimos que tenemos muy buena coordinación como pareja ya que hemos trabajado anteriormente en otros proyectos tanto escolares como personales, entonces para nosotros no hubo ningun tipo de problema, unicamente en los tiempos, ya que cuando trabajamos cada quien por su cuenta evitamos hacer push para evitar errores de merge. 
