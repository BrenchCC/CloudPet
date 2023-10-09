import sys
import time

from transformers import AutoTokenizer, AutoModel



print("建立模型")
tokenizer = AutoTokenizer.from_pretrained("D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4", trust_remote_code=True, revision="")
model = AutoModel.from_pretrained("D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4",trust_remote_code=True, revision="").float()
model = model.quantize(bits=4, kernel_file="D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4\\quantization_kernels.so")
model = model.quantize(bits=4, kernel_file="D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4\\quantization_kernels_parallel.so")
model = model.eval()

def model_pre(data):
    response, history = model.chat(tokenizer, data, history=[])
    return response