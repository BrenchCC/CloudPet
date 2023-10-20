import os;
os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染



def main():

    #gra-web端的内容在  GraWeb中，暂时没有任何修改，直接导入可用
    #原本位置上的内容进行了删除，不知道是否会对Pet有所影响
    #删除了这部分，极大地提升了启动的速度
    
    #桌面宠物的类
    #导入桌宠界面
    from DesktopPet import create_pet

    create_pet()

if __name__ == "__main__":
    main()