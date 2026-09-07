# Uso de Inteligencia Artificial

## 1. Herramientas utilizadas

* **Claude (Anthropic):** utilizado principalmente como tutor y asistente de desarrollo — explicación de conceptos nuevos (JWT, ORM, patrones de diseño), generación de fragmentos de código a partir de decisiones ya tomadas por el desarrollador, y apoyo en depuración de errores reales.

* **GitHub Copilot:** utilizado como asistente de programación dentro del entorno de desarrollo para revisión de código, detección de inconsistencias, análisis de estructura del proyecto, propuesta de organización de módulos e identificación de problemas en routers y relaciones entre componentes. También se utilizó para verificar cambios después de reconstruir y ejecutar el proyecto.

* **ChatGPT:** apoyo puntual en organización de documentación, explicación de conceptos y revisión de decisiones técnicas.

Es importante aclarar que la mayoría del código del proyecto **no fue copiado directamente de la IA sin revisión**: gran parte de los módulos fueron escritos por el desarrollador siguiendo patrones previamente explicados y entendidos. La IA se utilizó principalmente como acompañamiento para comprender el "por qué" de las decisiones, revisar implementaciones y diagnosticar errores.

---

## 2. Etapas de utilización y nivel de participación

| Etapa                              | Quién lo escribió                           | Rol de la IA                                                                           |
| ---------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------- |
| Diseño de base de datos            | Desarrollador, con validación de Claude     | Explicó trade-offs como ENUM vs. tabla aparte y normalización                          |
| CRUD de Productos/Sucursales       | Desarrollador                               | Sirvió como patrón inicial explicado; posteriormente el patrón se replicó              |
| CRUD de Usuarios                   | Desarrollador                               | Ayudó a revisar detalles puntuales                                                     |
| Autenticación (JWT)                | Desarrollador, siguiendo explicación guiada | Explicó el concepto de token/Bearer paso a paso                                        |
| Módulo de Inventario               | Desarrollador                               | Ayudó a diagnosticar errores reales y revisar lógica                                   |
| Módulo de Compras                  | Mixto                                       | El desarrollador construyó la lógica y la IA apoyó en revisión y corrección de errores |
| Módulo de Ventas                   | Mixto                                       | El desarrollador construyó la lógica; la IA ayudó a revisar seguridad y consistencia   |
| Módulo de Transferencias           | Desarrollador, con apoyo guiado             | Se aplicaron patrones aprendidos de Compras, Ventas e Inventario                       |
| Frontend (React)                   | Mixto                                       | Explicó conceptos nuevos y apoyó la revisión de componentes                            |
| Organización de arquitectura       | Mixto                                       | Se revisó la separación de modelos, schemas, routers y servicios                       |
| Revisión de seguridad y estructura | GitHub Copilot + desarrollador              | Segunda revisión independiente de routers, roles, imports y relaciones                 |

---

## 3. Prompts y decisiones representativas

### Caso 1 — Diagnóstico de un bug real

Al ejecutar el proyecto apareció el error:

> `psycopg2.errors.InvalidTextRepresentation: invalid input value for enum tipo_movimiento: "INGRESO_COMPRA"`

Se compartió el traceback con Claude para entender la causa. La IA explicó la diferencia entre el **nombre** de un atributo de `enum.Enum` en Python y su **valor** real, y propuso el uso de `values_callable`.

El desarrollador aplicó el mismo criterio al resto de los ENUM utilizados en el proyecto, anticipando problemas equivalentes.

### Caso 2 — Revisión de código ya escrito por el desarrollador

En el módulo de Compras, el desarrollador escribió primero su propio servicio y posteriormente lo compartió para revisión.

La IA identificó sobre ese código existente:

* valores de enum inexistentes;
* una llamada incorrecta a una función de inventario;
* lógica duplicada de costo promedio ponderado;
* diferencias entre la estructura del servicio y los modelos reales.

Las correcciones fueron aplicadas sobre la estructura ya escrita por el desarrollador, sin reemplazar el módulo completo por una solución generada desde cero.

### Caso 3 — El desarrollador detecta un riesgo de seguridad

Al construir el frontend de Ventas, el desarrollador identificó que la selección de sucursal se estaba resolviendo únicamente desde React y planteó el riesgo de seguridad antes de que la IA lo señalara.

La IA confirmó el problema y ayudó a establecer la regla de que la sucursal debía validarse y resolverse en el backend de acuerdo con el usuario autenticado y su rol.

### Caso 4 — Una sugerencia de la IA fue rechazada

En una revisión de Ventas, una sugerencia asumió que el modelo `Venta` tenía un atributo llamado `detalles`. Al revisar el `models.py` real se confirmó que la relación correcta era `detalles_venta`.

La sugerencia incorrecta fue descartada y el código se corrigió de acuerdo con la estructura real del proyecto.

### Caso 5 — Revisión estructural con GitHub Copilot

GitHub Copilot se utilizó posteriormente para realizar una revisión más amplia de la estructura del proyecto y detectar posibles inconsistencias.

A partir de esta revisión se realizaron y verificaron los siguientes cambios:

**a. Roles y autorización**

Además de las correcciones iniciales, se ajustaron los endpoints de consulta de compras, ventas y movimientos de inventario para respetar las reglas de acceso:

* `admin_general` puede consultar información de todas las sucursales.
* `gerente_sucursal` y `operador_inventario` quedan limitados a su propia sucursal.
* Los intentos de acceder a otra sucursal generan respuesta `403`.

**b. División de modelos**

El archivo monolítico de modelos fue dividido en módulos por dominio dentro del paquete `models`.

Se mantuvo un `__init__.py` para centralizar y reexportar los modelos, evitando modificar la forma en que el resto de la aplicación los importa.

Después del cambio se reconstruyó la imagen Docker del backend y se verificaron llamadas reales a:

* `GET /sucursales`
* `GET /productos`
* `GET /compras`
* `GET /ventas`

También se verificó que las relaciones entre entidades continuaran funcionando correctamente.

**c. Convención de nombres por capa**

Se adoptó la convención de sufijos por responsabilidad:

* `_schema`
* `_router`
* `_service`

Por ejemplo:

```text
schemas/compra_schema.py
routers/compra_router.py
services/compra_service.py
```

Esto mejora la identificación de archivos cuando existen varias capas con nombres de dominio iguales.

Después de los renombres se actualizaron los imports afectados y se realizó una nueva verificación del proyecto sin referencias rotas a los nombres anteriores.

**d. Verificación posterior**

Los cambios no se consideraron terminados únicamente por modificar archivos. Se reconstruyó el contenedor del backend y se ejecutaron pruebas reales contra la API para validar que la reorganización no hubiera introducido ciclos, imports rotos o errores de ejecución.

---

## 4. Validación humana

Cada sugerencia de IA se consideró únicamente una propuesta y fue contrastada con el código real del proyecto.

La validación incluyó:

* pruebas manuales mediante Swagger (`/docs`);
* pruebas desde el frontend;
* reconstrucción real de imágenes Docker cuando los cambios afectaban al backend;
* validación de respuestas HTTP y errores esperados;
* comprobación de permisos según rol;
* revisión de relaciones ORM;
* verificación de imports después de reorganizar archivos.

También se rechazaron sugerencias de IA cuando no coincidían con los modelos o decisiones reales del proyecto.

La organización final de la arquitectura fue decidida por el desarrollador y ajustada posteriormente con apoyo de las herramientas.

---

## 5. Evaluación crítica

### Qué aportó la IA

* Redujo el tiempo de diagnóstico de errores específicos de PostgreSQL, FastAPI y SQLAlchemy.
* Permitió revisar código ya escrito antes de integrarlo.
* Ayudó a detectar inconsistencias entre schemas, modelos, routers y servicios.
* Sirvió como segunda opinión sobre seguridad y autorización.
* Ayudó a comprender relaciones ORM con dos claves foráneas hacia la misma tabla.
* Permitió revisar la organización de la arquitectura y la separación por capas.
* GitHub Copilot aportó una segunda revisión independiente de la estructura y los permisos del sistema.

### Qué se hizo sin asistencia de IA o mediante decisiones propias

* Una parte importante del CRUD básico.
* La detección inicial del problema de autorización por sucursal.
* La corrección de sugerencias que no coincidían con los modelos reales.
* La elección final de la organización de módulos.
* La implementación y prueba de los cambios posteriores a las sugerencias.
* La decisión sobre qué funcionalidades realmente podían marcarse como implementadas.

### Dónde la IA no fue tan útil

Las sugerencias generadas sin conocer completamente el código real podían asumir nombres de atributos, relaciones o estructuras que no existían.

Por esta razón, se utilizó siempre el proyecto real como fuente definitiva y las propuestas de IA fueron verificadas antes de aplicarse.

---

## 6. Porcentaje estimado de participación de IA

Es difícil representar toda la participación mediante un único porcentaje porque la IA fue utilizada para diferentes tipos de tareas.

* **Explicación de conceptos y depuración:** participación alta de IA, aproximadamente 70%.
* **Código escrito directamente por el desarrollador después de comprender el patrón:** participación menor de IA.
* **Revisión y corrección de código ya existente:** participación intermedia y frecuente.
* **Organización y revisión estructural:** participación mixta entre desarrollador y herramientas de IA.

### Porcentaje global estimado

**Participación aproximada de IA en el desarrollo: 45%.**

Este valor representa principalmente asistencia en explicación, revisión, depuración y detección de errores, y **no significa que el 45% del sistema haya sido generado autónomamente por IA y pegado sin revisión**.

Una parte importante del código fue escrita directamente por el desarrollador, especialmente después de comprender los patrones utilizados.

---

## 7. Conclusión

La inteligencia artificial fue utilizada como una herramienta de acompañamiento durante el desarrollo de OptiPlant, principalmente para aprender conceptos, revisar código, diagnosticar errores y contrastar decisiones técnicas.

El desarrollador mantuvo el control sobre la implementación y validó las propuestas contra el código real, las pruebas de ejecución y los requerimientos de la evaluación.

Un aspecto especialmente relevante fue el uso de distintas herramientas con funciones complementarias: Claude como apoyo de aprendizaje y depuración, GitHub Copilot como segunda revisión de estructura y código, y ChatGPT como apoyo puntual de organización y documentación.

La experiencia permitió no solo resolver errores concretos, sino también mejorar progresivamente la separación entre **schemas, routers, services, modelos y autorización**, manteniendo la trazabilidad de las decisiones tomadas durante el desarrollo.
