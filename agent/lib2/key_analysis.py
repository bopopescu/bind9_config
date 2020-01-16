#! -*-coding:utf8 -*-
import re
import logging


class Base:
    def re_match(self, data):
        result = []
        for i in data:
            try:
                result.append(self.pattern.match(i).groupdict())
            except AttributeError:
                continue
        return result

    def format(self, data):
        return self.re_match(data=data)


class RNdcKey(Base):
    def __init__(self, file=None):
        self.file = file
        # 获取key名称和秘钥
        self.pattern = re.compile(
            r"key\s+['\"](?P<name>.*)['\"]\s+{[\s\S]+secret[\s]+['\"](?P<key>[\s\S]+)['\"]\s{0,};[\s\S]+?};")

    def get_all(self):
        try:
            with open(self.file) as f:
                # 获取key配置
                return self.format(re.findall(r"key\s['\"].*['\"]\s+{[\s\S]+?};", f.read()))
        except FileNotFoundError as err:
            logging.error("{error}".format(error=err))

    def get_target(self, key_name):
        result = self.get_all()
        if not result:
            return None
        for key in result:
            if key["name"] == key_name:
                return key
