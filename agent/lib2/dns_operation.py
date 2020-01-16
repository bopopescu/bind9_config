#! -*- coding:utf8 -*-
import dns.update
import dns.query
import dns.tsigkeyring
import dns.zone
import dns.rdatatype
import logging
import dns.rdata
import dns.rdataclass


class Bind:
    def __init__(self, server, key, code, domain, port=53, allow_type=None):
        self.server = server
        self.port = port
        self.keyring = dns.tsigkeyring.from_text({'{}'.format(key): '{}'.format(code)})
        self.dns = dns.update.Update(domain, keyring=self.keyring)
        if allow_type is None:
            self.allow_type = ['AAAA', 'A', 'NS', 'CNAME', 'TXT', 'MX']
        else:
            self.allow_type = allow_type
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s",
            datefmt="%d/%b/%Y %H:%M:%S"
        )

    def add(self, name, ttl, domain_type, host):
        if domain_type not in self.allow_type:
            logging.error("不允许增加'{}'类型记录 来自: {} {} {}操作".format(domain_type, name, domain_type, host))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, host)
            self.dns.add(name, dns_obj)
            logging.info("创建添加解析对象 {} {} {} 成功!".format(name, domain_type, host))
            return True
        except Exception as e:
            logging.error("创建添加解析对象 {}  {}  {}  失败, 错误: {},请检查IP,解析类型，域名是否存在".format(name, domain_type, host, str(e)))
            return False

    def replace(self, name, ttl, domain_type, host):
        if domain_type not in self.allow_type:
            logging.error("不允许修改'{}'类型记录 来自: {} {} {}操作".format(domain_type, name, domain_type, host))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, *host)
            self.dns.replace(name, dns_obj)
            logging.info("创建修改解析对象 {} {} {} 成功!".format(name, domain_type, host))
            return True
        except Exception as e:
            # 域名类型或者主机IP非法, 请检查
            logging.error("创建修改解析对象 {}  {}  {}  失败, 错误: {},请检查IP,解析类型，域名是否存在".format(name, domain_type, host, str(e)))
            return False

    def delete(self, name, domain_type, host, ttl):
        if domain_type not in self.allow_type:
            logging.error("不允许删除'{}'类型记录 来自: {} {} {}操作".format(domain_type, name, domain_type, host))
            return False
        try:
            # mx记录 name必须为空，如果记录不是本域名的则需要写全部域名  例如 'mail.test.com.'
            dns_obj = dns.rdataset.from_text("IN", domain_type, ttl, host)
            self.dns.delete(name, dns_obj)
            logging.info("创建删除解析对象 {} {} {} 成功!".format(name, domain_type, host))
            return True
        except Exception as e:
            # 域名类型或者主机IP非法, 请检查, 或域名不存在
            logging.error("创建删除解析对象{}  {}  {}  失败, 错误: {},请检查IP,解析类型，域名是否存在".format(name, domain_type, host, str(e)))
            return False

    def save(self):
        try:
            send_result = dns.query.tcp(self.dns, self.server, timeout=10, port=self.port)
            if send_result.rcode() == 0:
                logging.info("解析记录操作提交至{}服务器成功!".format(self.server))
                return True
            elif send_result.rcode() == 5:
                logging.error("解析记录操作提交至{}服务器失败, 请检查密钥相关配置".format(self.server))
                return False
            elif send_result.rcode() == 9:
                logging.error("解析记录操作提交至{}服务器失败, 域名不存在, 请手动删除系统中的域名".format(self.server))
                return False
            else:
                print("----------ERROR INFO----------")
                print(send_result)
                print("----------ERROR END----------")
                logging.error("解析记录操作提交至{}服务器失败".format(self.server))
                return False
        except Exception as e:
            # 连接服务器失败，请检查服务器是否正常
            logging.error("连接 {}:{} 服务器失败，请检查服务器是否正常, 错误:{}".format(self.server, self.port, str(e)))
            return False
