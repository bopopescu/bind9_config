from django.core.management.base import BaseCommand, CommandError
from agent.lib2.key_analysis import RNdcKey
from agent import models
from django.conf import settings
from prettytable import PrettyTable
import argparse


class Command(BaseCommand):
    help = "增加视图"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--add", action="store_true", help="增加视图")
        group.add_argument("--list", action="store_true", help="列出视图")
        group.add_argument("--delete", action="store_true", help="删除视图")
        parser.add_argument("value", type=str, nargs=argparse.REMAINDER, help="[ view-name, key_name, dns_type]")

    def add_view(self, name, key, dns_type):
        try:
            models.AgentViewModels.objects.get(view_name=name.strip())
            raise CommandError("[+] 视图: {name} 已经存在!".format(name=name))
        except models.AgentViewModels.DoesNotExist:
            config = getattr(settings, "AGENT_CONFIG")["named_key"]
            key_obj = RNdcKey(config)
            key = key_obj.get_target(key)
            if key is None:
                raise CommandEifcorror("[+] 视图: {name} 秘钥获取失败!".format(name=name))
            models.AgentViewModels.objects.create(
                view_name=name.strip(),
                key_name=key["name"],
                code_name=key["key"],
                type=dns_type
            )
            self.stdout.write(self.style.SUCCESS("[+] 视图: {name}添加成功!".format(name=name)))

    @staticmethod
    def list_view(table):
        for i in models.AgentViewModels.objects.all():
            table.add_row(
                [i.view_name,
                 i.key_name,
                 i.code_name,
                 i.get_type_display(),
                 "注册" if i.is_register else "未注册",
                 i.create_time.strftime("%Y/%d/%m %H:%M:%S")]
            )

    def handle(self, *args, **options):
        if options.get("add"):
            try:
                name, key, dns_type = options["value"]
            except ValueError:
                raise CommandError("缺少参数!")
            if dns_type.strip() == "master":
                dns_type = 1
            elif dns_type.strip() == "slave":
                dns_type = 2
            else:
                raise CommandError("dns_type错误, 目前支持[master, slave]")
            self.add_view(name, key, dns_type)
        elif options.get("list"):

            table = PrettyTable(["视图", "key", "code", "类型", "注册服务端", "创建日期"])
            self.list_view(table)
            print(table)
        elif options.get("delete"):
            #  注册到服务器端后需要在服务端删除
            try:
                name = options["value"][0]
                view_obj = models.AgentViewModels.objects.get(view_name=name)
                if not view_obj.is_register:
                    view_obj.delete()
                    self.stdout.write(self.style.SUCCESS("[+] 视图: {name}删除成功!".format(name=name)))
                else:
                    raise CommandError("{name} 视图已经注册到服务端, 请在服务端删除".format(name=options["value"]))
            except ValueError:
                raise CommandError("缺少参数!")
            except models.AgentViewModels.DoesNotExist:
                raise CommandError("{name} 视图不存在".format(name=options["value"][0]))
        else:
            raise CommandError("请填写正确的参数!")
