#-*- coding:utf-8 -*-
import datetime
import logging
import requests

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from alipay_face.alipay_face import alipay_trade_precreate, alipay_response, alipay_notify_check

__author__ = 'root'

log = logging.getLogger('proscenium')


def face_test(request):
    '''
    获取支付宝当面支付的生成二维码的url
    :param request:
    :return: 生成二维码的url
    '''
    tn=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    url=alipay_trade_precreate(tn,'测试晨曦',0.01)
    log.info('获取支付宝报文 %s' %url)
    try:
        response=requests.get(url)
    except Exception,e:
        log.warning(e)
        log.warning('获取支付宝二维码失败')
        return HttpResponse('error')
    if response.status_code!=200:
        log.warning('获取支付宝二维码失败')
        return HttpResponse('error')
    body=response.text
    log.info('%s' %body)
    result=alipay_response(body)
    if result[0]==False:
        log.warning('获取支付宝二维码，解析返回报文体失败')
        return HttpResponse('error')
    return HttpResponseRedirect(result[2])

@csrf_exempt
def alipay_face_notify(request):
    '''
    异步通知处理函数
    :param request:
    :return:
    '''
    log.info(request.META.get('HTTP_USER_AGENT', ''))
    log.info('用户申请数据 %s' % request.POST)
    if request.method=='POST':
        log.info('items   %s',request.POST.dict())
        items_params=request.POST.dict()
        if alipay_notify_check(items_params)==True:
            log.info('支付宝支付成功')
            return HttpResponse('success')
        else:
            log.warning('支付宝支付失败')
            return HttpResponse('error')