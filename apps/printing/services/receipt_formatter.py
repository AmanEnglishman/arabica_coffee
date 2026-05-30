from django.utils import timezone

WIDTH = 42  # 80mm paper @ 12x24 font ≈ 42 chars


def _divider():
    return "-" * WIDTH


def _center(text):
    return text.center(WIDTH)[:WIDTH]


def _left_right(left, right):
    right = str(right)
    left = str(left)
    max_left = WIDTH - len(right) - 1
    if len(left) > max_left:
        left = left[:max_left - 1] + "…"
    return f"{left:<{WIDTH - len(right)}}{right}"


def format_receipt(order) -> str:
    lines = []

    # Header
    cafe_name = order.cafe.name if order.cafe else "ARABICA"
    lines.append(_center(cafe_name))
    lines.append(_divider())
    lines.append(f"Заказ #{order.id}")
    now_str = timezone.localtime(order.created_at).strftime("%d.%m.%Y %H:%M")
    lines.append(f"Время: {now_str}")
    lines.append(_divider())

    # Items
    for item in order.items.select_related("product").all():
        name  = item.product.title
        qty   = item.quantity
        price = f"{item.final_price} с"
        lines.append(_left_right(f"{name} x{qty}", price))

        options = item.product_options.get("options", [])
        if options:
            opts_str = ", ".join(
                o.get("value", "") for o in options if o.get("value")
            )
            if opts_str:
                lines.append(f"  [{opts_str}]")

        comment = item.product_options.get("comment", "")
        if comment:
            lines.append(f"  Комм: {comment}")

    lines.append(_divider())

    # Bonus
    if order.bonus_spent:
        lines.append(_left_right("Бонусы:", f"-{order.bonus_spent} с"))

    lines.append(_left_right("ИТОГО:", f"{order.total_price} с"))
    lines.append("")

    # Delivery info
    if order.delivery_type == "delivery":
        lines.append("Тип: Доставка")
        if order.address:
            lines.append(f"Адрес: {order.address}")
        if order.delivery_time:
            lines.append(f"Время доставки: {order.delivery_time.strftime('%H:%M')}")
    else:
        lines.append("Тип: Самовывоз")

    # Customer
    if not order.user.phone_number.startswith("+00000"):
        name = " ".join(p for p in [order.user.first_name, order.user.last_name] if p)
        if name:
            lines.append(f"Клиент: {name}")
        lines.append(f"Тел: {order.user.phone_number}")

    lines.append(_divider())
    lines.append(_center("Спасибо за заказ!"))
    lines.append("")

    return "\n".join(lines)
