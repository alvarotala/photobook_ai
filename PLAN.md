# Photobook AI — Plan de producto

## 1. Descripción general

**Photobook AI** es una experiencia fotográfica interactiva para eventos, presentada en un tótem vertical con cámara y pantalla táctil. La propuesta convierte a cada visitante en protagonista de una escena de rally mediante inteligencia artificial.

La persona elige una situación, se toma una fotografía y el sistema integra su rostro y apariencia en una composición previamente diseñada. Al finalizar, recibe una imagen cinematográfica lista para descargar mediante un código QR.

La experiencia debe sentirse como un juego breve, sorprendente y fácil de entender, sin requerir instrucciones de un operador.

## 2. Objetivo de la experiencia

- Crear un recuerdo personalizado y atractivo en pocos minutos.
- Acercar al visitante a la emoción del rally.
- Generar una experiencia compartible en redes sociales.
- Permitir que muchas personas participen de manera rápida y autónoma.
- Adaptar la ambientación, los colores y las escenas a cada evento o patrocinador.

## 3. Dinámica del juego

La experiencia se organiza en cuatro pasos:

### Paso 1 — Elegir una escena

La persona selecciona el tipo de fotografía que quiere protagonizar. Las opciones iniciales son:

1. **Dentro del auto:** el participante aparece como copiloto o acompañante dentro de un vehículo de rally.
2. **En el podio:** el participante aparece celebrando una victoria junto a pilotos ficticios.
3. **Hero pose:** el participante posa en primer plano, con un auto de rally y una ambientación cinematográfica de fondo.

En esta pantalla se muestran ilustraciones conceptuales que explican cada tipo de fotografía. No se muestran fotografías de participantes anteriores.

### Paso 2 — Tomar la fotografía

La cámara del tótem muestra una vista previa en vivo. Una guía ayuda a la persona a centrar correctamente su rostro.

Las instrucciones deben ser simples:

- Mirar al frente.
- Mantener el rostro dentro de la guía.
- Evitar gorras, lentes oscuros u objetos que oculten la cara.
- Mantener una expresión natural o sonreír.

Al presionar el botón de captura, se realiza una cuenta regresiva y se toma la fotografía.

### Paso 3 — Crear la composición

El sistema procesa la fotografía e integra a la persona en la plantilla seleccionada. Durante la espera, la pantalla muestra una animación y mensajes breves relacionados con el proceso, por ejemplo:

- Preparando tu escena.
- Ajustando iluminación y perspectiva.
- Integrándote en el mundo del rally.
- Aplicando el acabado cinematográfico.

El procesamiento debe conservar la identidad y los rasgos principales de la persona, adaptando vestuario, postura, iluminación y entorno a la escena elegida.

### Paso 4 — Ver y descargar el resultado

La composición final aparece en pantalla acompañada de un código QR. La persona escanea el código con su teléfono para abrir y descargar su fotografía.

Desde esta pantalla también puede:

- Repetir la fotografía si el resultado no es adecuado.
- Iniciar una experiencia nueva para el siguiente participante.
- Consultar un aviso breve sobre el tiempo disponible para descargar la imagen.

Cuando termina el tiempo de espera, el tótem vuelve automáticamente a la pantalla inicial.

## 4. Imágenes y plantillas

Las imágenes utilizadas como base de las composiciones serán proporcionadas por el responsable del proyecto.

Cada plantilla debe entregarse en alta resolución y, preferentemente, sin marcas comerciales no autorizadas. La escena puede incluir autos, indumentaria, cascos, podios, público, banderas y elementos de rally, siempre que exista permiso para utilizarlos.

Para cada plantilla se recomienda proporcionar:

- Imagen principal en alta resolución.
- Nombre y breve descripción de la escena.
- Zona aproximada donde aparecerá el participante.
- Posición y tamaño esperados del rostro o cuerpo.
- Referencia de postura y expresión.
- Indicación de vestuario deseado.
- Elementos que deben conservarse sin modificaciones.
- Logos o marcas autorizadas, si corresponde.
- Formato final requerido: vertical, horizontal o ambos.

Las personas adicionales que aparezcan en las composiciones deben ser personajes ficticios o modelos autorizados. No se utilizarán imágenes reales de pilotos conocidos sin autorización.

## 5. Lineamientos visuales

- Interfaz vertical optimizada para un tótem.
- Botones grandes y fáciles de tocar.
- Textos breves, claros y legibles a distancia.
- Estética deportiva y cinematográfica.
- Paleta oscura con acentos rojos, naranjas y azules.
- Sin marcas comerciales visibles, salvo aquellas expresamente autorizadas.
- Fotografías finales realistas, con iluminación, escala, sombras y perspectiva coherentes.
- Los pies, cuerpos, vehículos y objetos deben estar correctamente apoyados en la escena, sin sensación de estar flotando.

## 6. Requisitos funcionales

- Selección táctil de plantilla.
- Vista previa en vivo de la cámara.
- Guía de posicionamiento facial.
- Cuenta regresiva antes de la captura.
- Opción para repetir la fotografía.
- Procesamiento automático con IA.
- Indicador de progreso durante la espera.
- Generación de una imagen final en alta calidad.
- Creación de un enlace único y un código QR.
- Descarga desde teléfonos iOS y Android sin instalar una aplicación.
- Reinicio automático de la experiencia.
- Modo de recuperación ante errores de cámara, conexión o procesamiento.

## 7. Flujo alternativo y errores

El sistema debe contemplar los siguientes casos:

- **Rostro no detectado:** solicitar una nueva fotografía.
- **Más de un rostro:** indicar que debe participar una sola persona, salvo que la plantilla admita grupos.
- **Imagen movida u oscura:** recomendar repetir la captura.
- **Error de procesamiento:** ofrecer un nuevo intento sin reiniciar toda la experiencia.
- **Pérdida de conexión:** mostrar un mensaje simple y reintentar automáticamente.
- **QR vencido:** informar durante cuánto tiempo estará disponible la descarga.
- **Inactividad:** volver a la pantalla inicial luego de una cuenta regresiva visible.

## 8. Privacidad y consentimiento

Antes de tomar la fotografía, la interfaz debe informar de forma breve que la imagen será procesada con inteligencia artificial para generar la composición elegida.

Se recomienda:

- Solicitar aceptación antes de activar la captura.
- No utilizar las fotografías para otros fines sin consentimiento adicional.
- Definir un tiempo automático de eliminación de las imágenes originales y procesadas.
- No mostrar fotografías de participantes anteriores en la selección de plantillas.
- Proteger los enlaces de descarga mediante identificadores únicos difíciles de adivinar.
- Incluir condiciones especiales para menores de edad según el evento y la legislación aplicable.

## 9. Experiencia esperada

La interacción completa debería durar aproximadamente entre uno y tres minutos:

1. Selección de escena: 10 a 20 segundos.
2. Posicionamiento y captura: 15 a 30 segundos.
3. Procesamiento: idealmente menos de 60 segundos.
4. Vista previa y escaneo del QR: 20 a 40 segundos.

El objetivo es mantener una rotación rápida de participantes sin perder el efecto de sorpresa del resultado final.

## 10. Alcance del MVP

La primera versión funcional incluirá:

- Un tótem vertical.
- Tres plantillas: dentro del auto, podio y hero pose.
- Experiencia para una persona por sesión.
- Una captura por intento.
- Procesamiento de imagen con IA.
- Vista previa del resultado.
- Descarga mediante QR.
- Reinicio automático para el siguiente participante.

## 11. Evolución futura

Después de validar el MVP, se pueden incorporar:

- Nuevas escenas y disciplinas deportivas.
- Fotografías grupales.
- Elección de uniforme, número o colores.
- Diferentes expresiones o poses.
- Video corto o animación del resultado.
- Envío por correo o mensajería.
- Galería moderada del evento.
- Métricas de participación y descargas.
- Personalización por patrocinador, sede o campeonato.

## 12. Indicadores de éxito

- Cantidad de experiencias completadas.
- Porcentaje de fotografías descargadas.
- Tiempo promedio por participante.
- Porcentaje de capturas repetidas.
- Tasa de errores de procesamiento.
- Cantidad de imágenes compartidas, cuando sea medible y exista consentimiento.
- Satisfacción de los participantes y organizadores.

## 13. Entregables necesarios para comenzar

- Las tres imágenes de plantilla definitivas.
- Identidad visual del evento o del producto.
- Resolución y medidas exactas de la pantalla del tótem.
- Características de la cámara y la iluminación disponible.
- Textos legales y política de privacidad.
- Duración deseada de los enlaces de descarga.
- Reglas sobre logos, marcas y banderas permitidas.
- Ejemplos aprobados del estilo visual esperado.

---

**Resumen:** Photobook AI transforma una fotografía tomada en el evento en una escena personalizada de rally. La experiencia combina selección de escenario, captura guiada, composición con IA y descarga inmediata mediante QR, dentro de un flujo breve diseñado para un tótem táctil.
