# Sidebar UI Capitalization Reference

## Purpose

This reference documents capitalization and layout rules for Russian web interface sidebar filters to ensure consistent presentation and proper rendering on mobile devices.

## Rules

### Chip Label Capitalization

All filter chips must start with a capital letter:
- **Benefit chips**: Очень высокая, Высокая, Обычная
- **Category chips**: Жизнь, Деньги, Время и силы, Свобода
- **Evidence chips**: Уровень A, Уровень B, Уровень C
- **Money chips**: Бесплатно, Мало, Много
- **Time chips**: На бегу, Несколько часов, Каждый день
- **Willpower chips**: Не нужна, Немного, Сильно

### Money Chip Special Case

Chinese-derived chips (少/多) must be translated to Russian with capitalization:
- `data-v="少"` → visible text "Мало"
- `data-v="多"` → visible text "Много"
- **Never change `data-v` attributes** — these are internal filter keys

### Card Badge Capitalization

Values in the LABEL map must be capitalized:
- `money: {'0': 'Бесплатно', '少': 'Небольшие траты', '多': 'Заметные траты'}`
- `time: {'少': 'На бегу', '中': 'Несколько часов', '多': 'Каждый день'}`
- `will: {'否': 'Без силы воли', '些': 'Немного усилий', '是': 'Серьёзные усилия'}`

### Section Header Layout Fix

Prevent header/helper text overlap on mobile:
```css
.gt {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}
.gt small {
  display: block;
  line-height: 16px;
}
```

## Implementation Pattern

When updating sidebar UI:
1. Replace all lowercase chip labels with capitalized versions
2. Translate Chinese-derived chips (少/多) to Russian
3. Apply CSS fix for section headers
4. Update LABEL map values with capitalization
5. Verify no Chinese characters remain in visible text

## Quality Assurance

- Scan for `\u4e00-\u9fff` Unicode ranges to detect remaining Chinese characters
- Test on mobile devices to verify header layout fix
- Confirm filter functionality still works with unchanged `data-v` values
- Check that all chips display with proper capitalization

## Example Fix Pattern

```javascript
// Replace chip labels
t = t.replace('<button class="chip" data-v="少" aria-pressed="false">少</button>', 
              '<button class="chip" data-v="少" aria-pressed="false">Мало</button>');
t = t.replace('<button class="chip" data-v="多" aria-pressed="false">多</button>', 
              '<button class="chip" data-v="多" aria-pressed="false">Много</button>');

// Capitalize all other chips
capitalizedChips = [
  ['очень высокая', 'Очень высокая'],
  ['высокая', 'Высокая'],
  // ... other chips
];
for (let [old, new] of capitalizedChips) {
  t = t.replace(`<button class="chip" data-v="[^"]*" aria-pressed="false">${old}</button>`, 
                `<button class="chip" data-v="$1" aria-pressed="false">${new}</button>`);
}
```