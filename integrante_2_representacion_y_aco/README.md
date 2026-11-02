# Integrante 2 — Representación de soluciones y colonia de hormigas

Tu trabajo tiene dos partes: investigar un tema general de la práctica y estudiar un algoritmo. Primero comprende el tema general y después relaciónalo con el algoritmo. Al finalizar, comparte tu explicación con el equipo. Todos deben comprender los fundamentos, aunque cada persona coordine un tema distinto.

## 1 Tema general que debes investigar

**Representación del espacio de búsqueda**

- Cómo guardar un grafo mediante una matriz o una lista de conexiones; ventajas y limitaciones.
- Cómo representar una ruta mediante una permutación, es decir, un orden de los vértices sin repetirlos.
- Por qué una permutación sin repeticiones puede fallar si faltan conexiones o no se puede regresar al inicio.
- Cómo evitar, corregir o evaluar rutas que no cumplen todas las reglas.

## 2 Algoritmo que debes investigar

**Colonia de hormigas (ACO)**

- Cómo las hormigas construyen rutas y eligen el siguiente vértice sin repetir visitas.
- Qué representan las feromonas y cómo se refuerzan y evaporan.
- Qué información del grafo puede ayudar a elegir el siguiente paso.
- Qué sucede si una ruta no puede continuar o si visita todos los vértices pero no logra cerrar el ciclo.

## 3 Qué debes subir

Sube en esta misma carpeta un documento llamado `investigacion.pdf` con:

1. Una explicación del tema general y del algoritmo, con palabras propias y términos definidos.
2. Un ejemplo de cinco a ocho vértices que muestre pasos del método y cómo comprobar la ruta, incluido el regreso al inicio.
3. Una lista ordenada de los pasos del algoritmo, llamada pseudocódigo, y una explicación de sus ajustes principales.
4. Las opciones para aplicarlo al ciclo hamiltoniano, sus dificultades y las dudas pendientes.
5. Las fuentes que consultaste: autor, título, año y enlace, indicando qué información respalda cada una.

Por ahora se entrega investigación, no un programa completo. No es necesario elegir lenguaje ni herramientas. Usa artículos o libros confiables y revisa la práctica original. Los ejemplos son didácticos; no los presentes como resultados experimentales del FHCP.

## 4 Prompt de apoyo

Copia este texto en Codex u otro asistente. Adjunta la práctica si la tienes disponible.

```text
Estoy comenzando una práctica sobre el ciclo hamiltoniano y tengo pocos conocimientos previos. Lee este README. Debo investigar dos temas: Representación del espacio de búsqueda y Colonia de hormigas (ACO).

Ayúdame a comprender todos los puntos de las secciones 1 y 2, primero el tema general y después el algoritmo. Explica los términos con español neutral y ejemplos sencillos. Distingue los requisitos de la práctica de las propuestas para organizar el trabajo.

Consulta artículos originales, libros o fuentes académicas. Indica qué fuente respalda cada explicación. No inventes referencias; si no puedes consultarlas, señálalas como pendientes de verificación.

Trabajemos por etapas. Comienza con los fundamentos y hazme hasta tres preguntas para comprobar que entendí. Espera mis respuestas antes de avanzar. Después ayúdame con un ejemplo pequeño, el pseudocódigo y la organización del documento de la sección 3.

No elijas tecnologías ni escribas todavía el programa completo. No inventes mis respuestas ni resultados de pruebas. Distingue lo respaldado por fuentes, las opciones propuestas y las dudas que debemos resolver con el profesor.
```
