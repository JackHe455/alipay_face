#-*- coding:utf-8 -*-
from alipay_core import make_payment_request, analysis_ali_response, notify_check_sign
from config import settings

__author__ = 'root'


#precreate_GATEWAY="https://openapi.alipay.com/gateway.do?"
precreate_GATEWAY='https://openapi.alipaydev.com/gateway.do?'   #测试环境
import datetime

def alipay_trade_precreate(tn, subject, total_fee):


    params = {}
    params['method'] = 'alipay.trade.precreate'
    params['version']='1.0'
    params['app_id'] = settings.APP_ID
    params['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params['charset']=settings.ALIPAY_INPUT_CHARSET
    params['notify_url'] = settings.ALIPAY_NOTIFY_URL
    params['sign_type']='RSA'

    # 获取配置文件
    biz_content={}


    # 从订单数据中动态获取到的必填参数
    biz_content['out_trade_no'] =tn   # 请与贵网站订单系统中的唯一订单号匹配
    biz_content['subject'] = subject  # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    biz_content['total_amount'] = total_fee  # 订单总金额，显示在支付宝收银台里的“应付总额”里

    params['biz_content']=biz_content

    encode_params=make_payment_request(params)

    return precreate_GATEWAY + encode_params





def alipay_response(body):
    '''
    对当前付款的返回的response进行解析 校验并且返回相关信息
    :param body: 返回的报文体
    :return:
    '''
    result=analysis_ali_response(body)
    return result


def alipay_notify_check(params):
    '''
    异步通知报文进行签名校验
    :param params: 通知报文参数 type dict
    :return:
    '''
    result=notify_check_sign(params)
    return result