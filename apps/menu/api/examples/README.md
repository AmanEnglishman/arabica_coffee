# Массовый импорт продуктов

## Описание

API endpoint для массового создания продуктов, категорий, подкатегорий и опций одним запросом.

## Endpoint

```
POST /api/v1/menu/bulk-import/
```

**Требования:**
- Аутентификация: требуется (только для администраторов)
- Content-Type: `application/json`

## Формат данных

### Структура запроса:

```json
{
  "categories": [
    {
      "title": "Название категории",
      "subcategories": [
        {
          "title": "Название подкатегории",
          "products": [
            {
              "title": "Название продукта",
              "price": 120,
              "description": "Описание продукта",
              "bonus_percent": 5.0,
              "has_options": true,
              "option_type_titles": ["Объем", "Вид молока"]
            }
          ]
        }
      ]
    }
  ],
  "option_types": [
    {
      "title": "Объем",
      "values": [
        {"value": "200 мл", "additional_cost": 0},
        {"value": "300 мл", "additional_cost": 20}
      ]
    }
  ]
}
```

### Поля продукта:

- `title` (обязательно) - название продукта
- `price` (обязательно) - цена (целое число, >= 0)
- `description` (обязательно) - описание продукта
- `bonus_percent` (опционально) - процент бонусов (по умолчанию 5.0)
- `has_options` (опционально) - есть ли опции у продукта (по умолчанию false)
- `option_type_titles` (опционально) - список названий типов опций, которые должны быть связаны с продуктом
- `image` (опционально) - путь к изображению

### Поля опций:

- `title` (обязательно) - название типа опции
- `values` (обязательно) - массив значений опции
  - `value` (обязательно) - название значения
  - `additional_cost` (опционально) - дополнительная стоимость (по умолчанию 0)

## Пример использования

### cURL:

```bash
curl -X POST http://your-domain/api/v1/menu/bulk-import/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @bulk_import_example.json
```

### Python (requests):

```python
import requests

url = "http://your-domain/api/v1/menu/bulk-import/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}

data = {
    "categories": [
        {
            "title": "Напитки",
            "subcategories": [
                {
                    "title": "Кофе",
                    "products": [
                        {
                            "title": "Эспрессо",
                            "price": 120,
                            "description": "Крепкий кофе",
                            "has_options": True,
                            "option_type_titles": ["Объем"]
                        }
                    ]
                }
            ]
        }
    ],
    "option_types": [
        {
            "title": "Объем",
            "values": [
                {"value": "200 мл", "additional_cost": 0},
                {"value": "300 мл", "additional_cost": 20}
            ]
        }
    ]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Ответ

### Успешный ответ (201 Created):

```json
{
  "message": "Продукты успешно импортированы",
  "created": {
    "categories": 2,
    "subcategories": 4,
    "products": 10,
    "option_types": 3,
    "option_values": 12
  }
}
```

### Ошибка валидации (400 Bad Request):

```json
{
  "categories": [
    {
      "subcategories": [
        {
          "products": [
            {
              "price": ["Это поле обязательно."]
            }
          ]
        }
      ]
    }
  ]
}
```

## Особенности

1. **Идемпотентность**: Если категория, подкатегория или продукт с таким названием уже существует, они не будут созданы повторно, но будут обновлены (для продуктов).

2. **Транзакции**: Все операции выполняются в одной транзакции. Если произойдет ошибка, все изменения будут отменены.

3. **Связывание опций**: Если продукт имеет `has_options: true` и указаны `option_type_titles`, опции будут автоматически связаны с продуктом.

4. **Права доступа**: Только администраторы могут использовать этот endpoint.

## Пример файла

См. `bulk_import_example.json` для полного примера.
