# 借鉴了 https://github.com/binary-husky/chatgpt_academic 项目

import json
import traceback
import requests
from queue import Queue
import time
from PyQt5.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor


from chat_model.chatGlm.chatSend import server_set


# private_config.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
class OpenAI_request(QThread):
    response_received = pyqtSignal(str)
    tools_received = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.prompt_queue = Queue()

        self.LLM=self.config["LLM"]["LLM_NAME"]
        
        #基本参数
        self.api_key = self.config[self.LLM]["API_KEY"]
        self.secret_key=self.config[self.LLM]["secret_key"]
        self.llm_model = self.config[self.LLM]["LLM_MODEL"]
        self.proxy = self.config[self.LLM]["PROXY"]
        self.proxies = {
            "http": self.proxy,
            "https": self.proxy,
        }
        self.timeout_seconds = int(self.config[self.LLM]["TIMEOUT_SECONDS"])
        self.max_retry = int(self.config[self.LLM]["MAX_RETRY"])
        self.url = self.config[self.LLM]["AUTHORIZE_URL"]
        self.top_p = float(self.config[self.LLM]["TOP_P"])
        self.temperature = float(self.config[self.LLM]["TEMPERATURE"])
        self.max_tokens = int(self.config[self.LLM]["MAX_TOKENS"])

        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        #设计启动的LLM类型

    
    def run(self):
        while True:
            prompt, context, sys_prompt, tools = self.prompt_queue.get()  # 从队列中获取 prompt 和 context

            if self.LLM=="GLM":
                response = server_set(prompt)
                self.tools_received.emit(response)
                self.response_received.emit(response)
                print(response)
            else:
                self.get_response_(inputs=prompt, history=context,sys_prompt=sys_prompt ,tools=tools)
            # time.sleep(0.1)



    #获取gpt回复
    def get_response_(self, inputs, history, sys_prompt='',
                              handle_token_exceed=True,retry_times_at_unknown_error=2,tools=False):
        # 多线程的时候，需要一个mutable结构在不同线程之间传递信息
        # list就是最简单的mutable结构，我们第一个位置放gpt输出，第二个位置传递报错信息

        # executor = ThreadPoolExecutor(max_workers=16)
        mutable = ["", time.time()]

        def _req_gpt(inputs, history, sys_prompt):
            retry_op = retry_times_at_unknown_error
            exceeded_cnt = 0
            while True:
                # watchdog error
                # if len(mutable) >= 2 and (time.time()-mutable[1]) > 5:
                #     raise RuntimeError("检测到程序终止。")
                try:
                    # 【第一种情况】：顺利完成
                    result = self.llm_stream_connection(
                        inputs=inputs, history=history, sys_prompt=sys_prompt)
                    return result
                except ConnectionAbortedError as token_exceeded_error:
                    # 【第二种情况】：Token溢出
                    if handle_token_exceed:
                        exceeded_cnt += 1
                        # 【选择处理】 尝试计算比例，尽可能多地保留文本
                        from toolbox import get_reduce_token_percent
                        p_ratio, n_exceed = get_reduce_token_percent(
                            str(token_exceeded_error))
                        MAX_TOKEN = 4096
                        EXCEED_ALLO = 512 + 512 * exceeded_cnt
                        inputs, history = self.input_clipping(
                            inputs, history, max_token_limit=MAX_TOKEN-EXCEED_ALLO)
                        mutable[0] += f'[Local Message] 警告，文本过长将进行截断，Token溢出数：{n_exceed}。\n\n'
                        continue  # 返回重试
                    else:
                        # 【选择放弃】
                        tb_str = '```\n' + traceback.format_exc() + '```'
                        mutable[0] += f"[Local Message] 警告，在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
                        return mutable[0]  # 放弃
                except Exception as e:
                    # 【第三种情况】：其他错误：重试几次
                    tb_str = '```\n' + traceback.format_exc() + '```'
                    mutable[0] += f"[Local Message] 警告，在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
                    if retry_op > 0:
                        retry_op -= 1
                        mutable[0] += f"[Local Message] 重试中，请稍等 {retry_times_at_unknown_error-retry_op}/{retry_times_at_unknown_error}：\n\n"
                        if "Rate limit reached" in tb_str:
                            time.sleep(30)
                        time.sleep(5)
                        continue  # 返回重试
                    else:
                        time.sleep(5)
                        return mutable[0]  # 放弃

        # 提交任务
        # future = executor.submit(_req_gpt, inputs, history, sys_prompt)

        # while True:
        #     if future.done():
        #         break
        # final_result = future.result()
        final_result = _req_gpt(inputs, history, sys_prompt)
        if tools:
            self.tools_received.emit(final_result)
        else:
            self.response_received.emit(final_result)
    
    def llm_stream_connection(self, inputs, history, sys_prompt):

        if self.LLM=='WenXin':
            from chat_model.WenXin_Request import stream_connection

            return stream_connection(self,inputs,history,sys_prompt)

        elif self.LLM == 'OpenAI':

            from chat_model.OpenAI_Request import stream_connection



