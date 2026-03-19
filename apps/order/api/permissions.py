from rest_framework.permissions import BasePermission

from apps.order.models import CafeMembership


def _get_membership(user):
    # Для списков/объектов удобно не плодить try/catch в каждом view.
    try:
        return user.cafe_membership
    except CafeMembership.DoesNotExist:
        return None


class IsCafeStaff(BasePermission):
    """
    Разрешает доступ только сотруднику кафе (в рамках его филиала).
    """

    def has_permission(self, request, view):
        membership = _get_membership(request.user)
        return bool(membership and membership.role == CafeMembership.Role.STAFF)

    def has_object_permission(self, request, view, obj):
        membership = _get_membership(request.user)
        return bool(membership and obj.cafe_id == membership.cafe_id)


class IsCourier(BasePermission):
    """
    Разрешает доступ только курьеру и только к назначенным ему заказам.
    """

    def has_permission(self, request, view):
        membership = _get_membership(request.user)
        return bool(membership and membership.role == CafeMembership.Role.COURIER)

    def has_object_permission(self, request, view, obj):
        return bool(obj.courier_id == request.user.id)

