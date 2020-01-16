# Bind9 管理
[![Python3](https://img.shields.io/badge/Python-3.6.9-blue.svg?style=popout&)](https://www.python.org/)
[![Django2](https://img.shields.io/badge/Django-2.1.11-brightgreen.svg?style=popout)](https://www.djangoproject.com/)
[![Bind](https://img.shields.io/badge/Bind-9.9.4-orange.svg?style=popout)](http://www.isc.org/)
[![DnsPython](https://img.shields.io/badge/DnsPython-1.16.0-9cf.svg?style=popout)](http://www.dnspython.org/)
[![DnsPython](https://img.shields.io/badge/DjangoRestFramework-3.10.3-yellow.svg?style=popout)](https://www.django-rest-framework.org/)


#### 环境部署
##### 获取代码,并进入bind9_config
```bash
git clone https://github.com/xiaoxin1992/bind9_config.git
cd bind9_config
```

##### 安装所需要的模块以及初始化数据库
```bash
pip3 install -r requirements.txt
python3 manage.py  migrate
```

##### 启动服务
```bash
python3 manage.py  runserver 0.0.0.0:8000
```


#### bind 配置

##### rndc配置
```bash
# rndc-confgen
# Start of rndc.conf
key "rndc-key" {
	algorithm hmac-md5;
	secret "K5kgr6A5IfwDXmbou2NxrQ==";
};

options {
	default-key "rndc-key";
	default-server 127.0.0.1;
	default-port 953;
};
# End of rndc.conf

# Use with the following in named.conf, adjusting the allow list as needed:
# key "rndc-key" {
# 	algorithm hmac-md5;
# 	secret "K5kgr6A5IfwDXmbou2NxrQ==";
# };
#
# controls {
# 	inet 127.0.0.1 port 953
# 		allow { 127.0.0.1; } keys { "rndc-key"; };
# };
# End of named.conf
```
rndc.key 配置文件添加
```bash
# cat>/etc/rndc.key
key "rndc-key" {
	algorithm hmac-md5;
	secret "K5kgr6A5IfwDXmbou2NxrQ==";
};

options {
	default-key "rndc-key";
	default-server 127.0.0.1;
	default-port 953;
};
```

named.conf 配置文件添加
```bash
# /etc/named.conf
key "rndc-key" {
 	algorithm hmac-md5;
 	secret "K5kgr6A5IfwDXmbou2NxrQ==";
};

controls {
 	inet 127.0.0.1 port 953
 		allow { 127.0.0.1; } keys { "rndc-key"; };
};
```

##### named.conf配置

创建view文件
```bash
touch /etc/named/view.conf
```
创建key文件
```bash
touch /etc/named/dns.key
```
view.conf 内容如下 
```bash
view "myview" {
        match-clients { key mykey; 127.0.0.1;};
        zone "." IN {
                type hint;
                file "named.ca";
        };
        include "/etc/named.rfc1912.zones";
};
```

key生成进入 /var/named/
```bash
dnssec-keygen -a HMAC-MD5 -b 128 -n USER mykey
chown named.named -R /var/naemd  # 保证named用户可以访问
```

key文件内容如下
```bash
key "mykey" {
   algorithm hmac-md5;
   secret "GzzQeGnshf+n15mwLiEUMg==";
};
```

named.conf 配置如下

```bash
cat /etc/named.conf
options {
'''省略配置''''
dnssec-enable yes;
dnssec-validation yes;
allow-new-zones yes;
}

key "rndc-key" {
	algorithm hmac-md5;
 	secret "K5kgr6A5IfwDXmbou2NxrQ==";
};

controls {
	inet 127.0.0.1 port 953
 		allow { 127.0.0.1; } keys { "rndc-key"; };
};

include "/etc/named/dns.key";
include "/etc/named/view.conf";
include "/etc/named.root.key";
/*因为使用的是bind视同所以需要删除
include "/etc/named.rfc1912.zones";
*/
```
检查配置文件
```bash
named-checkconf
```
重启服务
```bash
systemctl  restart named
```

添加视图到agent端
```bash
# python3 manage.py  view  --add myview mykey master
[+] 视图: myview添加成功!
```
第一个参数视图名称       我这里是myview
第二个参数是key的名称    我这里是mykey
第三个是主从            我这里是master, 目前支持单台dns


查看视图
```bash
# python3 manage.py  view  --list
+--------+-------+--------------------------+--------+------------+---------------------+
|  视图  |  key  |           code           |  类型  | 注册服务端 |       创建日期      |
+--------+-------+--------------------------+--------+------------+---------------------+
| myview | mykey | GzzQeGnshf+n15mwLiEUMg== | master |   未注册   | 2019/07/11 18:05:56 |
+--------+-------+--------------------------+--------+------------+---------------------+
```
删除视图
```bash
# python3 manage.py  view  --delete myview
[+] 视图: myview删除成功!
```


说明:
   agent使用的rndc协议
   域名： 创建完成后会存放在生成视图哈希以.nzf结尾的文件，bind重启的时候会加载
   
   解析: 创建会存放以域名开始.jnl结尾的文件, 比如: test.com.jnl bind每个15分组会写入到区域文件 test.com.zone 但是需要确保named用户对区域文件可写权限，否则不会写入
  
 
 [API接口调用文档](./api.md)
