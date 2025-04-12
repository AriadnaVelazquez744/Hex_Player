# Hex_Player
  
---

## Estrategia del Agente de IA para Hex

Este agente implementa una estrategia avanzada basada en el algoritmo **Minimax con poda Alfa-Beta**, optimizada para el juego Hex mediante técnicas de **búsqueda iterativa en profundidad (Iterative Deepening)** y heurísticas especializadas. A continuación, se detallan los componentes clave:

---

### 🔍 Algoritmo Principal: **Minimax con Poda Alfa-Beta**
- **Objetivo:** Encontrar la jugada óptima considerando las posibles respuestas del oponente.
- **Profundidad Adaptativa:** 
- Usa **Iterative Deepening** para aumentar gradualmente la profundidad de búsqueda (`max_depth`).
- Se detiene automáticamente si se agota el tiempo límite (`time_limit`), retornando el mejor movimiento encontrado hasta ese momento.
- **Optimización:** 
- Poda Alfa-Beta para descartar ramas del árbol de búsqueda que no afectarán la decisión final.
- Ordenamiento dinámico de movimientos para maximizar la eficiencia de la poda.

---

### 🧠 Heurísticas Clave
#### 1. **Detección de Amenazas Inmediatas**
- Bloquea jugadas que permitirían al oponente ganar en el siguiente turno.
- Solo revisa si existen movimientos que hagan ganar al contrincante en caso de este ya haya colocado una cantida mayor o igual al tamaño del tablero menos 1 para evitar cálculos innecesarios.

#### 2. **Evaluación Estratégica del Tablero**
- **Dirección Estratégica:** 
    - Jugador 1 (🔴): Prioriza conectar bordes izquierdo y derecho.
    - Jugador 2 (🔵): Prioriza conectar bordes superior e inferior.
    - Calcula puntuaciones basadas en la proximidad a estos objetivos (`strategic_direction()`).
- **Puentes entre Grupos:** 
    - Recompensa movimientos que conectan grupos desconectados (`detectar_puentes()`).
    - Aumenta esta recompensa en caso de que se esté conectando al grupo con uno de los bordes objetivo.
- **Expansión No Lineal:** 
    - Detecta patrones en forma de diamante para controlar áreas centrales (`convolve2d`).

#### 3. **Cálculo de Fronteras Activas**
- Valora las casillas vacías adyacentes a fichas propias, incentivando la expansión controlada.

---

### ⚙️ Optimizaciones Técnicas
- **Estructuras de Datos Eficientes:**
- Uso de `DisjointSet` (de `scipy.cluster.hierarchy`) para trackear conexiones entre fichas en tiempo constante.
- Clonación rápida de tableros y estructuras durante la simulación de movimientos.
- **Ordenamiento de Movimientos:**
- Precalcula puntuaciones heurísticas para explorar primero los movimientos más prometedores.
- **Manejo de Tiempo:**
- Verificación del tiempo en cada iteración para garantizar respuestas dentro del límite especificado.

---

### 🎯 Estrategia de Apertura
- **Primera Jugada:** 
- Jugador 1: Centro del borde izquierdo, centro absoluto, o centro del borde derecho.
- Jugador 2: Centro del borde superior, centro absoluto, o centro del borde inferior.
- Implementado en `elegir_apertura()`.

---

### 📊 Métricas de Rendimiento
```python
Evaluación Total = 
(Dirección Estratégica × 0.5) + 
(Puentes × 0.3) + 
(Fronteras × 0.05) + 
(Expansión × 0.25)
```

---

### 🔄 Flujo de Decisión
- **Verificar Amenazas**: Bloquear victorias inminentes del oponente.
- **Búsqueda Iterativa**: Ejecutar Minimax con profundidad creciente.
- **Evaluar Movimientos**: Usar heurísticas para simular y puntuar jugadas.
- **Seleccionar Mejor Opción**: Retornar la jugada con mayor puntuación heurística.
