import time

from transformers import AutoTokenizer, AutoModel

from chatSocket import  ChatSocket

print("建立模型")
tokenizer = AutoTokenizer.from_pretrained("D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4", trust_remote_code=True, revision="")
model = AutoModel.from_pretrained("D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4",trust_remote_code=True, revision="").float()
model = model.quantize(bits=4, kernel_file="D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4\\quantization_kernels.so")
model = model.quantize(bits=4, kernel_file="D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4\\quantization_kernels_parallel.so")
model = model.eval()

print("建立连接")
socket_=ChatSocket()

while True:
    socket_.server_set()#这里应该开启一个协程，用来不间断获取信息，且不需要等待它的进行，现在暂且简化，只用做一次信息获取
    print("开启服务器链接服务")
    data=socket_.get_last_data()
    if data:
        socket_.send_info("正在处理",handle=socket_.conn)
        response, history = model.chat(tokenizer, data, history=[])
        socket_.send_info(response,handle=socket_.conn)
        print(response)