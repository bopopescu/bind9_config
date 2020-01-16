from .base import ExistsBase
from ..models import AgentViewModels
from rest_framework.exceptions import ValidationError


class Domain(ExistsBase):
    @staticmethod
    def format(data):
        return {
            "id": data.id,
            "domain": data.domain_name,
            "zone_file": data.zone_file,
            "view": data.view.view_name,
            "create_time": data.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def check_exits(self):
        if self.action == "name_exists":
            self.field = "domain_name"
        return self.filter_queryset(self.get_queryset())

    @staticmethod
    def check_view_exists(view_name, is_error=True):
        try:
            return AgentViewModels.objects.get(view_name=view_name)
        except AgentViewModels.DoesNotExist:
            if is_error:
                raise ValidationError({"code": 2001, "msg": "视图: {view}不存在".format(view=view_name)})
            return None
