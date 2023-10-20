import socket  # for sockets
import time
import sys  # for exit



try:
    # create an AF_INET, STREAM socket (TCP)
    print("尝试创建链接")
    server = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM)  # 这两个其实就是默认参数，不写也一样，分别表示 IPv4(默认)，流式socket - for TCP (默认)

    ip, port = '127.0.0.1', 9999

    BUFFER_SIZE = 1024  # 该变量为一次传输的最大字节信息量【缓冲区大小】
    # 如果发送的信息超过这个大小，最好--在开头就说明文件大小，或者增加一个终止符在结尾
    # 也许也能一次就发1024，短于1024就意味着终止？

    SOCKET_TIMEOUT_TIME = 60  # 超时 时间

except socket.error.msg:
    print("创建链接失败")
    sys.exit();




def receive_socket_info(handle, expected_msg, side='server', do_decode=True, do_print_info=True):
    """
    循环接收socket info，判断其返回值，直到指定的值出现为止，防止socket信息粘连，并根据side打印不同的前缀信息
    :param handle: socket句柄
    :param expected_msg: 期待接受的内容，如果接受内容不在返回结果中，一直循环等待，期待内容可以为字符串，也可以为多个字符串组成的列表或元组
    :param side: 默认server端
    :param do_decode: 是否需要decode，默认True
    :param do_print_info: 是否需要打印socket信息，默认True
    :return:
    """
    while True:
        if do_decode:  # 发来的信息可能有编码要求
            socket_data = handle.recv(BUFFER_SIZE).decode()
        else:
            socket_data = handle.recv(BUFFER_SIZE)

        # 如果expected_msg为空，跳出循环
        if not expected_msg:
            break

        if isinstance(expected_msg, (list, tuple)):
            flag = False
            for expect in expected_msg:  # 循环判断每个期待字符是否在返回结果中
                if expect in socket_data:  # 如果有任意一个存在，跳出循环
                    flag = True
                    break
            if not flag:  # 如果没有该标识符
                return False
        else:
            if expected_msg not in socket_data:  # 如果没有该标识符
                return False
            else:
                break

        time.sleep(3)  # 每隔3秒接收一次socket--测试时使用，正式使用不受限

    return socket_data


def server_set(text):  # 创建一个链接
    try:

        server.connect((ip,port))
        print("链接成功")
        server.send(text.encode())

        respone=server.recv(BUFFER_SIZE).decode()
        if respone=="正在处理":
            print("正在处理")
            answer=server.recv(BUFFER_SIZE).decode()
            return answer
        else:
            print("存在错误，第一次返回为非 正在处理 ")


    except:
        print("链接失败")
        sys.exit()

