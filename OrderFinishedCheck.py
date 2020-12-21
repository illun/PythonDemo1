#  检查指定时间内（默认1天内） 订单， 按电子票方式出票的订单，订单支付完成后，仍然停留在待出票的订单
#  检查指定时间内（默认1天内） 订单， 按电子票方式出票的订单，订单支付完成后状态不正确的订单，tm_po_stub表里没有checkCode的记录
#  找到对应的订单后，可以以某种特定的格式，发送到指定的飞书群进行通报
#  支持每小时执行一次或指定的时间执行

# 测试MTL测试天团群
URL = "https://open.feishu.cn/open-apis/bot/v2/hook/b530999d-2e01-4030-99b9-273bb0******"
# 小群
URL2 = "https://open.feishu.cn/open-apis/bot/v2/hook/ddce83fc-1cad-40fa-a1d8-2e6328******"


#!/usr/bin/python
# -*- coding: UTF-8 -*-
import MySQLdb
from confluence2jira.FeishuOpt import FeishuOpt
import time
import datetime
from enum import Enum
from configparser import  ConfigParser
import argparse


class DB(Enum) :
    TM_SHOW = 'show'
    SHOW_CENTER = 'center'

parser = argparse.ArgumentParser(description="制定传入参数")
parser.add_argument("--env",type=str,default="QA")
parser.add_argument("--startDate",type=str)
parser.add_argument("--endDate",type=str)
args = parser.parse_args()

class checkOrderStatus():
    def connetDB(connetDB,sql):
        database_conf = ConfigParser()
        database_conf.read("db_config.cfg")
        hostname =  ""
        user =  ""
        password =  ""
        database =  ""

        env = args.env

        if (str(connetDB) == str(DB.TM_SHOW) and (str(env).upper()=='QA')):
            print("数据库 === show_qa")
            hostname = database_conf.get('show_qa','hostname')
            user = database_conf.get('show_qa', 'user')
            password = database_conf.get('show_qa', 'password')
            database = database_conf.get('show_qa', 'database')
        elif (str(connetDB) == str(DB.TM_SHOW) and (str(env).upper()=='PROD')):
            print("数据库 === show_prod")
            hostname = database_conf.get('show_prod', 'hostname')
            user = database_conf.get('show_prod', 'user')
            password = database_conf.get('show_prod', 'password')
            database = database_conf.get('show_prod', 'database')
        elif (str(connetDB) == str(DB.SHOW_CENTER) and (str(env).upper()=='QA')) :
            print("数据库 === show_center_qa")
            hostname = database_conf.get('show_center_qa','hostname')
            user = database_conf.get('show_center_qa', 'user')
            password = database_conf.get('show_center_qa', 'password')
            database = database_conf.get('show_center_qa', 'database')
        elif (str(connetDB) == str(DB.SHOW_CENTER) and (str(env).upper()=='PROD')) :
            print("数据库 === show_center_prod")
            hostname = database_conf.get('show_center_prod','hostname')
            user = database_conf.get('show_center_prod', 'user')
            password = database_conf.get('show_center_prod', 'password')
            database = database_conf.get('show_center_prod', 'database')
        try :

            db = MySQLdb.connect(hostname, user, password, database, charset='utf8')
            cursor = db.cursor()
            # 查询fhl_m的所有biz_shows
            cursor.execute(sql)  # 查询所有的fhl_m的演出id
            datas = cursor.fetchall()
            db.close()
        except Exception as e :
            print("数据库链接异常 %s"  %e)
        return datas


    def  checkOrderFinished():
        '''
        :param startDate:  查询下单日期的起始时间，默认当前日期
        :param endDate:  查询下单日期的结束时间
        :return: 时间段内 订单状态不正确的订单信息
        '''
        #链接show_center数据库,查询所有的来自风火轮的项目
        sql = "select biz_show.id from std_show  left join biz_show on std_show.id = biz_show.std_show_id where std_show.source = 'FHL_M'"
        datas = checkOrderStatus.connetDB(DB.SHOW_CENTER,sql)

        biz_show_ids = []
        for data in datas:
            if isinstance(data[0], str):
                biz_show_ids.append(data[0])
        # print(biz_show_ids)
        print("票务系统的show_ids list : " , tuple(biz_show_ids))

        # 处理时间  默认查询当前日期的数据，输入日期后，查询指定日期的数据
        if (isinstance(args.startDate,str) and isinstance(args.endDate,str)):
            start_date = args.startDate
            end_date = args.endDate
            print("start_date = args.startDate ", "end_date = args.endDate")
        else:
            start_date = time.strftime("%Y-%m-%d", time.localtime())
            end_date = time.strftime("%Y-%m-%d", time.localtime())
            print("start_date = systemdate", "end_date = systemdate")
        print("startDate === ", start_date,"endDate === ", end_date)

        #查询电子票的配送方式，但是下单后订单状态仍然未待出票或已支付的订单号
        sql = "select distinct order.orderOID,order.orderNumber,Date(order.createTime),order.biz_code,case order.orderStatus " \
              "when 'Ticket_Allocating' then '待出票Ticket_Allocating' " \
              "when 'Paid' then '已支付Paid' end," \
              "case order.deliverMethod " \
              "when 'eticket' then '电子票'  " \
              "when 'E_TICKET_ADMISSION' then '电子票-扫码入场' " \
              "when 'E_TICKET_ADMISSION_FOR_ID_CARD' then '身份证-直刷入场' " \
              "when 'venue' then '现场取票' " \
              "when 'VENUE_SELF_HELP' then '自助取票-电子码'   " \
              "when 'VENUE_SELF_HELP_FOR_ID_CARD' then '自助取票-身份证' " \
              "end from order " \
              "left join order_item on  order.orderOID = order_item.orderOID  " \
              "where order.biz_code in ( 'PXQ','FHL_M') and order.deliverMethod  in ('eticket','E_TICKET_ADMISSION','venue','E_TICKET_ADMISSION_FOR_ID_CARD','VENUE_SELF_HELP_FOR_ID_CARD','VENUE_SELF_HELP') " \
              " and order.orderStatus in( 'Ticket_Allocating','Paid') " \
              "and date(order.createtime) between '"+start_date+"' and '"+end_date+"' " \
              " and  order.showoid in " + str(
            tuple(biz_show_ids)) + " order by date(order.createtime) desc ; "
        print(sql)
        datas = checkOrderStatus.connetDB(DB.TM_SHOW, sql)
        return datas

    def  checkOrderPoTicketStub(orderIds):
        if isinstance(orderIds,str) :
            print("str")
            sql = "select order_id,stub from po_ticket_stub where order_id  in ('" + orderIds + "') ;"
        elif isinstance(orderIds,tuple):
            print("tuple")
            sql = "select order_id,stub from po_ticket_stub where order_id  in "+str(orderIds)+";"
        elif isinstance(orderIds,list):
            print("list")
            sql = "select order_id,stub from po_ticket_stub where order_id  in " + str(tuple(orderIds)) + ";"
        print(sql)
        datas = checkOrderStatus.connetDB(DB.TM_SHOW, sql)
        return datas



if __name__ == '__main__':

    datas = checkOrderStatus.checkOrderFinished()

    feishu = FeishuOpt()
    if (len(datas) > 0 ):

        #  订单状态不正确提醒
        orders = "序号,订单OID,订单编号,订单日期,订单状态,配送方式 \n"
        order_ids = []
        i = 1
        for data in datas:
            order = str(i) + ","
            for column in data:
                if isinstance(column, datetime.date):
                    column = str(column)
                order = order + column + ","
            # print(order)
            order_ids.append(data[0])
            orders = orders + order + '\n'
            i = i + 1
        # print(orders)
        # print(order_ids)
        output_content = str(orders)
        print(output_content)

        ##  发送 订单状态异常提醒
        feishu.sendMsgV2("订单状态异常提醒", orders, group=URL)

        #  检查查询的订单是否有po_ticket_stub
        if (len(order_ids)  > 0 ) :
            results = "序号,订单OID,是否有码\n"
            i = 1
            for order_id in order_ids :
            # print(order_ids,'=====\n=====',order_id)
                po_ticket_stub  = checkOrderStatus.checkOrderPoTicketStub(str(order_id))
                if (len(po_ticket_stub) > 0 ) :
                    if (str(po_ticket_stub[0][1]).__contains__("checkCode")) :
                        result = str(i) + "," + order_id +  ",有checkCode \n"
                    else:
                        result = str(i) + "," +  order_id + ",有po_ticket_stub记录，但是没有checkCode\n"
                else:
                    result = str(i) + "," + order_id + ",无checkCode\n"
                results = results + result

                i = i + 1
            print(results)
            ##  发送 异常订单数字码检查
            feishu.sendMsgV2("异常订单数字码检查",str(results),group=URL)

    else:
        orders = "无异常订单"
        feishu.sendMsgV2("订单状态异常提醒", orders, group=URL2)

