# -*- coding: utf-8 -*-

import json
import requests


#测试
#url = "https://open.feishu.cn/open-apis/bot/hook/a95a24f05cbc4cdb8b2325692******"

#正式MTL测试天团
url = "https://open.feishu.cn/open-apis/bot/hook/137bf99c93274ccfa88ce0ce4******"
#测试2
# url ="https://open.feishu.cn/open-apis/bot/v2/hook/ddce83fc-1cad-40fa-a1d8-2e632*****"


class FeishuOpt:

    def sendMsg(self, title, msg):
        headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }

        requestBody = {
            'title': title,
            "text": msg
        }

        s = requests.request("POST", url,
                             data=json.dumps(requestBody, ensure_ascii=False).encode('utf-8'),
                             headers=headers)
        js = s.json()
        print(js)

    def sendMsgV2(self, title, msg , **group):
        headers = {
            "Content-Type": "application/json",
            "charset": "utf-8"
        }

        requestBody = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": msg
                                }
                            ]
                        ]
                    }
                }
            }
        }

        if (len(group) > 0) :
            url = group['group']
            print(group['group'])

        s = requests.request("POST", url,
                             data=json.dumps(requestBody, ensure_ascii=False).encode('utf-8'),
                             headers=headers)
        js = s.json()
        print(js)


