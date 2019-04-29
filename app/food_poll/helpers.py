

def get_updated_serializer_fields(
        fields_to_extend, is_admin=False,
        fields_to_add_if_user_is_admin=False):
    if is_admin and fields_to_add_if_user_is_admin:
        fields_to_extend.extend(fields_to_add_if_user_is_admin)
    return fields_to_extend


def get_permissions_by_action(
        permission_classes_by_action, action, permission_classes):
    try:
        return [
            permission() for permission in permission_classes_by_action[action]
        ]
    except KeyError:
        return [permission() for permission in permission_classes]
