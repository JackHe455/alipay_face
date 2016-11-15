# alipay_face
python(django) 支付宝当面支付（二维码 扫码支付）

生成rsa key,在控制台中执行命令，在当前文件夹下生成文件:
openssl genrsa -out app_private_key.pem   1024  #生成私钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem #生成公钥

