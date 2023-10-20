import requests
import json
import traceback




def stream_connection(self,inputs, history, sys_prompt):
    #headers, payload = generate_payload(self,inputs=inputs, system_prompt=sys_prompt, stream=True ,history=history)

    def get_access_token():
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.api_key, "client_secret": self.secret_key}
        return str(requests.post(url, params=params).json().get("access_token"))

    def create_payload(inputs,system_prompt,history):
        messages=[

        ]
        messages.append({"role": "user", "content": history[0][0]})
        for i in range(len(history[0]) -1 ):
            print(i)
            print(history[1][i])
            messages.append({"role": "assistant", "content": history[1][i]})
            messages.append({"role": "user", "content": history[0][i+1]})
        return json.dumps( {"messages":messages} )



    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + get_access_token()

    payload=create_payload(inputs,sys_prompt,history)

    headers = {
        'Content-Type': 'application/json'
    }

    retry = 0
    while True:
        try:
            print("尝试发送信息给llm-{}")
            # make a POST request to the API endpoint, stream=False
            response = requests.post(url, headers=headers ,data=payload,
                                     stream=True, timeout=self.timeout_seconds)


            print("发送成功")
            break
        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > self.max_retry: raise TimeoutError
            if self.max_retry !=0: print(f'请求超时，正在重试 ({retry}/{self.max_retry}) ……')

    c = json.loads(response.text)

    return  c['result']
