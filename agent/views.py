from rest_framework import viewsets
from . import models
from . import serializers
from . import views_tools
import string
import os
from rest_framework.response import Response
from rest_framework.decorators import action
from .lib2.zone_operate import Zone
from django.conf import settings


class ViewVies(views_tools.View, viewsets.GenericViewSet):
    """
    视图操作
    """
    authentication_classes = []
    permission_classes = []
    queryset = models.AgentViewModels.objects.all()
    db_models = models.AgentViewModels

    def get_serializer_class(self):
        if self.action == "id_exists":
            return serializers.ViewIdModelsSerializer
        return serializers.ViewNameModelsSerializer

    @action(detail=False, methods=["GET"], url_path="list")
    def get_views(self, request, *args, **kwargs):
        views_obj = self.get_queryset()
        return Response({"code": 0, "data": [self.format(i) for i in views_obj]})


class DomainView(views_tools.Domain, viewsets.GenericViewSet):
    """
    域名操作
    """
    authentication_classes = []
    permission_classes = []
    queryset = models.AgentDomainModels.objects.all()
    serializer_class = serializers.DomainSerializer
    db_models = models.AgentDomainModels

    def get_serializer_class(self):
        if self.action == "id_exists":
            return serializers.DomainExistsIDSerializer
        elif self.action == "name_exists":
            return serializers.DomainExistsNameSerializer
        elif self.action == "view_domain_exists":
            return serializers.DomainExistsViewSerializer
        elif self.action == "delete_domain":
            return serializers.DomainDeleteViewSerializer
        else:
            return serializers.DomainSerializer

    @action(detail=False, methods=["GET"], url_path='(?P<view>\w+)/domains')
    def get_domains(self, request, *args, **kwargs):
        domains_obj = self.queryset.filter(view__view_name=kwargs["view"])
        return Response({"code": 1, "data": [self.format(i) for i in domains_obj]})

    @action(detail=False, methods=["POST"], url_path='name/view/exits')
    def view_domain_exists(self, request, *args, **kwargs):
        """
        查看指定视图下是否存在指定域名，如果存放返回数据， code：0 表示找到数据， code:1 表示未找到数据
        """
        self.serializer_ver(self.get_serializer(data=request.data))
        try:
            domain_obj = self.get_queryset().get(view__view_name=request.data["view_name"],
                                                 domain_name=request.data["domain_name"])
            data = {"code": 0, "data": self.format(domain_obj)}
        except models.AgentDomainModels.DoesNotExist:
            data = {"code": 1, "data": {}}
        return Response(data)

    def create(self, request, *args, **kwargs):
        """
        创建域名
        """
        self.serializer_ver(self.get_serializer(data=request.data))
        agent_config = getattr(settings, "AGENT_CONFIG")
        view = request.data["view"]
        domain_name = request.data["domain_name"]
        zone_file = request.data["zone_file"]
        config = request.data["config"]
        view_obj = self.check_view_exists(view_name=view.strip())
        try:
            view_obj.domain.get(domain_name=domain_name)
        except models.AgentDomainModels.DoesNotExist:
            # 如果zone_file不存在则创建一个新的文件
            # '{type master; file "$zone_file"; allow-update {key $code;};};' zone_file 表示zone文件， safe_code 表示操作zone_key
            # if not os.path.exists(zone_file) or not os.path.isfile(zone_file):
            #     return Response({"code": 2003, "msg": "文件{file}不存在".format(file=zone_file)})
            config_template = string.Template(config.strip())
            try:
                config = config_template.substitute(zone_file=os.path.basename(zone_file), safe_code=view_obj.key_name)
            except KeyError as e:
                print("config template format fail error :{err}".format(err=e))
                return Response({"code": 2004, "msg": "视图{view}中添加域名{domain}失败".format(view=view, domain=domain_name)})
            zone_obj = Zone(agent_config["zone_template"], data_root=os.path.dirname(zone_file))
            if zone_obj.add_zone(view.strip(), domain_name.strip(), zone_file.strip(), config.strip()):
                view_obj.domain.create(
                    domain_name=domain_name,
                    zone_file=zone_file
                )
                return Response({"code": 0, "msg": "视图{view}中添加域名{domain}成功".format(view=view, domain=domain_name)})
            else:
                return Response({"code": 2004, "msg": "视图{view}中添加域名{domain}失败".format(view=view, domain=domain_name)})
        return Response({"code": 2002, "msg": "视图{view}已经存在{domain}域名 ".format(view=view, domain=domain_name)})

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete_domain(self, request, *args, **kwargs):
        """
        删除域名
        """
        self.serializer_ver(self.get_serializer(data=request.data))
        agent_config = getattr(settings, "AGENT_CONFIG")
        view = request.data["view_name"]
        domain_name = request.data["domain_name"]
        is_delete_zone = request.data.get("is_delete_zone", False)
        view_obj = self.check_view_exists(view_name=view.strip())
        try:
            domain_obj = view_obj.domain.get(domain_name=domain_name)
            if len(domain_obj.zone_file) == 0:
                return Response(
                    {"code": 2005, "msg": "视图{view}域名{domain}没有zone文件".format(view=view, domain=domain_name)})
            zone_obj = Zone(agent_config["zone_template"], data_root=os.path.dirname(domain_obj.zone_file))
            if zone_obj.del_zone(view, domain_obj.domain_name, os.path.basename(domain_obj.zone_file),
                                 is_delete_file=is_delete_zone):
                domain_obj.delete()
                return Response({"code": 0, "msg": "视图{view}中删除域名{domain}成功".format(view=view, domain=domain_name)})
            else:
                return Response({"code": 2004, "msg": "视图{view}中删除域名{domain}失败".format(view=view, domain=domain_name)})
        except models.AgentDomainModels.DoesNotExist:
            return Response({"code": 2002, "msg": "视图{view}不存在{domain}域名 ".format(view=view, domain=domain_name)})


class ResolveView(views_tools.Resolve, viewsets.GenericViewSet):
    """
    解析记录操作
    """
    authentication_classes = []
    permission_classes = []
    queryset = models.AgentResolveModels.objects.all()
    serializer_class = serializers.AgentResolveModelsSerializer
    db_models = models.AgentResolveModels

    def get_serializer_class(self):
        if self.action == "id_exists":
            return serializers.ResolveExistsIDSerializer
        elif self.action == "name_exists":
            return serializers.ResolveExistsNameSerializer
        elif self.action == "delete_resolve":
            return serializers.AgentResolveDeleteModelsSerializer
        elif self.action == "modify_resolve":
            return serializers.AgentResolveModifyModelsSerializer
        else:
            return serializers.AgentResolveModelsSerializer

    @action(detail=False, methods=["GET"], url_path="type")
    def get_type(self, request, *args, **kwargs):
        """获取支持的解析类型"""
        return Response({"code": 0, "data": dict(self.db_models.TYPE_CHOICES)})

    @action(detail=False, methods=["GET"], url_path='list/(?P<view_id>[0-9]+)/(?P<domain_id>[0-9]+)')
    def get_resolve(self, request, *args, **kwargs):
        query = self.queryset.filter(domain_id=kwargs["domain_id"], domain__view_id=kwargs["view_id"])
        return Response({"code": 1, "date": [self.format(i) for i in query]})

    def create(self, request, *args, **kwargs):
        self.serializer_ver(self.get_serializer(data=request.data))
        view = request.data["view"]
        domain = request.data["domain"]
        self.verification()
        domain_obj = self.check_view_domain_exists(view=view, domain=domain)
        name = request.data["name"]
        mx = request.data["mx"]
        ttl = request.data["ttl"]
        address = request.data["address"]
        resolve_type = request.data["type"]
        bind_obj = self.bind(domain_obj)

        try:
            self.queryset.get(domain_id=domain_obj.id, name=name, type=resolve_type, address__value=address)
            return Response({"code": 1002, "msg": "解析已经存在"})
        except models.AgentResolveModels.DoesNotExist:
            sub_resolve_type = dict(self.db_models.TYPE_CHOICES)[int(resolve_type)]
            if sub_resolve_type == "MX":
                mx = 5 if request.data["mx"] < 5 else request.data["mx"]
            else:
                mx = 0
            sub_host = self.is_mx(int(resolve_type), mx, address)
            if not bind_obj.add(name=name, ttl=ttl, domain_type=sub_resolve_type, host=sub_host):
                return Response({"code": 1002, "msg": "创建解析失败"})
            if not bind_obj.save():
                return Response({"code": 1002, "msg": "创建解析失败"})
            resolve_obj,_ = domain_obj.resolve.get_or_create(
                name=name,
                type=resolve_type,
            )
            resolve_obj.address.create(
                value=address,
                ttl=ttl,
                mx=mx
            )
            return Response({"code": 0, "msg": "解析添加成功"})

    @action(detail=False, methods=["POST"], url_path='modify')
    def modify_resolve(self, request, *args, **kwargs):
        self.serializer_ver(self.get_serializer(data=request.data))
        try:
            instance = self.get_queryset().get(id=request.data["id"], address__value=request.data["address"])
        except models.AgentResolveModels.DoesNotExist:
            return Response({"code": 1001, "msg": "当前解析不存在"})
        self.verification(instance)
        value_obj = instance.address.get(value=request.data["address"])
        value_obj.ttl = request.data.get("ttl", value_obj.ttl)
        value_obj.mx = request.data.get("mx", value_obj.mx)
        value_obj.value = request.data.get("new_address", value_obj.value)
        if instance.get_type_display() == "MX":
            value_obj.mx = value_obj.mx if int(request.data["mx"]) < 5 else int(request.data["mx"])
            sub_host = ["{mx} {address}".format(mx=i.mx, address=i.value) for i in instance.address.all()]
        else:
            value_obj.mx = 0
            sub_host = [i.value for i in instance.address.all()]

        sub_host.append(self.is_mx(int(instance.type), value_obj.mx, value_obj.value))
        bind_obj = self.bind(instance.domain)
        if not bind_obj.replace(name=instance.name, ttl=value_obj.ttl, domain_type=instance.get_type_display(),
                                host=sub_host):
            return Response({"code": 1002, "msg": "当前解析修改失败"})
        if not bind_obj.save():
            return Response({"code": 1002, "msg": "当前解析修改失败"})
        value_obj.save()
        return Response({"code": 0, "msg": "解析修改完成"})

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete_resolve(self, request, *args, **kwargs):
        self.serializer_ver(self.get_serializer(data=request.data))
        try:
            instance = self.get_queryset().get(id=request.data["id"], address__value=request.data["address"])
        except models.AgentResolveModels.DoesNotExist:
            return Response({"code": 1001, "msg": "当前解析不存在"})
        bind_obj = self.bind(instance.domain)
        value_obj = instance.address.get(value=request.data["address"])

        address = self.is_mx(int(instance.type), value_obj.mx, value_obj.value)
        if not bind_obj.delete(name=instance.name, ttl=value_obj.ttl, domain_type=instance.get_type_display(),
                               host=address):
            return Response({"code": 1002, "msg": "删除解析失败"})
        if not bind_obj.save():
            return Response({"code": 1002, "msg": "删除解析失败"})
        print(len(instance.address.all()))
        if len(instance.address.all()) > 1:
            value_obj.delete()
        else:
            instance.delete()
        return Response({"code": 0, "msg": "删除解析完成"})
