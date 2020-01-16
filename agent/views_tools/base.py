from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response


class SerializerVerificationCheck:
    """
    检查Serializer参数是否正常
    """

    def serializer_ver(self, serializer):
        serializer_check = serializer.is_valid(raise_exception=False)
        if not serializer_check:
            key = [i for i in serializer.errors][0]
            raise ValidationError({"code": 1001, "msg": "{field} {msg}".format(field=key, msg=serializer.errors[key])})


class ExistsBase(SerializerVerificationCheck):
    """
    生成根据名称和id查询数据是否存在接口
    """

    @action(detail=False, methods=["POST"], url_path='name/exists')
    def name_exists(self, request, *args, **kwargs):
        """
          根据名称查找数据是否存在， code： 为0表示查找到信息 code为1表示未找到信息
          """
        self.serializer_ver(self.get_serializer(data=request.data))
        return self.check_exits()

    @action(detail=False, methods=["POST"], url_path='id/exists')
    def id_exists(self, request, *args, **kwargs):
        """
          根据名称查找数据是否存在， code： 为0表示查找到信息 code为1表示未找到信息
          """
        self.serializer_ver(self.get_serializer(data=request.data))
        return self.check_exits()

    def filter_queryset(self, queryset):
        field = getattr(self, "field", "id")
        try:
            f_data = self.format(queryset.get(**{field: self.request.data[field]}))
            return Response({"code": 0, "data": f_data})
        except self.db_models.DoesNotExist:
            return Response({"code": 1, "data": {}})
