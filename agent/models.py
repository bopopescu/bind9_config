from django.db import models


class AgentViewModels(models.Model):
    TYPE_CHOICES = (
        (1, "master"),
        (2, "slave"),
    )
    view_name = models.CharField(max_length=120, unique=True, verbose_name="视图名称")
    key_name = models.CharField(max_length=120, verbose_name="视图所有使用的Key名称")
    code_name = models.CharField(max_length=120, verbose_name="视图所有使用密钥")
    type = models.IntegerField(default=1, choices=TYPE_CHOICES, verbose_name="服务类型")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_register = models.BooleanField(default=False, verbose_name="是否注册到服务端")

    def __str__(self):
        return "<{!r}>".format(self.view_name)

    class Meta:
        verbose_name = "视图表"
        verbose_name_plural = verbose_name


class AgentDomainModels(models.Model):
    domain_name = models.CharField(max_length=120, blank=False, null=False, verbose_name="域名")
    zone_file = models.CharField(max_length=120, blank=False, null=False, verbose_name="zone文件使用的文件路径")
    view = models.ForeignKey(AgentViewModels, on_delete=models.CASCADE, related_name="domain", verbose_name="视图")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return "<{!r}-{!r}>".format(self.view.view_name, self.domain_name)

    class Meta:
        verbose_name = "域名表"
        verbose_name_plural = verbose_name


class AgentResolveModels(models.Model):
    TYPE_CHOICES = (
        (1, "AAAA"),
        (2, "A"),
        (3, "NS"),
        (4, "CNAME"),
        (5, "TXT"),
        (6, "MX")
    )
    name = models.CharField(max_length=120, verbose_name="解析名称")
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name="解析类型")
    domain = models.ForeignKey(AgentDomainModels, on_delete=models.CASCADE, related_name="resolve", verbose_name="域名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return "<{!r}-{!r}-{!r}>".format(self.domain.view.view_name, self.domain.domain_name, self.name)

    class Meta:
        verbose_name = "解析表"
        verbose_name_plural = verbose_name


class AgentResolveValue(models.Model):
    resolve = models.ForeignKey(AgentResolveModels, related_name="address", on_delete=models.CASCADE)
    value = models.CharField(max_length=128, verbose_name="解析值")
    ttl = models.IntegerField(default=600, verbose_name="TTL值, 默认值600")
    mx = models.IntegerField(default=0, help_text="MX记录值, 非MX记录则为0")

    def __str__(self):
        return "{!r}".format(self.value)

    class Meta:
        verbose_name = "解析值"
        verbose_name_plural = verbose_name
