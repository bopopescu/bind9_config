#### 获取视图列表
##### url: http://test.com:8000/agent/views/list/
##### method: GET
```bash
curl http://test.com:8000/agent/views/list/
{
    "code": 1,
    "data": [
        {
            "id": 1,
            "view": "myview",
            "key": "mykey",
            "code": "GzzQeGnshf+n15mwLiEUMg==",
            "type": "master",
            "is_register": false,
            "create_time": "2019/11/07/19-27 15:11:1573111669"
        }
    ]
}
```
##### 参数说明
```bash
id          视图在数据库的ID
view        视图名称
key         key名称
code        key密钥
type        是否是mater dns
is_register 是否注册到服务端
create_time 创建时间

```

#### 获取域名列表
##### url: http://test.com:8000/agent/domain/{view}/domains/
##### method: POST
##### 参数:
view            视图名称

##### 请求
```bash
curl http://test.com:8000/agent/domain/myview/domains/
{"code":1,"data":[{"id":1,"domain":"golet.cc","zone_file":"/var/named/golet.cc.zone","view":"myview","create_time":"2019/11/07/19-40 15:11:1573112411"},{"id":2,"domain":"xiaoxin.com","zone_file":"/var/named/xiaoxin.com.zone","view":"myview","create_time":"2019/11/07/19-40 15:11:1573112447"},{"id":4,"domain":"test.com","zone_file":"/var/named/test.com.zone","view":"myview","create_time":"2019/11/07/19-45 18:11:1573123536"}]}%
```

#### 创建域名
##### url: http://test.com:8000/agent/domain/
##### method: POST

##### 参数
```bash
view                视图名称
domain_name         域名名称
zone_file           zone文件使用的文件路径
config              域名配置项参数, named.conf 的zone配置
```

##### 请求
```bash
curl -H "Content-Type:application/json"  -X POST -d '{"view": "myview", "domain_name": "test.com", "zone_file": "/var/named/test.com.zone", "config": "{type master; file \"test.com.zone\"; allow-update {key mykey;};};"}' http://test.com:8000/agent/domain/
{"code":0,"msg":"视图myview中添加域名test.com成功"}%
type master; file "xiaoxin.com.zone"; allow-update {key mykey;};};
zone配置项目
{   type master; 
    file "xiaoxin.com.zone"; 
    allow-update {key mykey;};
};
```
code: 0表示成功， 非0表示失败


#### 删除域名
##### url: http://test.com:8000/agent/domain/delete/
##### method: POST
##### 参数
view_name           视图名称
domain_name         域名
is_delete_zone      是否删除域名解析文件

#####请求
```bash
curl -H "Content-Type:application/json" -X post -d '{"view_name": "myview", "domain_name": "test.com", "is_delete_zone":true}' http://test.com:8000/agent/domain/delete/
{"code":0,"msg":"视图myview中删除域名test.com成功"}%
```

#### 增加解析
##### url: http://test.com/agent/resolve/
##### method: POST
##### 参数
name                解析名称
type                解析类型, 支持['AAAA', 'A', 'NS', 'CNAME', 'TXT', 'MX']
mx                  MX记录值, 非MX记录则为0
ttl                 TTL值
address             解析地址
domain              域名名称
view                视图名称

##### 请求
```bash
curl -H "Content-Type:application/json"  -X POST -d '{"name": "www", "type": "A", "mx": 0, "ttl": 200, "address": "192.168.1.1", "domain": "test.com", "view": "myview"}' http://test.com:8000/agent/resolve/
{"code":0,"msg":"解析添加成功"}%
```

#### 获取解析
##### url: http://test.com/agent/resolve/list/{view_id}/{domain_id}/
##### method: GET
##### 参数
domain_id           域名ID
view_id             视图ID

#####请求
```bash
curl http://test.com:8000/agent/resolve/list/1/1/
{"code":1,"date":[{"id":8,"name":"www","type":"A","mx":0,"ttl":200,"address":"192.168.1.1"}]}%
```

#### 修改解析
##### url: http://test.com/agent/resolve/modify/
##### method: POST
##### 参数
id                  解析ID
mx                  MX记录值, 非MX记录则为0
ttl                 TTL值
address             解析地址

##### 请求
```bash
curl -H "Content-Type:application/json" -X post -d '{"id": 1, "mx": 0, "ttl": 200, "address": "10.10.10.1"}' http://test.com:8000/agent/resolve/modify/
{"code":0,"msg":"解析修改完成"}%
```


#### 删除解析
##### url: http://test.com/agent/resolve/delete/
##### method: POST
##### 参数
id                  解析ID

##### 请求
```bash
curl -H "Content-Type:application/json" -X post -d '{"id": 8}' http://test.com:8000/agent/resolve/delete/
{"code":0,"msg":"删除解析完成"}%
```

