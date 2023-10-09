
from chatSocket import  ChatSocket

from GLM import model_pre

import asyncio




def wait_model(data):
    return model_pre()


def main():
    socket_ = ChatSocket()
    while True:
        conn=socket_.server_set()
        if conn:
            data=conn.get_()
            response=wait_model(data)
            conn.send_(response)






if __name__=="__main__":
    main()