import socket  # for sockets
import time
import sys  # for exit

import asyncio #用来建立协程

class Connect():
    def __init__(self,conn,address,BUFFER_SIZE):
        self.conn=conn
        self.address=address

        self.BUFFER_SIZE=BUFFER_SIZE

        self.conn.send("正在处理".encode())

    def get_(self):
        while True:#使用while是为了一个链接能够有多次交流
            socket_data = self.conn.recv(self.BUFFER_SIZE).decode()

            self.data = socket_data

            print("当前获取的信息为{}".format(socket_data))

            if not socket_data:
                self.conn.close()
                break

            if 'quit' in socket_data:  # 这里是关闭指令
                self.conn.close()
                break

            break  # 目前只进行一次对话，后续改为协程之后，再删去这一行

        # 断开socket连接
        # self.conn.close() 暂时不能断开连接，因为后续还要发回给对方内容

        #print(f'与客户端 {self.ip}:{self.port} 断开连接')
        return  # 只进行一次对话

    def send_(self,msg):
        self.conn.send(msg.encode())
        self.conn.close()

class ChatSocket():
    def __init__(self,ip='127.0.0.1',port= 9999,listen_Num=1,BUFFER_SOZE=1024,SOCKET_TIMEOUT=60):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM)  # 这两个其实就是默认参数，不写也一样，分别表示 IPv4(默认)，流式socket - for TCP (默认)

            self.ip, self.port = ip,port

            self.listen_Num=listen_Num

            self.BUFFER_SIZE = BUFFER_SOZE  # 该变量为一次传输的最大字节信息量【缓冲区大小】
            # 如果发送的信息超过这个大小，最好--在开头就说明文件大小，或者增加一个终止符在结尾
            # 也许也能一次就发1024，短于1024就意味着终止？

            self.SOCKET_TIMEOUT = SOCKET_TIMEOUT  # 超时 时间

            self.socket.bind((self.ip, self.port))  # 绑定IP与端口


            self.socket.listen(listen_Num)  # 设置最大连接数为1,因为只跟自己的服务器进行连线


        except:
            print("创建链接失败")
            sys.exit()

    def server_set(self):  # 创建一个服务器，用于等待链接，但不做出任何反应--仅仅用于接收信息
        try:

            print('等待连接...')
            conn, address = self.socket.accept()  # 使用accept阻塞式等待客户端请求，如果多个客户端同时访问，排队一个一个进
            conn.settimeout(self.SOCKET_TIMEOUT)  # 设置服务端超时时间

            print("创建链接成功")

            self.conn=Connect(conn,address,self.BUFFER_SIZE)

            # 这里的coon应该也是一种socket?
            print(f'当前连接客户端：{address}')

            return self.conn

            # 不断接收客户端发来的消息 —— 这里应该制作成协程，处理下面的内容，因为listen可能不止一个


        except:
            print("退出链接")
            sys.exit()




