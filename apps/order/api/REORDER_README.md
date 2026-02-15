# Повторный заказ (Reorder)

## Описание

API endpoint для повторения предыдущих заказов. Позволяет добавить все товары из заказа в корзину, а также добавить дополнительные товары.

## Endpoint

```
POST /api/v1/orders/<order_id>/reorder/
```

**Требования:**
- Аутентификация: требуется (только для владельца заказа)
- Content-Type: `application/json`

## Использование

### Базовое использование (повторить заказ без дополнительных товаров)

```bash
curl -X POST http://your-domain/api/v1/orders/1/reorder/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{}'
```

### С дополнительными товарами

```bash
curl -X POST http://your-domain/api/v1/orders/1/reorder/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "additional_items": [
      {
        "product_id": 5,
        "quantity": 2,
        "options": [1, 2],
        "comment": "Дополнительный комментарий"
      },
      {
        "product_id": 10,
        "quantity": 1,
        "options": []
      }
    ]
  }'
```

## Формат запроса

### Без дополнительных товаров:

```json
{}
```

### С дополнительными товарами:

```json
{
  "additional_items": [
    {
      "product_id": 5,
      "quantity": 2,
      "options": [1, 2, 3],
      "comment": "Комментарий к товару"
    }
  ]
}
```

### Поля дополнительного товара:

- `product_id` (обязательно) - ID продукта
- `quantity` (опционально) - количество (по умолчанию 1)
- `options` (опционально) - список ID опций (по умолчанию [])
- `comment` (опционально) - комментарий к товару

## Формат ответа

### Успешный ответ (200 OK):

```json
{
  "message": "Товары из заказа успешно добавлены в корзину",
  "cart": {
    "id": 1,
    "user": 1,
    "items": [
      {
        "id": 1,
        "product": 1,
        "quantity": 2,
        "comment": "",
        "options": [
          {
            "id": 1,
            "option_value": {
              "id": 1,
              "type": 1,
              "value": "200 мл"
            }
          }
        ],
        "get_total_price": 240
      }
    ],
    "get_total_price": 240
  },
  "added_items": [
    {
      "product": "Эспрессо",
      "quantity": 2
    },
    {
      "product": "Капучино",
      "quantity": 1
    }
  ]
}
```

### С предупреждениями:

```json
{
  "message": "Товары из заказа успешно добавлены в корзину",
  "cart": { ... },
  "added_items": [ ... ],
  "warnings": [
    "Продукт 'Старый продукт' больше не доступен",
    "Опция с ID 5 не найдена"
  ]
}
```

### Ошибки:

**404 Not Found** - Заказ не найден или принадлежит другому пользователю:
```json
{
  "detail": "Not found."
}
```

**400 Bad Request** - Ошибка валидации:
```json
{
  "additional_items": [
    {
      "product_id": ["Это поле обязательно."]
    }
  ]
}
```

## Особенности

1. **Восстановление опций**: Опции из оригинального заказа автоматически восстанавливаются в корзине
2. **Проверка доступности**: Недоступные продукты пропускаются с предупреждением
3. **Дополнительные товары**: Можно добавить новые товары к повторному заказу
4. **Кэш**: Кэш корзины автоматически очищается после добавления товаров
5. **Безопасность**: Пользователь может повторять только свои заказы

## Пример использования в Python

```python
import requests

url = "http://your-domain/api/v1/orders/1/reorder/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}

# Просто повторить заказ
response = requests.post(url, json={}, headers=headers)
print(response.json())

# Повторить заказ с дополнительными товарами
data = {
    "additional_items": [
        {
            "product_id": 5,
            "quantity": 2,
            "options": [1, 2],
            "comment": "Дополнительный товар"
        }
    ]
}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Пример использования в JavaScript

```javascript
// Повторить заказ
fetch('http://your-domain/api/v1/orders/1/reorder/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    additional_items: [
      {
        product_id: 5,
        quantity: 2,
        options: [1, 2],
        comment: 'Дополнительный товар'
      }
    ]
  })
})
.then(response => response.json())
.then(data => {
  console.log('Товары добавлены в корзину:', data);
})
.catch(error => {
  console.error('Ошибка:', error);
});
```

## Workflow

1. Пользователь просматривает список своих заказов: `GET /api/v1/orders/`
2. Пользователь выбирает заказ для повторения
3. Пользователь вызывает `POST /api/v1/orders/<order_id>/reorder/`
4. Все товары из заказа добавляются в корзину
5. Пользователь может добавить дополнительные товары через тот же запрос
6. Пользователь просматривает корзину: `GET /api/v1/cart/cart/`
7. Пользователь может редактировать корзину или создать новый заказ
