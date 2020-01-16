from rest_framework import serializers
from . import models


#  ------------------------视图操作---------------------------------
class ViewNameModelsSerializer(serializers.ModelSerializer):
    view_name = serializers.CharField(help_text="视图名称")

    class Meta:
        model = models.AgentViewModels
        fields = ["view_name"]


class ViewIdModelsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="视图ID")

    class Meta:
        model = models.AgentViewModels
        fields = ["id"]


#  -------------------------------------------------------------


# ----------------------------域名操作----------------------------
class DomainSerializer(serializers.ModelSerializer):
    domain_name = serializers.CharField(max_length=120, help_text="域名")
    zone_file = serializers.CharField(max_length=120, help_text="zone文件使用的文件路径")
    view = serializers.CharField(help_text="视图名称")
    config = serializers.CharField(max_length=120, help_text="域名配置项参数")

    class Meta:
        model = models.AgentDomainModels
        fields = ["view", "domain_name", "zone_file", "config"]


class DomainExistsViewSerializer(serializers.ModelSerializer):
    domain_name = serializers.CharField(help_text="域名")
    view_name = serializers.CharField(help_text="视图名称")

    class Meta:
        model = models.AgentDomainModels
        fields = ["view_name", "domain_name"]


class DomainDeleteViewSerializer(serializers.ModelSerializer):
    domain_name = serializers.CharField(help_text="域名")
    view_name = serializers.CharField(help_text="视图名称")
    is_delete_zone = serializers.BooleanField(default=False, help_text="是否删除域名解析文件")

    class Meta:
        model = models.AgentDomainModels
        fields = ["view_name", "domain_name", "is_delete_zone"]


class DomainExistsNameSerializer(serializers.ModelSerializer):
    domain_name = serializers.CharField(help_text="域名")

    class Meta:
        model = models.AgentDomainModels
        fields = ["domain_name"]


class DomainExistsIDSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="域名ID")

    class Meta:
        model = models.AgentDomainModels
        fields = ["id"]


# ----------------------------------------------------------------


# -------------------------解析操作-------------------------
class AgentResolveModelsSerializer(serializers.ModelSerializer):
    TYPE_CHOICES = (
        (1, "AAAA"),
        (2, "A"),
        (3, "NS"),
        (4, "CNAME"),
        (5, "TXT"),
        (6, "MX")
    )
    name = serializers.CharField(help_text="解析名称")
    type = serializers.ChoiceField(choices=TYPE_CHOICES, label="解析类型",help_text="解析类型")
    mx = serializers.IntegerField(help_text="MX记录值, 非MX记录则为0")
    ttl = serializers.IntegerField(help_text="TTL值, 默认值600")
    address = serializers.CharField(help_text="解析地址")
    domain = serializers.CharField(help_text="域名")
    view = serializers.CharField(help_text="视图")

    class Meta:
        model = models.AgentResolveModels
        fields = ["name", "type", "mx", "ttl", "address", "domain", "view"]


class AgentResolveDeleteModelsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="解析ID")
    address = serializers.CharField(help_text="解析值")

    class Meta:
        model = models.AgentResolveModels
        fields = ["id", "address"]


class AgentResolveModifyModelsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="解析ID")
    address = serializers.CharField(help_text="解析值")
    new_address = serializers.CharField(help_text="新的解析值", required=False)
    mx = serializers.CharField(help_text="MX值", required=False)
    ttl = serializers.IntegerField(help_text="TTL值", required=False)

    class Meta:
        model = models.AgentResolveModels
        fields = ["id", "address", "new_address", "mx", "ttl"]


class ResolveExistsNameSerializer(serializers.ModelSerializer):
    resolve_name = serializers.CharField(help_text="解析名称")

    class Meta:
        model = models.AgentDomainModels
        fields = ["resolve_name"]


class ResolveExistsIDSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="解析ID")

    class Meta:
        model = models.AgentDomainModels
        fields = ["id"]

# ---------------------------------------------------------
