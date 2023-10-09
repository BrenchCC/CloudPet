import sys
import time

from transformers import AutoTokenizer, AutoModel






class model():
    def __init__(self):
        print("建立模型")
        self.tokenizer = AutoTokenizer.from_pretrained("D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4",
                                                  trust_remote_code=True, revision="")
        self.model = AutoModel.from_pretrained("D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4", trust_remote_code=True,
                                          revision="").float()
        self.model = self.model.quantize(bits=4,
                               kernel_file="D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4\\quantization_kernels.so")
        self.model = self.model.quantize(bits=4,
                               kernel_file="D:\\Mycode\\source\\python\\llm\\chatglm-6b-int4\\quantization_kernels_parallel.so")
        self.model = self.model.eval()

    def model_pre(self,data):
        response, history = model.chat(self.tokenizer, data, history=[])
        return response

model()