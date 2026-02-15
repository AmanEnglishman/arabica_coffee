# Повторный заказ (Reorder)

## Описание

API endpoint для повторения предыдущих заказов. Добавляет все товары из заказа в корзину пользователя.

## Endpoint

```
POST /api/v1/orders/<order_id>/reorder/
```

**Требования:**
- Аутентификация: требуется (только для владельца заказа)
- Content-Type: `application/json`

## Использование

### Использование

```bash
curl -X POST http://your-domain/api/v1/orders/1/reorder/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Примечание:** Запрос не требует тела (body), все товары из заказа автоматически добавляются в корзину.

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
3. **Кэш**: Кэш корзины автоматически очищается после добавления товаров
4. **Безопасность**: Пользователь может повторять только свои заказы
5. **Простота**: Не требует входных данных - просто переносит все товары из заказа в корзину

## Пример использования в Python

```python
import requests

url = "http://your-domain/api/v1/orders/1/reorder/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}

# Повторить заказ (все товары из заказа добавятся в корзину)
response = requests.post(url, headers=headers)
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
  }
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
4. Все товары из заказа автоматически добавляются в корзину с сохранением опций
5. Пользователь просматривает корзину: `GET /api/v1/cart/cart/`
6. Пользователь может редактировать корзину (добавить/удалить товары) или создать новый заказ
