# LLM Evaluation Harness

Мини-фреймворк для оценки качества промтов и LLM-приложений.

## Цель
Показать, как измерять качество ответов модели, а не полагаться на субъективное впечатление.

## Что внутри
- `data/test_cases.json` — 20 тестовых задач (классификация, извлечение сущностей, суммаризация).
- `src/evaluate.py` — скрипт для прогона промтов и расчёта метрик.
- `results/` — сохранённые отчёты с метриками.

## Метрики
- **Accuracy** — доля правильных ответов.
- **F1-score** — баланс между точностью и полнотой.
- **Exact Match** — полное совпадение.

## Как запустить
```bash
python src/evaluate.py

Автор
redsea1970


**Сохраните и выйдите:**
1. `Ctrl + O` (сохранить).
2. `Enter` (подтвердить имя файла).
3. `Ctrl + X` (выйти).

### 📄 Шаг 2. Создаём `data/test_cases.json` через `nano`

Выполните:
```bash
nano data/test_cases.json

[
  {"id": 1, "type": "classification", "input": "Отличный сервис, всё работает быстро", "expected": "positive"},
  {"id": 2, "type": "classification", "input": "Заказ пришёл поздно, упаковка повреждена", "expected": "negative"},
  {"id": 3, "type": "classification", "input": "Пока не могу оценить", "expected": "neutral"},
  {"id": 4, "type": "classification", "input": "Товар хороший, но доставка заняла вечность", "expected": "negative"},
  {"id": 5, "type": "classification", "input": "Спасибо за помощь в выборе!", "expected": "positive"},
  {"id": 6, "type": "classification", "input": "Ну не знаю, может быть и нормально", "expected": "neutral"},
  {"id": 7, "type": "classification", "input": "Курьер был вежлив и помог занести", "expected": "positive"},
  {"id": 8, "type": "classification", "input": "Пришло не то что заказывал", "expected": "negative"},
  {"id": 9, "type": "classification", "input": "Сначала всё сломалось, но поддержка быстро помогла", "expected": "positive"},
  {"id": 10, "type": "classification", "input": "Обычный товар, ничего особенного", "expected": "neutral"},
  {"id": 11, "type": "extraction", "input": "Иван Петров, email: ivan@example.com, телефон: +7-999-123-45-67", "expected": {"name": "Иван Петров", "email": "ivan@example.com", "phone": "+7-999-123-45-67"}},
  {"id": 12, "type": "extraction", "input": "Мария Сидорова, email: maria@test.ru", "expected": {"name": "Мария Сидорова", "email": "maria@test.ru", "phone": null}},
  {"id": 13, "type": "extraction", "input": "ООО Ромашка, ИНН 1234567890", "expected": {"name": "ООО Ромашка", "inn": "1234567890"}},
  {"id": 14, "type": "extraction", "input": "Алексей, тел. 8-800-555-35-35", "expected": {"name": "Алексей", "phone": "8-800-555-35-35"}},
  {"id": 15, "type": "extraction", "input": "Компания Вектор, адрес: г. Москва, ул. Ленина, д. 10", "expected": {"name": "Вектор", "address": "г. Москва, ул. Ленина, д. 10"}},
  {"id": 16, "type": "summarization", "input": "Компания X выпустила новый продукт. Он работает быстро и стоит недорого. Пользователи довольны.", "expected_keywords": ["новый продукт", "быстро", "недорого", "довольны"]},
  {"id": 17, "type": "summarization", "input": "Курс доллара вырос на 5%. Эксперты связывают это с санкциями. Прогнозы неоднозначны.", "expected_keywords": ["курс доллара", "вырос", "санкции", "прогнозы"]},
  {"id": 18, "type": "summarization", "input": "Новый закон вступит в силу с 1 января. Он коснётся малого бизнеса. Штрафы вырастут.", "expected_keywords": ["закон", "1 января", "малый бизнес", "штрафы"]},
  {"id": 19, "type": "summarization", "input": "Учёные обнаружили новый вид рыб. Он обитает на глубине 2 км. Исследование опубликовано в Nature.", "expected_keywords": ["новый вид", "рыбы", "глубина", "Nature"]},
  {"id": 20, "type": "summarization", "input": "Команда выиграла матч со счётом 3:1. Тренер доволен игрой. Следующий матч через неделю.", "expected_keywords": ["выиграла", "3:1", "тренер", "доволен"]}
]
