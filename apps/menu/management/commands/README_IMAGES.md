# Обновление изображений продуктов

## Подготовка файла изображения

1. Убедитесь, что файл `larry.jpg` находится в корне проекта или скопируйте его туда
2. Файл будет автоматически использован для всех продуктов

## Способы обновления изображений

### Способ 1: Обновить изображения для всех существующих продуктов

```bash
docker exec -it arabica-back python manage.py update_product_images
```

Или с указанием другого изображения:

```bash
docker exec -it arabica-back python manage.py update_product_images --image products/other_image.jpg
```

### Способ 2: Импортировать продукты с изображением (новые продукты получат larry.jpg автоматически)

```bash
docker exec -it arabica-back python manage.py import_products
```

## Важно

- Путь к изображению: `products/larry.jpg` (относительно MEDIA_ROOT)
- Файл должен быть доступен в контейнере Django
- Если файл находится в корне проекта, его нужно скопировать в `media/products/` или использовать через volume

## Проверка

После выполнения команды проверьте:

```bash
# В Django shell
docker exec -it arabica-back python manage.py shell

# Затем в shell:
from apps.menu.models import Product
Product.objects.first().image  # Должно показать 'products/larry.jpg'
```
