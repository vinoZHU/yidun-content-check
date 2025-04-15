import json
from collections.abc import Generator
from typing import Any

import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.image_check import ImageCheckAPIDemo
from tools.text_check import TextCheckAPIDemo


class YidunContentSecurityTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        params = {
            "secretId": self.runtime.credentials["yidun_secret_id"],
            "secretKey": self.runtime.credentials["yidun_secret_key"],
            "textBusinessId": self.runtime.credentials["yidun_text_business_id"],
            "imageBusinessId": self.runtime.credentials["yidun_image_business_id"],
            "textContent": tool_parameters["text_content"],
            "imageUrl": tool_parameters["image_url"],

        }
        time_stamp = str(int(time.time()))  # 时间戳获取
        ret = {}
        if (params["textBusinessId"] is not None and params["textBusinessId"] != ""
            and params["textContent"] is not None and params["textContent"] != ""):
            text_api = TextCheckAPIDemo(params["secretId"], params["secretKey"], params["textBusinessId"])
            text_check_param = {
                "dataId": "dify-yidun-text-check-" + time_stamp,
                "content": params["textContent"]
            }
            text_ret = text_api.check(text_check_param)
            code: int = text_ret["code"]
            if code == 200:
                result: dict = text_ret["result"]
                antispam: dict = result["antispam"]
                label: int = antispam["label"]
                suggestion: int = antispam["suggestion"]
                ret["text_label"] = label
                ret["text_suggestion"] = suggestion
            else:
                ret["text_result"] = text_ret

        if (params["imageBusinessId"] is not None and params["imageBusinessId"] != ""
            and params["imageUrl"] is not None and params["imageUrl"] != ""):
            image_api = ImageCheckAPIDemo(params["secretId"], params["secretKey"], params["imageBusinessId"])
            # 私有请求参数
            images: list = []
            image_url = {
                "name": "https://nos.netease.com/yidun/2-0-0-a6133509763d4d6eac881a58f1791976.jpg",
                "dataId": "dify-yidun-image-check-" + time_stamp,
                "type": 1,
                "data": "https://nos.netease.com/yidun/2-0-0-a6133509763d4d6eac881a58f1791976.jpg"
            }

            images.append(image_url)

            image_check_param = {
                "images": json.dumps(images)
            }
            image_ret = image_api.check(image_check_param)
            code: int = image_ret["code"]
            if code == 200:
                result: dict = image_ret["result"][0]
                antispam: dict = result["antispam"]
                label: int = antispam["label"]
                suggestion: int = antispam["suggestion"]
                ret["image_label"] = label
                ret["image_suggestion"] = suggestion
            else:
                ret["image_result"] = image_ret
        yield self.create_json_message({
            "check_result": ret
        })
