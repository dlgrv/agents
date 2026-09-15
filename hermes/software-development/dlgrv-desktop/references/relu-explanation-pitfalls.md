# ReLU explanation pitfalls (dlgrv.com blog clarity)

## New pitfalls (2026-09)

### 1. Never explain ReLU via geometry or graphs

- **User feedback:** «стало еще более непонятно» when comparing «изгиб»/«ломание» lines
- **Correct approach:** Explain as a simple condition: «Если итоговое число меньше нуля — нейрон возвращает ноль, как будто передумал говорить. Если ноль или больше — возвращает это число как есть»
- **Why:** Geometry analogies confuse readers; numbers and conditions are more accessible
- **Example:** −2 → 0, 3 → 3

### 2. Never use «изгиб» or «ломание» for ReLU

- **User feedback:** Explicit rejection of geometric metaphors
- **Correct terms:** «проверка»/«условие»
- **Avoid:** «изгиб», «ломание», «прямая линия», «график», «уголок»

### 3. Always show concrete numbers for layer stacking

- **Problem:** Abstract «стопка становится стопкой» is unclear
- **Solution:** Show actual computation chain
  - Input: 5
  - Layer 1: ×2 → 10
  - Layer 2: ×2 → 20
  - Layer 3: ×2 → 40
  - Same result as one layer: ×8 → 40 ($5×8=40$)
- **Why this proves the need for ReLU:** Without the «меньше нуля?» condition, multiple layers don't add new behavior

### 4. Always connect ReLU to layer uniqueness

- **Mechanism:** The «меньше нуля?» condition selectively silences neurons
- **Effect:** Each layer becomes unique because different neurons get silenced
- **Result:** Stack cannot be collapsed into one layer

## Template for ReLU explanation

> У нейрона есть ещё одно свойство, о котором мы молчали: он не просто умножает числа на веса и складывает — у него есть **условие**. Если итоговое число меньше нуля — нейрон возвращает ноль, как будто передумал говорить. Если ноль или больше — возвращает это число как есть. Например: нейрон посчитал **−2** — вернул **0**, «молчит»; сосед посчитал **3** — вернул **3**, передал дальше без изменений.
>
> Это правило называется **ReLU**. Зачем оно? Без него десятки слоёв схлопывались бы в один: умножай-и-складывай — это всегда одна и та же операция, и сколько её ни повторяй, результат тот же. Пример: три слоя подряд умножают на 2, вход был 5 — первый слой выдал 10, второй 20, третий 40. Те же 40 получаются одним умножением на 8: $5×8=40$. Никакого нового поведения от глубины не появляется.
>
> А теперь верни ReLU. На каждом этаже часть нейронов посчитала минус — и вернула ноль, замолчала. С каждым слоем молчит всё больше нейронов, и картина «кто говорит, кто молчит» с каждым слоем меняется. Это уже нельзя посчитать в один присест: чтобы узнать, что выдаст третий слой, надо пройти первый, потом второй, потом третий — на каждом этаже часть сигналов гаснет. Глубина начинает значить что-то новое: этажи не складываются в один, а достраивают друг друга.

## Pitfall checklist

When writing about ReLU, check:

- [ ] No geometry/graph terms («изгиб», «ломание», «прямая», «график»)
- [ ] Uses «условие» instead of geometric metaphors
- [ ] Has concrete number examples (input → layer1 → layer2 → layer3)
- [ ] Shows equivalent single-layer computation ($input×multiplier$)
- [ ] Explains how ReLU breaks the equivalence
- [ ] Connects ReLU to neuron silencing and layer uniqueness

## References

- Main article: `/public/blog/how-llm-works/index.md`
- Build script: `scripts/build-blog-pages.mjs`
- Preview server: `npx vite --port 5175 --strictPort`