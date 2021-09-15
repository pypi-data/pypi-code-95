class MerConfig(object):
    """
    商户配置信息
    """
    private_key = ""  # 商户私钥
    public_key = ""  # 商户公钥
    product_id = ""  # 产品号
    sys_id = ""  # 商户系统号

    def __init__(self, private_key, public_key, sys_id, product_id):
        self.product_id = product_id
        self.private_key = private_key
        self.public_key = public_key
        self.sys_id = sys_id
