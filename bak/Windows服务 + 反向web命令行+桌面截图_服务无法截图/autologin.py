import os
from datetime import datetime

import sys
import ctypes
import winreg


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def set_auto_login(username, password):   # 设置用户自动登录
    try:
        # 打开注册表项
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", 0, winreg.KEY_SET_VALUE)

        # 设置AutoAdminLogon
        winreg.SetValueEx(reg_key, "AutoAdminLogon", 0, winreg.REG_SZ, "1")
        # 设置DefaultUserName
        winreg.SetValueEx(reg_key, "DefaultUserName", 0, winreg.REG_SZ, username)
        # 设置DefaultPassword
        winreg.SetValueEx(reg_key, "DefaultPassword", 0, winreg.REG_SZ, password)
        # 关闭注册表项
        winreg.CloseKey(reg_key)


        print(f"{username}自动登录设置成功。")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    if not is_admin():
        # 如果没有管理员权限，使用ShellExecuteW重新启动自己
        print("没有管理员权限，正在请求提升权限...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)  # 退出当前脚本
    else:
        print("已获取管理员权限，正在设置自动登录...")

    # 调用函数设置自动登录
    set_auto_login("administrator", "F@st84080081")  # 替换为你的用户名和密码

