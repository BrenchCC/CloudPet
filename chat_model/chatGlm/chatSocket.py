import socket  # for sockets
import time
import sys  # for exit


class ChatSocket():
    def __init__(self,ip='127.0.0.1',port= 9999,BUFFER_SOZE=1024,SOCKET_TIMEOUT=60):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM)  # 这两个其实就是默认参数，不写也一样，分别表示 IPv4(默认)，流式socket - for TCP (默认)

            self.ip, self.port = ip,port

            self.BUFFER_SIZE = BUFFER_SOZE  # 该变量为一次传输的最大字节信息量【缓冲区大小】
            # 如果发送的信息超过这个大小，最好--在开头就说明文件大小，或者增加一个终止符在结尾
            # 也许也能一次就发1024，短于1024就意味着终止？

            self.SOCKET_TIMEOUT = SOCKET_TIMEOUT  # 超时 时间

        except:
            print("创建链接失败")
            sys.exit()



    def send_info(self,msg,handle=None):
        if handle:
            handle.send(msg)
        else:
            self.socket.send(msg)

    def server_set(self):  # 创建一个服务器--接收链接
        try:
            self.socket.bind((self.ip, self.port))  # 绑定IP与端口
            print("socket链接成功")
            self.socket.listen(1)  # 设置最大连接数为1,因为只跟自己的服务器进行连线

            while True:

                print('等待连接...')
                conn, address = self.socket.accept()  # 使用accept阻塞式等待客户端请求，如果多个客户端同时访问，排队一个一个进
                # 这里的coon应该也是一种socket?
                print(f'当前连接客户端：{address}')

                conn.settimeout(self.SOCKET_TIMEOUT)  # 设置服务端超时时间
                # 不断接收客户端发来的消息 —— 这里应该制作成协程，处理下面的内容，因为listen可能不止一个
                while True:
                    socket_data = conn.recv(self.BUFFER_SIZE).decode()

                    self.data=socket_data

                    if not socket_data:
                        conn.close()
                        break

                    if 'quit' in socket_data:  # 这里是关闭指令
                        conn.close()
                        break

                    # 在预想之中，socket_data之中#-#后面接的是传送过来的图片或者视频的路径
                    # path = socket_data.replace("#-#", "")

                    # 这里放一些处理的内容，将获得的路径-数据传给模型等位置进行使用
                    # run.run(img_path=path)

                # 断开socket连接
                conn.close()
                print(f'与客户端 {self.ip}:{self.port} 断开连接')


        except:
            print("退出链接")
            sys.exit()


    def get_last_data(self):
        if self.data:
            return self.data
        else:
            return False

