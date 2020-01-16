from django.conf import settings
from rest_framework.exceptions import ValidationError
from .base import SerializerVerificationCheck
from ..lib2.dns_operation import Bind
from ..models import AgentDomainModels
import re
from IPy import IP


class VerificationResolve:
    def __init__(self, name, address):
        self.name = name
        self.address = address

    @property
    def ver_domain(self):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})\.$'
        )
        if pattern.match(self.address):
            return True
        else:
            return False

    def ver_address(self, version=4):
        try:
            ip_obj = IP(self.address)
            return True if ip_obj.version() == version else False
        except ValueError:
            return False

    def cname(self):
        if not self.ver_domain:
            raise ValidationError({"code": 1004, "msg": "CNAME记录值必须是合格的FQDN名称"})

    def ipv4(self):
        if not self.ver_address(version=4):
            raise ValidationError({"code": 1004, "msg": "A记录值必须是合格的IPV4地址"})

    def ipv6(self):
        if not self.ver_address(version=4):
            raise ValidationError({"code": 1004, "msg": "AAAA记录值必须是合格的IPV6地址"})

    def ns(self):
        if not self.ver_address(4) and not self.ver_address(6) and not self.ver_domain:
            raise ValueError({"code": 1004, "msg": "NS记录值必须是合格的IP地址或者FNQD名称"})

    def mx(self):
        if self.name.strip() != "@":
            raise ValidationError({"code": 1004, "msg": "MX记录name必须是@"})
        if not self.ver_domain:
            raise ValidationError({"code": 1004, "msg": "MX记录值必须是合格的FQDN名称"})


class Resolve(SerializerVerificationCheck):

    @staticmethod
    def is_mx(resolve_type, mx, address):
        if resolve_type == 6:
            return "{mx} {address}".format(address=address, mx=5 if mx > 5 else mx)
        else:
            return address

    @staticmethod
    def verification_data(ver_obj, resolve_type):
        if resolve_type == 1:
            ver_obj.ipv6()
        elif resolve_type == 2:
            ver_obj.ipv4()
        elif resolve_type == 3:
            ver_obj.ns()
        elif resolve_type == 4:
            ver_obj.cname()
        elif resolve_type == 5:
            pass
        elif resolve_type == 6:
            ver_obj.mx()
        else:
            raise ValidationError({"code": 1004, "msg": "解析记录类型错误"})

    def verification(self, instance=None):
        if instance:
            ver = VerificationResolve(instance.name, self.request.data.get("new_address", self.request.data["address"]))
            resolve_type = int(instance.type)
        else:
            ver = VerificationResolve(self.request.data["name"], self.request.data["address"])
            resolve_type = int(self.request.data["type"])
        self.verification_data(ver, resolve_type)

    @staticmethod
    def format(data):
        return {
            "id": data.id,
            "name": data.name,
            "type": data.type,
            "values": [{
                "address": i.value,
                "ttl": i.ttl,
                "mx": i.mx
            } for i in data.address.all()]
        }

    def bind(self, domain_obj):
        config = getattr(settings, "DNS_SERVER")
        return Bind(config["server"], domain_obj.view.key_name, domain_obj.view.code_name, domain_obj.domain_name,
                    config["port"], [i[1] for i in self.db_models.TYPE_CHOICES])

    @staticmethod
    def check_view_domain_exists(view, domain, is_error=True):
        try:
            return AgentDomainModels.objects.get(view__view_name=view, domain_name=domain)
        except AgentDomainModels.DoesNotExist:
            if is_error:
                raise ValidationError({"code": 1002, "msg": "视图:{view}不存在:{domain}域名".format(view=view, domain=domain)})
            return None
