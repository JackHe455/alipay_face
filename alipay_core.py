#coding:utf-8
import json

import re
import rsa
import base64

SIGN_TYPE = "SHA-1"
import urllib

from config import RSA_ALIPAY_PUBLIC, RSA_PRIVATE, RSA_PUBLIC




def params_to_query(params):
    """
        生成需要签名的字符串
    :param params:
    :return:
    """
    """
    :param params:
    :return:
    """
    query = ""
    dict_items={}
    for key,value in params.items():
        if isinstance(value,dict)==True:
            dict_items[key]=value
            params[key]="%s"

    all_str=''
    for key in sorted(params.keys()):
        all_str=all_str+'%s=%s&' %(key,params[key])
    all_str=all_str.rstrip('&')


    biz_content_dict=dict_items['biz_content']

    content_str=''
    for key in sorted(biz_content_dict.keys()):
        if isinstance(biz_content_dict[key],basestring)==True:
            content_str=content_str+'"%s":"%s",' %(key,biz_content_dict[key])
        else:
            content_str = content_str + '"%s":%s,' % (key, biz_content_dict[key])
    content_str=content_str.rstrip(',')
    content_str='{'+content_str+'}'


    query=all_str %content_str

    return query





def make_sign(message):
    """
    签名
    :param message:
    :return:
    """
    private_key = rsa.PrivateKey._load_pkcs1_pem(RSA_PRIVATE)
    sign = rsa.sign(message, private_key, SIGN_TYPE)
    b64sing = base64.b64encode(sign)
    return b64sing




def check_sign(message, sign):
    """
    验证自签名
    :param message:
    :param sign:
    :return:
    """
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(RSA_PUBLIC)
    return rsa.verify(message, sign, pubkey)




def check_ali_sign(message, sign):
    """
    验证ali签名
    :param message:
    :param sign:
    :return:
    """
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(RSA_ALIPAY_PUBLIC)
    res = False
    try:
        res = rsa.verify(message, sign, pubkey)
    except Exception as e:
        print e
        res = False
    return res


def make_payment_request(params_dict):
    """
    构造一个支付请求的信息，包含最终结果里面包含签名
    :param params_dict:
    :return:
    """
    query_str = params_to_query(params_dict,) #拼接签名字符串
    sign = make_sign(query_str) #生成签名

    sign=urllib.quote(sign,safe='')
    res = "%s&sign=%s" % (query_str, sign)

    return res



def analysis_ali_response(body):
    '''
    对当前付款的返回的response进行解析 校验并且返回相关信息
    :param body:
    :return:
    '''
    result=False   #分析结果
    out_trade_no=''  #交易号
    qr_code=''   #二维码url
    if isinstance(body,basestring)==False or body=='':
        return result,out_trade_no,qr_code
    body_dict=json.loads(body)
    if isinstance(body_dict,dict)==False:
        return result, out_trade_no, qr_code
    sign=body_dict.get('sign','')
    if sign=='':
        return result, out_trade_no, qr_code
    alipay_trade_precreate_response=body_dict.get('alipay_trade_precreate_response',{})
    if isinstance(alipay_trade_precreate_response,dict)==False or alipay_trade_precreate_response.keys().__len__()==0:
        return result, out_trade_no, qr_code

    re_result=re.findall(r'^.*"alipay_trade_precreate_response":({.*}),"sign"',body)
    if re_result.__len__()==0:
        return result, out_trade_no, qr_code
    trade_str=re_result[0]
    if check_ali_sign(trade_str,sign)==False:
        return result, out_trade_no, qr_code
    out_trade_no=alipay_trade_precreate_response.get('out_trade_no','')
    qr_code=alipay_trade_precreate_response.get('qr_code','').replace('\/','/')
    result=True
    return result, out_trade_no, qr_code



def notify_make_query(params):
    '''
    对异步通知报文的参数组合成待签名的字符串
    :param params: 知报文参数 type dict
    :return:
    '''
    pop_keys=['sign','sign_type']   #需要剔除的key
    for key in pop_keys:
        params.pop(key)
    params_str=''
    for key in sorted(params.keys()):
        params_str=params_str+'%s=%s&' %(key,params[key])

    params_str=params_str.rstrip('&')
    return params_str


def notify_check_sign(params):
    '''
    异步通知报文进行签名校验
    :param params: 通知报文参数 type dict
    :return:
    '''
    sign=params.get('sign','')
    sign_str=notify_make_query(params)
    sign=sign.encode("utf-8")
    sign_str=sign_str.encode("utf-8")
    return check_ali_sign(sign_str,sign)








if __name__ == '__main__':
    # message='app_id=2016101000651561&biz_content={"out_trade_no":"20161114165856","subject":"test","total_amount":0.01}&charset=utf-8&method=alipay.trade.precreate&notify_url=http://test.kaoala.com/zh-cn/test/&sign_type=RSA&timestamp=2016-11-14 16:58:56&version=1.0'
    # #sign='eR/DwMmfCgfDAI2VqsUA8gwIy00mk9hrmRanyjPFIk6y9x0B+7opBwHloZvuZ/KpKhaXcmvpJKXGJA+MM5WU9qu0dnPS+TGJlh4yIxs4pRsCdke18249yZ98ZfkRxfkMuI42w+Lilkd84ziOONoTIhJ1uhTnYmkbBx7FOSAOJjE='
    # sign=make_sign(message)
    # print sign
    # re_message='{"alipay_trade_precreate_response":{"code":"10000","msg":"Success","out_trade_no":"20161114172110","qr_code":"https:\/\/qr.alipay.com\/bax017608vva6qhoi2zh0066"},"sign":"JRoEOO4v4Nz+2GCaE8fQWIzcCM89iVPIOWS5gC+ORriDqm16K+sbqFL6s8u4YtZHv5P143PK3vhHZqbQ9REOTw/DvAgRvLF08effQ9+xi00Oz6dblz/zB71I3/t9Zg35wQKOr6PvgBoSrR+OYnOGjeONMFjVo4wVA9mZu7WW9fs="}'
    # #re_sign='eR/DwMmfCgfDAI2VqsUA8gwIy00mk9hrmRanyjPFIk6y9x0B+7opBwHloZvuZ/KpKhaXcmvpJKXGJA+MM5WU9qu0dnPS+TGJlh4yIxs4pRsCdke18249yZ98ZfkRxfkMuI42w+Lilkd84ziOONoTIhJ1uhTnYmkbBx7FOSAOJjE='
    # print analysis_ali_response(re_message)
    dict_pa={u'seller_email': u'drehmy5005@sandbox.com', u'app_id': u'2016101000651561', u'sign': u'nzhASvx9DkHh0VPHep7JtsgiFBfS/rjfuSPuyUnJvcm/LzIy9pX+3sg2slfWwO6sI4lCdRGOy+gLFagL8oBH+goXkPMARQ/ZzlVtIMYrTq9Wl7cBhsEorpMbWc3sLN9wk+gckJ/he4ouIcDdBF4+HHc5UZFH3AHs9XeiNCzfVs8=', u'buyer_pay_amount': u'0.01', u'point_amount': u'0.00', u'subject': u'\u6d4b\u8bd5\u6668\u66e6', u'open_id': u'20881017039022118566577291814882', u'buyer_logon_id': u'bun***@sandbox.com', u'gmt_create': u'2016-11-15 11:14:24', u'out_trade_no': u'20161115111349', u'invoice_amount': u'0.01', u'sign_type': u'RSA', u'fund_bill_list': u'[{"amount":"0.01","fundChannel":"ALIPAYACCOUNT"}]', u'receipt_amount': u'0.01', u'trade_status': u'TRADE_SUCCESS', u'gmt_payment': u'2016-11-15 11:14:30', u'trade_no': u'2016111521001004820200129318', u'seller_id': u'2088102178904484', u'total_amount': u'0.01', u'notify_time': u'2016-11-15 11:14:31', u'notify_id': u'031f33ccc4cfc3cf4368fbbfc58a110mbu', u'notify_type': u'trade_status_sync', u'buyer_id': u'2088102169592821'}
    print notify_check_sign(dict_pa)













