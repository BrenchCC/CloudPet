
import requests
import traceback
import json


def get_full_error(chunk, stream_response):
    """
        获取完整的从Openai返回的报错
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

def generate_payload(self,inputs, system_prompt, stream, history):
    """
        整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    timeout_bot_msg = '[Local Message] Request timeout. Network error. Please check proxy settings in config.py.' + \
                      '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'

    if len(self.api_key) != 51:
        raise AssertionError("你提供了错误的API_KEY。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
    }

    messages = [
        {"role": "system",
         "content": system_prompt}
    ]
    user_history = history[0]
    pet_history = history[1]
    if user_history:
        for index in range(0, len(user_history)):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = user_history[index]

            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"

            try:
                what_gpt_answer["content"] = pet_history[index]
            except:
                what_gpt_answer["content"] = ""
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "":
                    continue
                if what_gpt_answer["content"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['content'] = what_gpt_answer['content']

    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = inputs
    messages.append(what_i_ask_now)

    payload = {
        "model": self.llm_model,
        "messages": messages,
        "temperature": self.temperature,  # 1.0,
        "top_p": self.top_p,  # 1.0,
        "n": 1,
        "stream": stream,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    try:
        print(f" {self.llm_model} : {len(history[0])} : {inputs[:100]} ..........")
    except:
        print('输入中可能存在乱码。')
        print(headers)

    return headers, payload

def stream_connection(self,inputs, history, sys_prompt):
    headers, payload = generate_payload(inputs=inputs, system_prompt=sys_prompt, stream=True ,history=history)

    retry = 0
    while True:
        try:

            # make a POST request to the API endpoint, stream=False

            response = requests.post(self.url, headers=headers, proxies=self.proxies,
                                    json=payload, stream=True, timeout=self.timeout_seconds)


            break
        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > self.max_retry: raise TimeoutError
            if self.max_retry != 0: print(f'请求超时，正在重试 ({retry}/{self.max_retry}) ……')

    stream_response =  response.iter_lines()
    result = ''

    c = json.loads(response.text)

    return  c['result']


    while True:
        try:
            chunk = next(stream_response).decode()
        except StopIteration:
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response).decode() # 失败了，重试一次？再失败就没办法了。

        if len(chunk) == 0:
            continue

        if not chunk.startswith('data:'):
            error_msg = get_full_error(chunk.encode('utf8'), stream_response).decode()
            if "reduce the length" in error_msg:
                raise ConnectionAbortedError("OpenAI拒绝了请求:" + error_msg)
            else:
                raise RuntimeError("OpenAI拒绝了请求：" + error_msg)

        json_data = json.loads(chunk.lstrip('data:'))['choices'][0]
        delta = json_data["delta"]
        if len(delta) == 0: break
        if "role" in delta: continue
        if "content" in delta:
            result += delta["content"]
        else: raise RuntimeError("意外Json结构： " +delta)
    if json_data['finish_reason'] == 'length':
        raise ConnectionAbortedError("正常结束，但显示Token不足，导致输出不完整，请削减单次输入的文本量。")
    return result