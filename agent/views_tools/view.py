from .base import ExistsBase


class View(ExistsBase):
    @staticmethod
    def format(data):
        return {
            "id": data.id,
            "view": data.view_name,
            "key": data.key_name,
            "code": data.code_name,
            "type": data.get_type_display(),
            "is_register": data.is_register,
            "create_time": data.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def check_exits(self):
        if self.action == "name_exists":
            self.field = "view_name"
        return self.filter_queryset(self.get_queryset())
