#! -*- coding:utf8 -*-
import dns.update
import dns.query
import dns.tsigkeyring
import dns.zone
import dns.rdatatype
import dns.rdata
import dns.rdataclass


class Resolve:
    def __init__(self, domain, zone_file, allow_type=None):
        self.domain = domain
        self.zone_file = zone_file
        if allow_type is None:
            self.allow_type = ['AAAA', 'A', 'NS', 'CNAME', 'TXT', 'MX']
        else:
            self.allow_type = allow_type

    @property
    def show_zone_resolve(self):
        dns_obj = dns.zone.from_file(self.zone_file, self.domain)
        dns_domain_name_list = list()
        for (name, ttl, data) in dns_obj.iterate_rdatas():
            if "{}".format(data) == "@":
                continue
            if dns.rdatatype.to_text(data.rdtype) in self.allow_type:
                dns_domain_name_list.append({
                    "name": "{}".format(name),
                    "ttl": int(ttl),
                    "type": "{}".format(dns.rdatatype.to_text(data.rdtype)),
                    "ip": "{}".format(data)
                })
        return dns_domain_name_list
