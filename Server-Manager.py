import subprocess, time, sys, os, re, psutil, json, smtplib, webbrowser, zipfile, requests, schedule, socket, asyncio, shutil, pywintypes, ctypes, pystray, threading, tqdm
import customtkinter as ctk
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import filedialog, messagebox
from PIL import Image
from gamercon_async import GameRCON, ClientError, TimeoutError, InvalidPassword
from win32api import (GetModuleFileName, RegCloseKey, RegDeleteValue, RegOpenKeyEx, RegSetValueEx, RegEnumValue)
from win32con import (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, KEY_WRITE, KEY_QUERY_VALUE, REG_SZ)
from winerror import ERROR_NO_MORE_ITEMS

Application_Executable_Directory = os.path.dirname(os.path.abspath(__file__))
Application_Executable_Path = os.path.abspath(__file__)
Application_Executable_Name = os.path.basename(__file__)
Application_Resource_Directory = os.path.join(Application_Executable_Directory, "assets")
Application_Image_Directory = os.path.join(Application_Resource_Directory, "images")
Application_Data_Directory = os.path.join(Application_Resource_Directory, "data")
Application_Update_Directory = os.path.join(Application_Resource_Directory, "updates")
Application_Name = "xKiller Palworld Server Manager"
Github_Repository = "xKiller-Palworld-Server-Manager"
Github_Username = "xkillermaverick"
Application_Local_Version = "1.5.0"
STARTUP_KEY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
DEFAULT_SETTINGS_FILE = os.path.join(Application_Resource_Directory, "Settings.json")
OLD_SETTINGS_FILE = os.path.join(os.path.expanduser("~"), "Documents/Palworld Server Manager", "settings.json")
LOGO_PNG_FILE = os.path.join(Application_Image_Directory, "Logo.png")
LOGO_ICO_FILE = os.path.join(Application_Image_Directory, "Logo.ico")
CHANGELOG_FILE = os.path.join(Application_Data_Directory, "Changelog.txt")
LICENSE_FILE = os.path.join(Application_Data_Directory, "License.txt")

async def rcon_command(host: str, port: int, password: str, command: str):
    try:
        async with GameRCON(host, port, password, timeout) as rcon:
            return await rcon.send(command)
    except (ClientError, TimeoutError, InvalidPassword) as e:
        return f"RCON error: {e}"
    except asyncio.TimeoutError:
        return "Timed out."
    except ConnectionResetError as e:
        return f"Connection reset: {e}"

def resource_directory():
    if not os.path.exists(Application_Resource_Directory):
        os.makedirs(Application_Resource_Directory)
        os.makedirs(Application_Update_Directory)
        os.makedirs(Application_Data_Directory)
        os.makedirs(Application_Image_Directory)

def download_resource(url, file_dir):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_dir, "wb") as fp:
                fp.write(response.content)
    except Exception as exData:
        pass

def save_settings():
    settings = {
        "Restart_Interval": restartEntry.get(),
        "Scheduled_Restart_Time": restartScheduleEntry.get(),
        "Time_Format": ampm_optionmenu_var.get(),
        "Monitor_Interval": monitorEntry.get(),
        "Backup_Interval": backupIntervalEntry.get(),
        "Backups_Age_Limit": deleteOldBackupsEntry.get(),
        "Server_Save_Interval": saveIntervalEntry.get(),
        "Server_Directory": server_directory_selection.cget("text"),
        "Arrcon_Directory": arrcon_directory_selection.cget("text"),
        "Steamcmd_Directory": steamcmd_directory_selection.cget("text"),
        "Backup_Directory": backup_directory_selection.cget("text"),
        "Palworld_Start_Arguments": server_start_args_entry.get(),
        "Email_Address": email_address_entry.get(),
        "Email_Password": email_password_entry.get(),
        "Discord_Webhook_URL": discordUrlEntry.get(),
        "Smtp_Server": smtp_server_entry.get(),
        "Smtp_Port": smtp_port_entry.get(),
        "Application_Update_Cleanup": globals().get("blnUpdateCleanup"),
        "Application_Startup_Name": globals().get("strAutorunName"),
        "Application_Startup_Path": globals().get("strAutorunPath"),
        "Application_Theme": theme_radio_var.get(),
        "Application_Theme_Color": theme_color_radio_var.get(),
        "Dpi_Awareness": dpiawarenessoptionmenu_var.get(),
        "Application_Widget_Scaling": widgetscalingComboBox_var.get(),
        "Application_Window_Scaling": windowscalingComboBox_var.get(),
        "Application_Theme_Color_Path": globals().get("theme_profile_file_path"),
        "Restart_Interval_Switch": restart_interval_switch_var.get(),
        "Restart_Schedule_Switch": restartScheduleSwitch_var.get(),
        "Monitor_Interval_Switch": monitor_interval_switch_var.get(),
        "Backup_Interval_Switch": backupIntervalSwitch_var.get(),
        "Send_Email_Switch": send_email_switch_var.get(),
        "Send_Discord_Message_Switch": discordWebhookSwitch_var.get(),
        "Update_Server_Startup_Switch": update_server_startup_switch_var.get(),
        "Backup_Server_Switch": backup_server_switch_var.get(),
        "Delete_Old_Backups_Switch": deleteOldBackupsSwitch_var.get(),
        "Save_Interval_Switch": saveIntervalSwitch_var.get(),
        "Autorun_Application_Switch": autorun_application_switch_var.get()
    }
    try:
        with open(DEFAULT_SETTINGS_FILE, "w") as file:
            json.dump(settings, file)
    except Exception as exData:
        pass

def load_settings():
    try:
        with open(DEFAULT_SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            SettingsCounter = len(settings)
            if SettingsCounter == 13:
                append_to_output("Old Settings File detected. Attempting to recover settings...")
                restartEntry.insert(0, settings.get("restartEntry", ""))
                restartScheduleEntry.insert(0, settings.get("restartScheduleEntry", ""))
                ampm_optionmenu_var.set(settings.get("ampm_var", "AM"))
                monitorEntry.insert(0, settings.get("monitorEntry", ""))
                server_directory_selection.config(text=settings.get("server_directory_selection", "No directory selected"))
                arrcon_directory_selection.config(text=settings.get("arrcon_directory_selection", "No directory selected"))
                steamcmd_directory_selection.config(text=settings.get("steamcmd_directory_selection", "No directory selected"))
                backup_directory_selection.config(text=settings.get("backup_directory_selection", "No directory selected"))
                server_start_args_entry.insert(0, settings.get("server_start_args_entry", '-useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS -publiclobby'))
                email_address_entry.insert(0, settings.get("email_address_entry", ""))
                discordUrlEntry.insert(0, settings.get("discordUrlEntry", ""))
                smtp_server_entry.insert(0, settings.get("smtp_server_entry", "smtp.gmail.com"))
                smtp_port_entry.insert(0, settings.get("smtp_port_entry", "587"))
                return
            if not SettingsCounter == 37:
                append_to_output("Invalid Settings File. Attempting to recover settings...")
            restartEntry.insert(0, settings.get("Restart_Interval", ""))
            restartScheduleEntry.insert(0, settings.get("Scheduled_Restart_Time", ""))
            ampm_optionmenu_var.set(settings.get("Time_Format", "AM"))
            monitorEntry.insert(0, settings.get("Monitor_Interval", ""))
            backupIntervalEntry.insert(0, settings.get("Backup_Interval", ""))
            deleteOldBackupsEntry.insert(0, settings.get("Backups_Age_Limit", ""))
            saveIntervalEntry.insert(0, settings.get("Server_Save_Interval", ""))
            server_directory_selection.configure(text=settings.get("Server_Directory", "No Directory Selected"))
            arrcon_directory_selection.configure(text=settings.get("Arrcon_Directory", "No Directory Selected"))
            steamcmd_directory_selection.configure(text=settings.get("Steamcmd_Directory", "No Directory Selected"))
            backup_directory_selection.configure(text=settings.get("Backup_Directory", "No Directory Selected"))
            server_start_args_entry.insert(0, settings.get("Palworld_Start_Arguments", '-useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS -publiclobby'))
            email_address_entry.insert(0, settings.get("Email_Address", ""))
            email_password_entry.insert(0, settings.get("Email_Password", ""))
            discordUrlEntry.insert(0, settings.get("Discord_Webhook_URL", ""))
            smtp_server_entry.insert(0, settings.get("Smtp_Server", "smtp.gmail.com"))
            smtp_port_entry.insert(0, settings.get("Smtp_Port", "587"))
            globals()["blnUpdateCleanup"] = settings.get("Application_Update_Cleanup", "False")
            globals()["strAutorunName"] = settings.get("Application_Startup_Name", "")
            globals()["strAutorunPath"] = settings.get("Application_Startup_Path", "")
            theme_radio_var.set(settings.get("Application_Theme", "System"))
            theme_color_radio_var.set(settings.get("Application_Theme_Color", "blue"))
            dpiawarenessoptionmenu_var.set(settings.get("Dpi_Awareness", "Enabled"))
            widgetscalingComboBox_var.set(settings.get("Application_Widget_Scaling", "Default"))
            windowscalingComboBox_var.set(settings.get("Application_Window_Scaling", "Default"))
            globals()["theme_profile_file_path"] = settings.get("Application_Theme_Color_Path", "None")
            restart_interval_switch_var.set(settings.get("Restart_Interval_Switch", "False"))
            restartScheduleSwitch_var.set(settings.get("Restart_Schedule_Switch", "False"))
            monitor_interval_switch_var.set(settings.get("Monitor_Interval_Switch", "False"))
            backupIntervalSwitch_var.set(settings.get("Backup_Interval_Switch", "False"))
            send_email_switch_var.set(settings.get("Send_Email_Switch", "False"))
            discordWebhookSwitch_var.set(settings.get("Send_Discord_Message_Switch", "False"))
            update_server_startup_switch_var.set(settings.get("Update_Server_Startup_Switch", "False"))
            backup_server_switch_var.set(settings.get("Backup_Server_Switch", "False"))
            deleteOldBackupsSwitch_var.set(settings.get("Delete_Old_Backups_Switch", "False"))
            saveIntervalSwitch_var.set(settings.get("Save_Interval_Switch", "False"))
            autorun_application_switch_var.set(settings.get("Autorun_Application_Switch", "False"))
    except FileNotFoundError:
        append_to_output("First time startup. Applying default configuration")
        server_directory_selection.configure(text="No Directory Selected", text_color="red")
        arrcon_directory_selection.configure(text="No Directory Selected", text_color="red")
        steamcmd_directory_selection.configure(text="No Directory Selected", text_color="red")
        backup_directory_selection.configure(text="No Directory Selected", text_color="red")
        server_start_args_entry.insert(0, '-useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS -publiclobby')
        smtp_server_entry.insert(0, "smtp.gmail.com")
        smtp_port_entry.insert(0, "587")
    except json.JSONDecodeError:
        append_to_output("Invalid Settings File. Applying default configuration")
        server_directory_selection.configure(text="No Directory Selected", text_color="red")
        arrcon_directory_selection.configure(text="No Directory Selected", text_color="red")
        steamcmd_directory_selection.configure(text="No Directory Selected", text_color="red")
        backup_directory_selection.configure(text="No Directory Selected", text_color="red")
        server_start_args_entry.insert(0, '-useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS -publiclobby')
        smtp_server_entry.insert(0, "smtp.gmail.com")
        smtp_port_entry.insert(0, "587")
    if os.path.isfile(OLD_SETTINGS_FILE):
        load_old_settings()

def load_old_settings():
    try:
        with open(OLD_SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            append_to_output("Old Settings File detected. Attempting to recover settings...")
            restartEntry.insert(0, settings.get("restartEntry", ""))
            restartScheduleEntry.insert(0, settings.get("restartScheduleEntry", ""))
            ampm_optionmenu_var.set(settings.get("ampm_var", "AM"))
            monitorEntry.insert(0, settings.get("monitorEntry", ""))
            server_directory_selection.config(text=settings.get("server_directory_selection", "No directory selected"))
            arrcon_directory_selection.config(text=settings.get("arrcon_directory_selection", "No directory selected"))
            steamcmd_directory_selection.config(text=settings.get("steamcmd_directory_selection", "No directory selected"))
            backup_directory_selection.config(text=settings.get("backup_directory_selection", "No directory selected"))
            server_start_args_entry.insert(0, settings.get("server_start_args_entry", '-useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS -publiclobby'))
            email_address_entry.insert(0, settings.get("email_address_entry", ""))
            discordUrlEntry.insert(0, settings.get("discordUrlEntry", ""))
            smtp_server_entry.insert(0, settings.get("smtp_server_entry", "smtp.gmail.com"))
            smtp_port_entry.insert(0, settings.get("smtp_port_entry", "587"))
        append_to_output("Now deleting old settings file...")
        shutil.rmtree(os.path.join(os.path.expanduser("~"), "Documents/Palworld Server Manager"))
    except Exception as exData:
        pass

def load_theme_settings():
    if os.path.isfile(DEFAULT_SETTINGS_FILE):
        try:
            with open(DEFAULT_SETTINGS_FILE, "r") as file:
                settings = json.load(file)
                Application_Theme = settings.get("Application_Theme", "System")
                Application_Theme_Color = settings.get("Application_Theme_Color", "blue")
                Application_DPI_Awareness = settings.get("Dpi_Awareness", "Enabled")
                Application_Widget_Scaling = settings.get("Application_Widget_Scaling", "Default")
                Application_Window_Scaling = settings.get("Application_Window_Scaling", "Default")
                Application_Theme_Color_Path = settings.get("Application_Theme_Color_Path", "None")
        except:
            pass
        if Application_Theme in ["System", "Dark", "Light"]:
            ctk.set_appearance_mode(Application_Theme)
            if Application_Theme_Color == "custom" and Application_Theme_Color_Path != "None":
                if os.path.isfile(Application_Theme_Color_Path):
                    ctk.set_default_color_theme(Application_Theme_Color_Path)
                else:
                    globals()["intForcedThemeColorChange"] = 1
                    globals()["theme_profile_file_path"] = "None"
                    ctk.set_default_color_theme("blue")
            elif Application_Theme_Color in ["blue", "dark-blue", "green"]:
                ctk.set_default_color_theme(Application_Theme_Color)
            if Application_DPI_Awareness == "Disabled":
                    ctk.deactivate_automatic_dpi_awareness()
            if not Application_Widget_Scaling == "Default":
                if not "%" in Application_Widget_Scaling:
                    Application_Widget_Scaling += " %"
                try:
                    Application_Widget_Scaling = int(Application_Widget_Scaling.replace("%", "")) / 100
                    ctk.set_widget_scaling(Application_Widget_Scaling)
                except:
                    globals()["intForcedWidgetScalingChange"] = 1
            if not Application_Window_Scaling == "Default":
                if not "%" in Application_Window_Scaling:
                    Application_Window_Scaling += " %"
                try:
                    Application_Window_Scaling_Float = int(Application_Window_Scaling.replace("%", "")) / 100
                    ctk.set_window_scaling(Application_Window_Scaling_Float)
                except:
                    globals()["intForcedWindowScalingChange"] = 1

def load_widget_settings():
    try:
        with open(DEFAULT_SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            Application_Theme_Color = settings.get("Application_Theme_Color", "blue")
            if Application_Theme_Color == "custom":
                theme_file_button.configure(state="normal")
    except:
        pass
    if intForcedThemeColorChange == 1:
        blueradiobutton.select()
        theme_file_button.configure(state="disabled")
    if intForcedWidgetScalingChange == 1:
        widgetscalingComboBox_var.set("Default")
    if intForcedWindowScalingChange == 1:
        windowscalingComboBox_var.set("Default")
    network_status_info()
    search_file(server_directory_selection.cget("text"), "PalServer.exe")
    search_file(arrcon_directory_selection.cget("text"), "ARRCON.exe")
    search_file(steamcmd_directory_selection.cget("text"), "SteamCMD.exe")
    search_file(steamcmd_directory_selection.cget("text"), "backup_directory")
    get_server_info(server_directory_selection.cget("text"))
    server_status_info()

#Save settings when exiting app
def on_exit():
    save_settings()
    root.destroy()

#commands used to save palworld server.
arrcon_command_save_server = None
arrcon_command_info_server = None
arrcon_command_shutdown_server = None
arrcon_command_server_message_30 = None
arrcon_command_server_message_10 = None
update_palworld_server_command = None
update_palworld_then_start_server_command = None
shutdown_server_command = None
force_shutdown_server_command = None

#define variables used in functions
send_email_checked = False
discord_message_checked = False
update_server_on_startup = False
enable_backups = False
start_server_clicked = False
after_id = None
monitor_after_id = None
current_function = None
scheduled_time = None
save_after_id = None
strAutorunName = None
strAutorunPath = None
blnUpdateCleanup = False
blnSettingsFileSameDirectory = False
intForcedThemeColorChange = 0
intForcedWidgetScalingChange = 0
intForcedWindowScalingChange = 0

def run_at_startup_set(appname, path=None, user=True):
    """
    Store the entry in the registry for running the application
    at startup.
    """
    # Open the registry key where applications that run
    # at startup are stored.
    key = RegOpenKeyEx(HKEY_CURRENT_USER if user else HKEY_LOCAL_MACHINE, STARTUP_KEY_PATH, 0, KEY_WRITE | KEY_QUERY_VALUE)
    # Make sure our application is not already in the registry.
    i = 0
    while True:
        try:
            name, _, _ = RegEnumValue(key, i)
        except pywintypes.error as e:
            if e.winerror == ERROR_NO_MORE_ITEMS:
                break
            else:
                raise
        if name == appname:
            RegCloseKey(key)
            return
        i += 1
    # Create a new entry or key.
    RegSetValueEx(key, appname, 0, REG_SZ, path or GetModuleFileName(0))
    # Close the key when no longer used.
    RegCloseKey(key)

def run_at_startup_remove(appname, user=True):
    """
    Remove the registry application passed in the first param.
    """
    key = RegOpenKeyEx(HKEY_CURRENT_USER if user else HKEY_LOCAL_MACHINE, STARTUP_KEY_PATH, 0, KEY_WRITE)
    RegDeleteValue(key, appname)
    RegCloseKey(key)

def center_window_to_parent(window: ctk):
    """Centers the window to the main tkinter window"""
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    window_X = window.winfo_x()
    window_Y = window.winfo_y()
    x = int(window_X + (screen_width - window_width) // 2)
    y = int(window_Y + (screen_height - window_height) // 2)
    window.geometry(f"+{x}+{y}")

def center_window(window: ctk):
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = int((screen_width // 2) - (window_width // 2))
    y = int((screen_height // 2) - (window_height // 2))
    window.geometry(f"+{x}+{y}")

def update_commands():
    global arrcon_command_save_server, arrcon_command_shutdown_server, arrcon_command_server_message_30, arrcon_command_server_message_10, start_server_command, shutdown_server_command, rcon_pass, force_shutdown_server_command, arrcon_command_info_server
    try:
        arrcon_exe_path = f'{arrcon_directory_selection.cget("text")}/ARRCON.exe'
        rcon_getport = rcon_port.cget("text")
        palworld_directory = server_directory_selection.cget("text")
        server_start_args = server_start_args_entry.get()
        arrcon_command_save_server = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "save"'
        arrcon_command_info_server = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "info"'
        arrcon_command_shutdown_server = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "shutdown 60 The_server_will_be_restarting_in_60_seconds"'
        arrcon_command_server_message_30 = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "broadcast The_server_will_be_restarting_in_30_seconds"'
        arrcon_command_server_message_10 = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "broadcast The_server_will_be_restarting_in_10_seconds"'
        start_server_command = f'{palworld_directory}/PalServer.exe {server_start_args}'
        shutdown_server_command = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "shutdown 5 The_server_will_be_shutting_down_in_5_seconds"'
        force_shutdown_server_command = f'{arrcon_exe_path} -H 127.0.0.1 -P {rcon_getport} -p {rcon_pass} "doexit"'
        return "commands updated"
    except Exception as exData:
        append_to_output(f"There was an issue creating the ARRCON commands and server startup command. Error: " + str(exData))

# Function that sends message to output window
def append_to_output(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    formatted_message = timestamp + message
    output_text.configure(state="normal")
    output_text.insert('end', formatted_message + "\n")
    output_text.yview('end')  # Auto-scroll to the bottom
    output_text.configure(state="disabled")

def get_public_ip():
    try:
        response = requests.get("http://ipv4.icanhazip.com")
        return response.text.strip()
    except Exception as exData:
        append_to_output(f"There was an issue getting your public IP. Error: " + str(exData))
        return "Offline"

def operating_mode():
    """
    Detects if the script is running as an executable or a script.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return True
    else:
        # Running as a script
        return False

def network_status_info():
    server_interal_ip = socket.gethostbyname(socket.gethostname())
    if server_interal_ip == "127.0.0.1":
        server_interal_ip = "Offline"
    server_interal_ip_state_label.configure(text=server_interal_ip)
    server_external_ip = get_public_ip()
    server_external_ip_state_label.configure(text=server_external_ip)

def server_status_info():
    task_name = "PalServer-Win64-Shipping-Cmd.exe"
    try:
        running_processes = [proc.name() for proc in psutil.process_iter()]
    except Exception as exServerStatus:
        append_to_output(f"There was an issue checking whats running on your server. Error: " + str(exData))
    if task_name in running_processes:
        results = server_check_update_commands()
        if results == "good":
            try:
                process = subprocess.Popen(arrcon_command_info_server, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                stdout = process.communicate()

                if process.returncode == 0:
                    if isinstance(stdout, tuple):
                        stdout = stdout[0]

                        # Check if stdout is not None and is a string before splitting
                        if stdout and isinstance(stdout, str):
                            output_lines = stdout.splitlines()

                            # Extract the server version using a regular expression
                            version_pattern = re.compile(r'Welcome to Pal Server\[v([\d.]+)\]')
                            match = version_pattern.search(output_lines[1])

                            if match:
                                server_version = match.group(1)
                                server_version_state_label.configure(text=server_version)
                                server_status_state_label.configure(text="Online", text_color="green")
                                root.after(60000, server_status_info)
                            else:
                                server_version_state_label.configure(text="Unknown")
                                server_status_state_label.configure(text="Online", text_color="green")
                                root.after(60000, server_status_info)
                        else:
                            server_version_state_label.configure(text="Unknown")
                            server_status_state_label.configure(text="Online", text_color="green")
                            root.after(60000, server_status_info)
                else:
                    server_version_state_label.configure(text="Unknown")
                    server_status_state_label.configure(text="Offline", text_color="red")
                    root.after(60000, server_status_info)
            except subprocess.CalledProcessError as exData:
                server_status_state_label.configure(text="Offline", text_color="red")
                server_version_state_label.configure(text="Unknown")
                append_to_output("Unable to update server info due to error: "+ str(exData))
                root.after(60000, server_status_info)
        else:
            root.after(60000, server_status_info)
    else:
        server_status_state_label.configure(text="Offline", text_color="red")
        server_version_state_label.configure(text="Unknown")
        root.after(60000, server_status_info)

def save_server():
    append_to_output("Saving Palworld Server...")
    root.update()
    try:
        subprocess.Popen(arrcon_command_save_server)
        append_to_output("Palworld server was saved successfully...")
    except Exception as exData:
        append_to_output(f"Couldn't save the server due to error: " + str(exData))

def shutdown_server(type):
    if type == "graceful":
        try:
            subprocess.Popen(shutdown_server_command)
        except Exception as exData:
            append_to_output(f"Couldn't shutdown the server due to error: " + str(exData))
    if type == "force":
        try:
            subprocess.Popen(force_shutdown_server_command)
        except Exception as exData:
            append_to_output(f"Couldn't shutdown the server due to error: " + str(exData))

# Function to save the server during the restart interval
def save_server_interval(restartinterval):
    global after_id, current_function, scheduled_time
    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        current_function = "save_server_interval"
        append_to_output("Saving Palworld Server...")
        try:
            subprocess.Popen(arrcon_command_save_server)
        except Exception as exData:
            append_to_output(f"Couldn't save the server due to error: " + str(exData))
        append_to_output("Palworld server was saved successfully...")
        scheduled_time = time.time() + 5  # Store the scheduled time (5 seconds in the future)
        after_id = root.after(5000, lambda: shutdown_server_interval(restartinterval))
    else:
        current_function = "save_server_interval"
        scheduled_time = time.time() + restartinterval
        trueRestartTime = int(restartinterval / 1000 / 60 / 60)
        append_to_output(f"The Restart interval attempted to run, but the server is not running. This will automatically retry in {trueRestartTime} hour(s)")
        root.after(restartinterval, lambda: save_server_interval(restartinterval))

def shutdown_server_interval(restartinterval):
    global after_id, current_function, scheduled_time
    current_function = "shutdown_server"
    append_to_output("Shutting Down Palworld Server...")
    try:
        subprocess.Popen(arrcon_command_shutdown_server)
        append_to_output("The server will go down in 60 seconds...")
        scheduled_time = time.time() + 70  # Store the scheduled time (30 seconds in the future)
        after_id = root.after(30000, lambda: message_server_30(restartinterval))
    except Exception as exData:
        current_function = ""
        append_to_output(f"Couldn't shutdown the server due to error: " + str(exData))

def scheduled_shutdown_server():
    global after_id, current_function, scheduled_time
    current_function = "shutdown_server"
    append_to_output("Shutting Down Palworld Server...")
    try:
        subprocess.Popen(arrcon_command_shutdown_server)
        append_to_output("The server will go down in 60 seconds...")
        scheduled_time = time.time() + 70  # Store the scheduled time (30 seconds in the future)
        after_id = root.after(30000, scheduled_message_server_30)
    except Exception as exData:
        current_function = ""
        append_to_output(f"Couldn't shutdown the server due to error: " + str(exData))

def message_server_30(restartinterval):
    global after_id, current_function, scheduled_time
    current_function = "message_server_30"
    subprocess.Popen(arrcon_command_server_message_30)
    after_id = root.after(20000, lambda: message_server_10(restartinterval))

def scheduled_message_server_30():
    global after_id, current_function, scheduled_time
    current_function = "message_server_30"
    subprocess.Popen(arrcon_command_server_message_30)
    after_id = root.after(20000, scheduled_message_server_10)

def message_server_10(restartinterval):
    global after_id, current_function, scheduled_time
    current_function = "message_server_10"
    try:
        subprocess.Popen(arrcon_command_server_message_10)
    except Exception as exData:
        append_to_output(f"Couldn't send message to the server due to error: " + str(exData))
    after_id = root.after(20000, lambda: restart_server(restartinterval))

def scheduled_message_server_10():
    global after_id, current_function, scheduled_time
    current_function = "message_server_10"
    try:
        subprocess.Popen(arrcon_command_server_message_10)
        after_id = root.after(20000, scheduled_restart_server)
    except Exception as exData:
        append_to_output(f"Couldn't send message to the server due to error: " + str(exData))

def restart_server(restartinterval):
    global after_id, current_function, scheduled_time
    current_function = "restart_server"
    append_to_output("Palworld Server is shutdown. Checking for residual processes... Sometimes the server process gets stuck")
    root.update()
    if enable_backups == True:
            backup_server()

    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        append_to_output(f"Task {task_name} is still running. Ending the process...")
    
        # Find the process by name and terminate it
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == task_name:
                psutil.Process(proc.info['pid']).terminate()
        root.update()
        time.sleep(3)
        append_to_output("Process ended. Starting the server back up...")
        root.update()
        if update_server_startup_switch_var.get():
            results = update_palworld_server()
            if results == "server updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                root.after(3000, check_palworld_process)
                scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
                after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
                trueRestartTime = int(restartinterval / 1000 / 60 / 60)
                append_to_output(f"The server will restart again in {trueRestartTime} hours")
                current_function = None
            elif results == "server not updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                root.after(3000, check_palworld_process)
                scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
                after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
                trueRestartTime = int(restartinterval / 1000 / 60 / 60)
                append_to_output(f"The server will restart again in {trueRestartTime} hours")
                current_function = None
        else:
            append_to_output("Starting server...")
            try:
                subprocess.Popen(start_server_command)
            except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
            root.after(3000, check_palworld_process)
            scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
            after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
            trueRestartTime = int(restartinterval / 1000 / 60 / 60)
            append_to_output(f"The server will restart again in {trueRestartTime} hours")
            current_function = None
    else:
        append_to_output(f"Task {task_name} is not running. Starting the server back up...")
        if update_server_startup_switch_var.get():
            results = update_palworld_server()
            if results == "server updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                root.after(3000, check_palworld_process)
                scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
                after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
                trueRestartTime = int(restartinterval / 1000 / 60 / 60)
                append_to_output(f"The server will restart again in {trueRestartTime} hours")
                current_function = None
            elif results == "server not updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                root.after(3000, check_palworld_process)
                scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
                after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
                trueRestartTime = int(restartinterval / 1000 / 60 / 60)
                append_to_output(f"The server will restart again in {trueRestartTime} hours")
                current_function = None
        else:
            append_to_output("Starting server...")
            try:
                subprocess.Popen(start_server_command)
            except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
            root.after(3000, check_palworld_process)
            scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
            after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
            trueRestartTime = int(restartinterval / 1000 / 60 / 60)
            append_to_output(f"The server will restart again in {trueRestartTime} hours")
            current_function = None

def scheduled_restart_server():
    global after_id, current_function, scheduled_time
    current_function = "restart_server"
    append_to_output("Palworld Server is shutdown. Checking for residual processes... Sometimes the server process gets stuck")
    root.update()
    if enable_backups == True:
            backup_server()

    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        append_to_output(f"Task {task_name} is still running. Ending the process...")
    
        # Find the process by name and terminate it
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == task_name:
                psutil.Process(proc.info['pid']).terminate()
        root.update()
        time.sleep(3)
        append_to_output("Process ended. Starting the server back up...")
        root.update()
        if update_server_startup_switch_var.get():
            results = update_palworld_server()
            if results == "server updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                    root.after(3000, check_palworld_process)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                current_function = None
            elif results == "server not updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                    root.after(3000, check_palworld_process)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                current_function = None
        else:
            append_to_output("Starting server...")
            try:
                subprocess.Popen(start_server_command)
                root.after(3000, check_palworld_process)
            except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
            current_function = None
    else:
        append_to_output(f"Task {task_name} is not running. Starting the server back up...")
        if update_server_startup_switch_var.get():
            results = update_palworld_server()
            if results == "server updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                    root.after(3000, check_palworld_process)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                current_function = None
            elif results == "server not updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                    root.after(3000, check_palworld_process)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                current_function = None
        else:
            append_to_output("Starting server...")
            try:
                subprocess.Popen(start_server_command)
                root.after(3000, check_palworld_process)
            except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
            current_function = None

def kill_palworld_process():
    append_to_output("Palworld Server is shutdown. Checking for residual processes... Sometimes the server process gets stuck")
    root.update()

    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        append_to_output(f"Task {task_name} is still running. Ending the process...")
        root.update()
    
        # Find the process by name and terminate it
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == task_name:
                psutil.Process(proc.info['pid']).terminate()
                append_to_output("PalServer.exe is no longer running...")
    else:
        append_to_output("PalServer.exe is not running. The server is completely shutdown")

def check_palworld_process():
    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        append_to_output("Server is now running")

def send_email():
    email_from = email_address_entry.get()
    email_to = email_address_entry.get()
    subject = "Palworld Server Crash"
    body = "This email indicates that the Palworld server was not running. No worries though. The server was restarted. Beep beep boop."

    smtp_server = smtp_server_entry.get()
    smtp_port = smtp_port_entry.get()
    smtp_user = email_address_entry.get()
    smtp_password = email_password_entry.get()

    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    # Attach the body of the email
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to the email account
        server.login(smtp_user, smtp_password)

        # Send the email
        server.sendmail(email_from, email_to, msg.as_string())

        append_to_output("Sent notification email successfully.")

    except Exception as exData:
        append_to_output(f"Notification email was not sent successfully due to error: " + str(exData))
        send_email_switch.deselect()

    finally:
        # Disconnect from the SMTP server
        server.quit()

def send_discord_message():
    webhook_url = discordUrlEntry.get()
    message = 'This message indicates that the Palworld server was not running. No worries though, the server was restarted and is back online. Beep beep boop.'
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Check for HTTP errors

        append_to_output("Discord alert was sent")
    except requests.exceptions.RequestException as exData:
        append_to_output(f"Error sending Discord alert: {exData}")

def monitor_server(monitorinterval):
    global monitor_after_id
    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        monitor_after_id = root.after(monitorinterval, lambda: monitor_server(monitorinterval))
    elif current_function == "shutdown_server" or current_function == "message_server_30" or current_function == "message_server_10" or current_function == "restart_server":
        monitor_after_id = root.after(monitorinterval, lambda: monitor_server(monitorinterval))
    else:
        if update_server_startup_switch_var.get():
            results = update_palworld_server()
            if results == "server updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                if send_email_checked == True:
                    send_email()
                if discord_message_checked == True:
                    send_discord_message()
                monitor_after_id = root.after(monitorinterval, lambda: monitor_server(monitorinterval))
            elif results == "server not updated":
                append_to_output("Starting server...")
                try:
                    subprocess.Popen(start_server_command)
                except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
                if send_email_checked == True:
                    send_email()
                if discord_message_checked == True:
                    send_discord_message()
                monitor_after_id = root.after(monitorinterval, lambda: monitor_server(monitorinterval))
        else:
            append_to_output("Starting server...")
            try:
                subprocess.Popen(start_server_command)
            except Exception as exData:
                    append_to_output(f"Couldn't start the server due to error: " + str(exData))
            if send_email_checked == True:
                send_email()
            if discord_message_checked == True:
                send_discord_message()
            monitor_after_id = root.after(monitorinterval, lambda: monitor_server(monitorinterval))

def enable_monitor_server():
    global monitor_after_id
    server_check_results = server_check()
    if server_check_results == "check good":
        update_commands_results = update_commands()
        if update_commands_results == "commands updated":
            try:
                if monitor_interval_switch_var.get():
                    monitorinterval = int(monitorEntry.get()) * 60 * 1000  # Convert to minutes and then translate to milliseconds
                    true_value = int(monitorinterval / 1000 / 60)
                    append_to_output(f"Monitor Interval has been enabled. The monitor will check every {true_value} minute(s) to ensure the server is running.")
                    monitor_after_id = root.after(monitorinterval, lambda: monitor_server(monitorinterval))
                else:
                    disable_monitor_server()
            except ValueError:
                append_to_output("Your monitor interval cannot be empty and can only contain numerical values")
                monitor_interval_switch.deselect()
    else:
        append_to_output("Server check failed. Check your Settings before attempting this again and be sure everything is configured first.")
        monitor_interval_switch.deselect()

def enable_save_interval():
    global save_after_id
    server_check_results = server_check()
    if server_check_results == "check good":
        try:
            if saveIntervalSwitch_var.get():
                saveInterval = int(saveIntervalEntry.get()) * 60 * 1000  # Convert to minutes and then translate to milliseconds
                true_value = int(saveInterval / 1000 / 60)
                append_to_output(f"Server Save Interval has been enabled. The server will be backed up every {true_value} minute(s)")
                save_after_id = root.after(saveInterval, save_server())
            else:
                root.after_cancel(backup_after_id)
                append_to_output("Server Save Interval has been disabled.")
        except ValueError:
                append_to_output("Your server save interval cannot be empty and can only contain numerical values")
                backupIntervalSwitch.deselect()
    else:
        append_to_output("Server check failed. Check your Settings before attempting this again and be sure everything is configured first.")
        saveIntervalSwitch.deselect()

def disable_monitor_server():
    global monitor_after_id
    try:
        if monitor_interval_switch_var.get() == False:
            if monitor_after_id:
                root.after_cancel(monitor_after_id)
                monitor_after_id = None  # Reset id to None
                append_to_output("Monitor interval was disabled.")
    except Exception as exData:
        append_to_output("There was an error disabling the monitor interval due to error: " + str(exData))

def enable_server_restart():
    global after_id, current_function, scheduled_time
    server_check_results = server_check()
    if server_check_results == "check good":
        update_commands_results = update_commands()
        if update_commands_results == "commands updated":
            if restartScheduleSwitch_var.get() == False:
                try:
                    if restart_interval_switch_var.get():
                        restartinterval = int(restartEntry.get()) * 60 * 60 * 1000  # Convert to minutes then hours and then translate to milliseconds
                        true_value = int(restartinterval / 1000 / 60 / 60)
                        append_to_output(f"Server Restart Interval has been enabled. The server will restart in {true_value} hour(s)")
                        current_function = "enable_server_restart"
                        scheduled_time = time.time() + restartinterval  # Store the scheduled time (restartinterval seconds in the future)
                        after_id = root.after(restartinterval, lambda: save_server_interval(restartinterval))
                    else:
                        disable_server_restart()
                except ValueError:
                    append_to_output("Your restart interval cannot be empty and can only contain numerical values")
                    restart_interval_switch.deselect()
            else:
                append_to_output("Scheduled Restarts is already Enabled. You cannot use this both of these features at the same time.")
                messagebox.showwarning("Warning", "Scheduled Restarts is already Enabled. You cannot use this both of these features at the same time.")
                restart_interval_switch.deselect()
    else:
        append_to_output("Server check failed. Check your Settings before attempting this again and be sure everything is configured first.")
        restart_interval_switch.deselect()

def disable_server_restart():
    global after_id
    try:
        if restart_interval_switch_var.get() == False:
            if after_id:
                root.after_cancel(after_id)
                after_id = None  # Reset after_id to None
                append_to_output("Server restart interval stopped.")
    except Exception as exData:
        append_to_output("There was an error disabling the server restart interval due to error: " + str(exData))

def backup_server_interval(backupInterval):
    global backup_after_id
    backup_server()
    backup_after_id = root.after(backupInterval, lambda: backup_server_interval(backupInterval))

def enable_backup_interval():
    global backup_after_id
    server_check_results = server_check()
    if server_check_results == "check good":
        if not backup_directory_selection.cget("text") == "No Directory Selected":
            try:
                if backupIntervalSwitch_var.get():
                    backupInterval = int(backupIntervalEntry.get()) * 60 * 60 * 1000  # Convert to minutes and then to hours and then translate to milliseconds
                    true_value = int(backupInterval / 1000 / 60 / 60)
                    append_to_output(f"Backup Interval has been enabled. The server will be backed up every {true_value} hour(s)")
                    backup_after_id = root.after(backupInterval, lambda: backup_server_interval(backupInterval))
                else:
                    root.after_cancel(backup_after_id)
                    append_to_output("Backup Interval has been disabled.")
            except ValueError:
                append_to_output("Your backup interval cannot be empty and can only contain numerical values")
                backupIntervalSwitch.deselect()
        else:
            append_to_output("You must select a valid backup directory before using this feature")
            backupIntervalSwitch.deselect()
    else:
        append_to_output("Server check failed. Check your Settings before attempting this again and be sure everything is configured first.")
        backupIntervalSwitch.deselect()

def start_scheduler():
    schedule.run_pending()
    root.after(1000, start_scheduler)

def scheduled_server_restart():
    append_to_output("Scheduled server restart executed at: " + time.strftime("%H:%M:%S"))
    root.update()
    save_server()
    root.after(3000, scheduled_shutdown_server)

def enable_scheduled_restart():
    global after_id, current_function, scheduled_time, restartServerJob
    server_check_results = server_check()
    if server_check_results == "check good":
        update_commands_results = update_commands()
        if update_commands_results == "commands updated":
            if restartScheduleSwitch_var.get():
                if restart_interval_switch_var.get() == False:
                    timeEntry = restartScheduleEntry.get()
                    if not timeEntry == "":
                        timeEntry = restartScheduleEntry.get()
                        timeInputCheck = validate_time_input(timeEntry)
                        if timeInputCheck == "time good":
                            timeEntry = str(restartScheduleEntry.get() + " " + ampm_optionmenu_var.get())
                            strptimeEntry = datetime.strptime(timeEntry, "%I:%M %p")
                            milTimeEntry = strptimeEntry.strftime("%H:%M")
                            restartServerJob = schedule.every().day.at(milTimeEntry).do(scheduled_server_restart)
                            start_scheduler()
                            append_to_output(f"Your server will now restart every day at {timeEntry}")
                        else:
                            append_to_output('Time entry is invalid. Please make sure to follow the proper 12 hour format.')
                            append_to_output('Example 12-hour Format: 1:25PM')
                            restartScheduleSwitch.deselect()
                    else:
                        append_to_output('Time entry is empty')
                        append_to_output('Example 12-hour Format: 1:25PM')
                        restartScheduleSwitch.deselect()
                else:
                    append_to_output("Restart Intervals is already Enabled. You cannot use this both of these features at the same time.")
                    messagebox.showwarning("Warning", "Restart Intervals is already Enabled. You cannot use this both of these features at the same time.")
                    restartScheduleSwitch.deselect()
            elif restartScheduleSwitch_var.get() == False:
                schedule.cancel_job(restartServerJob)
                append_to_output("Disabled scheduled restarts")
    else:
        append_to_output("Server check failed. Check your Settings before attempting this again and be sure everything is configured first.")
        restartScheduleSwitch.deselect()

def enable_send_email():
    global send_email_checked
    if send_email_switch_var.get():
        if monitor_interval_switch_var.get():
            if email_address_entry.get() and email_password_entry.get() and smtp_server_entry.get() and smtp_port_entry.get():
                send_email_checked = True
                append_to_output("Email notifications have been enabled")
            else:
                append_to_output("Be sure to fill out all of the information required in the Notifications page")
                messagebox.showwarning("Invalid Email Information", "1 or more fields are missing in the Notifications page")
                send_email_switch.deselect()
        else:
            append_to_output("You cannot enable this feature while Monitor Interval is disabled")
            messagebox.showinfo("Monitor Interval Disabled", "You cannot enable this feature while Monitor Interval is disabled")
            send_email_switch.deselect()
    else:
        disable_send_email()

def disable_send_email():
    global send_email_checked
    if send_email_switch_var.get() == False:
        send_email_checked = False
        append_to_output("Email notifications have been disabled")

def enable_send_discord_message():
    global discord_message_checked
    if discordWebhookSwitch_var.get():
        if monitor_interval_switch_var.get():
            if discordUrlEntry.get():
                discord_message_checked = True
                append_to_output("Discord alerts have been Enabled")
            else:
                append_to_output("Be sure to enter a Discord Webhook URL in the Notifications page.")
                messagebox.showwarning("Invalid Discord Webhook URL", "You need to enter a Discord Webhook URL in the Notifications page")
                discordWebhookSwitch.deselect()
        else:
            append_to_output("You cannot enable this feature while Monitor Interval is disabled")
            messagebox.showinfo("Monitor Interval Disabled", "You cannot enable this feature while Monitor Interval is disabled")
            discordWebhookSwitch.deselect()
    elif discordWebhookSwitch_var.get() == False:
        discord_message_checked = False
        append_to_output("Discord alerts have been Disabled")

def enable_server_updates_on_startup():
    global update_server_on_startup
    if update_server_startup_switch_var.get():
        if palworld_exe_result_label.cget("text") == "PalServer.exe detected":
            if steamcmd_exe_result_label.cget("text") == "SteamCMD.exe detected":
                update_commands()
                update_server_on_startup = True
                append_to_output("Check for updates on startup has been Enabled")
            else:
                append_to_output("You must select a valid Steamcmd Directory to use this function. Check your Settings before attempting this again")
                messagebox.showwarning("Invalid Directory", "You must select a valid Steamcmd directory to use this function")
                update_server_startup_switch.deselect()
        else:
            append_to_output("You must select a valid Palworld Server Directory to use this function. Check your Settings before attempting this again")
            messagebox.showwarning("Invalid Directory", "You must select a valid Palworld Server directory to use this function")
            update_server_startup_switch.deselect()
    elif update_server_startup_switch_var.get() == False:
        update_server_on_startup = False
        append_to_output("Check for updates on startup has been Disabled")

def enable_server_backups():
    global enable_backups
    if backup_server_switch_var.get():
        if not palworld_exe_result_label.cget("text") == "PalServer.exe not found":
            if not backup_directory_selection.cget("text") == "No Directory Selected":
                enable_backups = True
                append_to_output("Server backups have been Enabled")
            else:
                append_to_output("You need to select a directory where your backups will reside. Check your Settings before attempting this again")
                messagebox.showwarning("Invalid Directory", "You have not selected a backup directory. Check your Settings before attempting this again")
                backup_server_switch.deselect()
        else:
            append_to_output("PalServer.exe was not detected in your selected directory. Check your Settings before attempting this again")
            messagebox.showwarning("Invalid Directory", "PalServer.exe was not found in the selected directory. Check your Settings before attempting this again")
            backup_server_switch.deselect()
    elif backup_server_switch_var.get() == False:
        enable_backups = False
        append_to_output("Server backups have been Disabled")

def enable_delete_backups():
    if deleteOldBackupsEntry.get() == "":
        append_to_output('Please enter a number of days to delete old backups.')
        messagebox.showwarning("Invalid Input", 'Please enter a number of days to delete old backups.')
        deleteOldBackupsSwitch.deselect()
    elif deleteOldBackupsSwitch_var.get() == False:
        append_to_output("Old backups will no longer be deleted.")
    else:
        try:
            value = int(deleteOldBackupsEntry.get())
            append_to_output(f"Backups older than {value} day will now be deleted whenever new backups are created")
        except ValueError:
            append_to_output('Only numbers are allowed')
            messagebox.showwarning("Invalid Input", 'Only numbers are allowed')
            deleteOldBackupsSwitch.deselect()

def delete_old_backups():
    current_time = datetime.now()
    daysEntry = int(deleteOldBackupsEntry.get())
    append_to_output(str(daysEntry))

    days_ago = current_time - timedelta(days=daysEntry)

    backup_dir = backup_directory_selection.cget("text")

    for filename in os.listdir(backup_dir):
        if filename.startswith("palworld_backup_"):
            filepath = os.path.join(backup_dir, filename)
        
            modification_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        
            if modification_time < days_ago:
                os.remove(filepath)
                append_to_output(f"Old backup deleted: {filepath}")

def backup_server():
    if not palworld_exe_result_label.cget("text") == "PalServer.exe not found":
        if not backup_directory_selection.cget("text") == "No Directory Selected":
            palworld_directory = server_directory_selection.cget("text")
            backup_dir = backup_directory_selection.cget("text")
            source_dir = f"{palworld_directory}/Pal/Saved/SaveGames/0"

            # Create the backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)

            # Get the current date and time
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Compose the backup file path
            backup_file_path = os.path.join(backup_dir, f"palworld_backup_{current_datetime}.zip")

            files_to_backup = []
            for root, dirs, files in os.walk(source_dir):
                files_to_backup.extend(os.path.join(root, file) for file in files)

            if files_to_backup:
                with zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_dir)
                            zip_archive.write(file_path, arcname=arcname)

            # append_to_output a message indicating the completion of the backup
            append_to_output(f"Backup of {source_dir} completed at {backup_file_path}")
            if deleteOldBackupsSwitch_var.get():
                delete_old_backups()
        else:
            append_to_output("You must select a Backup Directory to use this function. Check your Settings before attempting this again")
            messagebox.showwarning("Invalid Directory", "You must select a valid Backup directory to use this function")
    else:
        append_to_output("You must select a valid Palworld Server Directory to use this function. Check your Settings before attempting this again")
        messagebox.showwarning("Invalid Directory", "You must select a valid Palworld Server directory to use this function")

def start_server():
    server_check_results = server_check()
    if server_check_results == "check good":
        update_commands_results = update_commands()
        if update_commands_results == "commands updated":
            task_name = "PalServer-Win64-Shipping-Cmd.exe"

            # Get the list of running processes
            running_processes = [proc.name() for proc in psutil.process_iter()]

            # Check if the process is in the list
            if task_name in running_processes:
                append_to_output("Server is already running... nothing to do")
            else:
                if update_server_startup_switch_var.get():
                    results = update_palworld_server()
                    if results == "server updated":
                        append_to_output("Starting server...")
                        try:
                            subprocess.Popen(start_server_command)
                        except Exception as exData:
                            append_to_output("There was an issue starting the server due to error: " + str(exData))
                        root.after(3000, check_palworld_process)
                    elif results == "server not updated":
                        append_to_output("Starting server...")
                        try:
                            subprocess.Popen(start_server_command)
                        except Exception as exData:
                            append_to_output("There was an issue starting the server due to error: " + str(exData))
                        root.after(3000, check_palworld_process)
                else:
                    append_to_output("Starting server...")
                    try:
                        subprocess.Popen(start_server_command)
                    except Exception as exData:
                        append_to_output("There was an issue starting the server due to error: " + str(exData))
                    root.after(3000, check_palworld_process)
        else:
            append_to_output("ARRCON commands failed to update. Check your Settings before attempting this again and be sure everything is configured first.")
    else:
        append_to_output("Server check failed. Check your Settings before attempting this again and be sure everything is configured first.")

def graceful_shutdown():
    global current_function, scheduled_time
    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        if current_function == "shutdown_server" or current_function == "message_server_30" or current_function == "message_server_10":
            time_left = int(max(0, scheduled_time - time.time()))
            append_to_output(f"The server is already in the process of shutting down. Shutdown will complete in: {time_left} seconds.")
        else:
            results = update_commands()
            if results == "commands updated":
                save_server()
                append_to_output("The server will shutdown in 10 seconds...")
                root.update()
                root.after(5000, shutdown_server("graceful"))
                root.after(13000, kill_palworld_process)
            else:
                append_to_output("RCON server shutdown commands did not update. Please Check your Settings before attempting this again.")
    else:
        append_to_output("Palworld server is not running. Nothing to stop.")

def force_shutdown():
    global current_function, scheduled_time
    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        if current_function == "shutdown_server" or current_function == "message_server_30" or current_function == "message_server_10":
            time_left = int(max(0, scheduled_time - time.time()))
            append_to_output(f"The server is already in the process of shutting down. Shutdown will complete in: {time_left} seconds.")
        else:
            results = update_commands()
            if results == "commands updated":
                save_server()
                append_to_output("Performing a forceful shutdown...")
                root.after(1000, shutdown_server("force"))
                root.after(2000, kill_palworld_process)
            else:
                append_to_output("RCON server shutdown commands did not update. Please Check your Settings before attempting this again.")
    else:
        append_to_output("Palworld server is not running. Nothing to stop.")

def nosave_shutdown():
    global current_function, scheduled_time
    task_name = "PalServer-Win64-Shipping-Cmd.exe"

    # Get the list of running processes
    running_processes = [proc.name() for proc in psutil.process_iter()]

    # Check if the process is in the list
    if task_name in running_processes:
        if current_function == "shutdown_server" or current_function == "message_server_30" or current_function == "message_server_10":
            time_left = int(max(0, scheduled_time - time.time()))
            append_to_output(f"The server is already in the process of shutting down. Shutdown will complete in: {time_left} seconds.")
        else:
            results = update_commands()
            if results == "commands updated":
                append_to_output("Performing a no save shutdown...")
                root.after(1000, shutdown_server("force"))
                root.after(2000, kill_palworld_process)
            else:
                append_to_output("RCON server shutdown commands did not update. Please Check your Settings before attempting this again.")
    else:
        append_to_output("Palworld server is not running. Nothing to stop.")

def update_palworld_server():
    if palworld_exe_result_label.cget("text") == "PalServer.exe detected":
        if steamcmd_exe_result_label.cget("text") == "SteamCMD.exe detected":
            task_name = "PalServer-Win64-Shipping-Cmd.exe"
            running_processes = [proc.name() for proc in psutil.process_iter()]
            if task_name not in running_processes:
                palworld_directory = server_directory_selection.cget("text")
                steamcmd_directory = steamcmd_directory_selection.cget("text")
                update_palworld_command = f'call {steamcmd_directory}/SteamCMD.exe +force_install_dir {palworld_directory} +login anonymous +app_update 2394010 +quit'
                try:
                    process = subprocess.Popen(update_palworld_command, shell=True, stdout=subprocess.PIPE, text=True, universal_newlines=True)
                    for line in process.stdout:
                        append_to_output(line.strip())
                        root.update()
                    return_code = process.wait()
                    if return_code == 0:
                        append_to_output("The server has updated successfully")
                        return "server updated"
                    else:
                        append_to_output("The server was unable to check for updates")
                        return "server not updated"
                except Exception as exData:
                    append_to_output(f"Couldn't update the server due to error: " + str(exData))
            else:
                append_to_output("Server is running. Cannot update the server unless the server is stopped.")
                messagebox.showinfo("Server Running", "Cannot run this function unless the server is stopped.")
        else:
            append_to_output("You must select a valid Steamcmd Directory to use this function. Check your Settings before attempting this again")
            messagebox.showwarning("Invalid Directory", "You must select a valid Steamcmd directory to use this function")
    else:
        append_to_output("You must select a valid Palworld Server Directory to use this function. Check your Settings before attempting this again")
        messagebox.showwarning("Invalid Directory", "You must select a valid Palworld Server directory to use this function")

def validate_palworld_server():
    if palworld_exe_result_label.cget("text") == "PalServer.exe detected":
        if steamcmd_exe_result_label.cget("text") == "SteamCMD.exe detected":
            task_name = "PalServer-Win64-Shipping-Cmd.exe"
            running_processes = [proc.name() for proc in psutil.process_iter()]
            if task_name not in running_processes:
                palworld_directory = server_directory_selection.cget("text")
                steamcmd_directory = steamcmd_directory_selection.cget("text")
                validate_palworld_command = f'call {steamcmd_directory}/SteamCMD.exe +force_install_dir {palworld_directory} +login anonymous +app_update 2394010 validate +quit'
                try:
                    process = subprocess.Popen(validate_palworld_command, shell=True, stdout=subprocess.PIPE, text=True, universal_newlines=True)
                    for line in process.stdout:
                        append_to_output(line.strip())
                        root.update()
                    return_code = process.wait()
                    if return_code == 0:
                        append_to_output("The server was validated successfully")
                except Exception as exData:
                    append_to_output(f"Couldn't validate the server due to error: " + str(exData))
            else:
                append_to_output("Server is running. Cannot update the server unless the server is stopped.")
                messagebox.showinfo("Server Running", "Cannot run this function unless the server is stopped")
        else:
            append_to_output("You must select a valid Steamcmd Directory to use this function. Check your Settings before attempting this again")
            messagebox.showwarning("Invalid Directory", "You must select a valid Steamcmd directory to use this function")
    else:
        append_to_output("You must select a valid Palworld Server Directory to use this function. Check your Settings before attempting this again")
        messagebox.showwarning("Invalid Directory", "You must select a valid Palworld Server directory to use this function")

def server_check_update_commands():
    server_check_results = server_check()
    if server_check_results == "check good":
        update_commands_results = update_commands()
        if update_commands_results == "commands updated":
            return "good"

def server_check():
    if palworld_exe_result_label.cget("text") == "PalServer.exe detected":
        if arrcon_exe_result_label.cget("text") == "ARRCON.exe detected":
            if isinstance(rcon_port.cget("text"), int):
                if rcon_state.cget("text") == "True":
                    return "check good"
                else:
                    append_to_output('RCON is disabled. Be sure the flag "RCONEnabled=True" is set in your PalWorldSettings.ini file.')
                    messagebox.showinfo("RCON Disabled", "RCON needs to be enabled")
            else:
                append_to_output("No RCON port was detected. Check your PalWorldSettings.ini file and the Palworld page to confirm that the RCON port is set correctly.")
                messagebox.showwarning("RCON Port Issue", "No RCON port was detected")
        else:
            append_to_output("ARRCON.exe was not detected in your selected directory. Check your Settings before attempting this again")
            messagebox.showwarning("Invalid Directory", "ARRCON.exe was not found in the selected directory")
    else:
        append_to_output("PalServer.exe was not detected in your selected directory. Check your Settings before attempting this again")
        messagebox.showwarning("Invalid Directory", "PalServer.exe was not found in the selected directory")

def select_palworld_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        server_directory_selection.configure(text=f"{directory_path}")
        search_file(directory_path, "PalServer.exe")
        get_server_info(directory_path)
    else:
        server_directory_selection.configure(text="No Directory Selected", text_color="red")
        palworld_exe_result_label.configure(text="PalServer.exe not found", text_color="red")
        append_to_output("The directory you selected does not contain the PalServer.exe and other file information required to run this application. Please verify the directory")
        messagebox.showwarning("Invalid Directory", "PalServer.exe was not found in the selected directory")

def select_arrcon_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        arrcon_directory_selection.configure(text=f"{directory_path}")
        search_file(directory_path, "ARRCON.exe")
    else:
        arrcon_directory_selection.configure(text="No Directory Selected", text_color="red")
        arrcon_exe_result_label.configure(text="ARRCON.exe not found", text_color="red")
        append_to_output("The directory you selected does not contain the ARRCON.exe required to run this application. Please verify the directory")
        messagebox.showwarning("Invalid Directory", "ARRCON.exe was not found in the selected directory")

def select_steamcmd_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        steamcmd_directory_selection.configure(text=f"{directory_path}")
        search_file(directory_path, "SteamCMD.exe")
    else:
        steamcmd_directory_selection.configure(text="No Directory Selected", text_color="red")
        steamcmd_exe_result_label.configure(text="SteamCMD.exe not found", text_color="red")
        append_to_output("The directory you selected does not contain the SteamCMD.exe. Please verify the directory")
        messagebox.showwarning("Invalid Directory", "SteamCMD.exe was not found in the selected directory")

def select_backup_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        backup_directory_selection.configure(text=f"{directory_path}")
        search_file(directory_path, "backup_directory")
    else:
        backup_directory_selection.configure(text="No Directory Selected", text_color="red")
        backup_result_label.configure(text="backup directory not found", text_color="red")

def search_file(directory, target_file):
    if target_file == "PalServer.exe":
        if not directory == "No Directory Selected":
            files_in_directory = os.listdir(directory)
            if target_file in files_in_directory:
                palworld_exe_result_label.configure(text=f"{target_file} detected", text_color="green")
                return
            else:
                palworld_exe_result_label.configure(text=f"{target_file} not found", text_color="red")
                messagebox.showwarning("Invalid Directory", "PalServer.exe was not found in the selected directory")
        else:
            palworld_exe_result_label.configure(text=f"{target_file} not found", text_color="red")
    elif target_file == "ARRCON.exe":
        if not directory == "No Directory Selected":
            files_in_directory = os.listdir(directory)
            if target_file in files_in_directory:
                arrcon_exe_result_label.configure(text=f"{target_file} detected", text_color="green")
                return
            else:
                arrcon_exe_result_label.configure(text=f"{target_file} not found", text_color="red")
                messagebox.showwarning("Invalid Directory", "ARRCON.exe was not found in the selected directory")
        else:
            arrcon_exe_result_label.configure(text=f"{target_file} not found", text_color="red")
    elif target_file == "SteamCMD.exe":
        if not directory == "No Directory Selected":
            files_in_directory = os.listdir(directory)
            if target_file in files_in_directory:
                steamcmd_exe_result_label.configure(text=f"{target_file} detected", text_color="green")
                return
            else:
                steamcmd_exe_result_label.configure(text=f"{target_file} not found", text_color="red")
                messagebox.showwarning("Invalid Directory", "SteamCMD.exe was not found in the selected directory")
        else:
            steamcmd_exe_result_label.configure(text=f"{target_file} not found", text_color="red")
    elif target_file == "backup_directory":
        if not directory == "No Directory Selected":
            files_in_directory = os.listdir(directory)
            if target_file in files_in_directory:
                backup_result_label.configure(text="Backup Directory detected", text_color="green")
                return
            else:
                backup_result_label.configure(text="Backup Directory not found", text_color="red")
                messagebox.showwarning("Invalid Directory", "Backup Directory was not found in the selected directory")
        else:
            backup_result_label.configure(text="Backup Directory not found", text_color="red")

def reset_server_info():
    rcon_port.configure(text="Unknown")
    rcon_state.configure(text="Unknown")
    max_players.configure(text="Unknown")
    server_name.configure(text="Unknown")
    server_description.configure(text="Unknown")
    server_password.configure(text="Unknown")
    server_port.configure(text="Unknown")

def get_server_info(directory):
    global rcon_pass
    if not directory == "No Directory Selected":
        file_path = os.path.join(directory, 'Pal', 'Saved', 'Config', 'WindowsServer', 'PalWorldSettings.ini')
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                file_content = file.read()
                max_players_match = re.search(r'ServerPlayerMaxNum=(\d+),', file_content)
                server_name_match = re.search(r'ServerName="([^"]+)",', file_content)
                server_description_match = re.search(r'ServerDescription="([^"]+)",', file_content)
                server_password_match = re.search(r'ServerPassword="([^"]*)",', file_content)
                server_port_match = re.search(r'PublicPort=(\d+),', file_content)
                rcon_port_match = re.search(r'RCONPort=(\d+),', file_content)
                rcon_enable_match = re.search(r'RCONEnabled=(\w+),', file_content)
                rcon_password_match = re.search(r'AdminPassword="([^"]*)",', file_content)
                crossplay_platforms_match = re.search(r'CrossplayPlatforms="((.*?)\)",', file_content)
                if rcon_port_match:
                    port = int(rcon_port_match.group(1))
                    rcon_port.configure(text=port)
                if rcon_enable_match:
                    state = str(rcon_enable_match.group(1))
                    rcon_state.configure(text=state)
                if rcon_password_match:
                    rcon_pass = str(rcon_password_match.group(1))
                    if rcon_pass == "":
                        rcon_password.configure(text="No Password Set")
                    else:
                        if show_recon_password_checkbox_var.get() == True:
                            rcon_password.configure(text=rcon_pass)
                        else:
                            rcon_password.configure(text="••••••••")
                if max_players_match:
                    max = int(max_players_match.group(1))
                    max_players.configure(text=max)
                if server_name_match:
                    server = str(server_name_match.group(1))
                    server_name.configure(text=server)
                if server_description_match:
                    description = str(server_description_match.group(1))
                    server_description.configure(text=description)
                if server_password_match:
                    serv_pass = str(server_password_match.group(1))
                    if serv_pass == "":
                        server_password.configure(text="No Password Set")
                    else:
                        server_password.configure(text=serv_pass)
                if server_port_match:
                    serv_port = int(server_port_match.group(1))
                    server_port.configure(text=serv_port)
                if crossplay_platforms_match:
                    crossplay = str(crossplay_platforms_match.group(1))
                    server_platform_state_label.configure(text=crossplay)
        else:
            reset_server_info()
    else:
        reset_server_info()

def change_theme_color():
    global theme_profile_file_path
    new_theme_color = theme_color_radio_var.get()
    if new_theme_color == "custom":
        theme_file_button.configure(state="normal")
        if os.path.isfile(theme_profile_file_path):
            try:
                ctk.set_default_color_theme(theme_profile_file_path)
            except:
                append_to_output("Invalid color profile. Reverting back to default value.")
                theme_color_radio_var.set("blue")
                theme_file_button.configure(state="disabled")
        else:
            theme_profile_file_path = filedialog.askopenfilename()
            try:
                ctk.set_default_color_theme(theme_profile_file_path)
            except:
                append_to_output("Invalid color profile. Reverting back to default value.")
                theme_color_radio_var.set("blue")
                theme_file_button.configure(state="disabled")
    else:
        theme_file_button.configure(state="disabled")
        ctk.set_default_color_theme(new_theme_color)

def change_appearance_mode():
    new_appearance_mode = theme_radio_var.get()
    ctk.set_appearance_mode(new_appearance_mode)

def change_widget_scaling():
    new_widget_scaling = widgetscalingComboBox_var.get()
    if not new_widget_scaling == "Default":
        if not "%" in new_widget_scaling:
            new_widget_scaling += "%"
            widgetscalingComboBox_var.set(new_widget_scaling)
        try:
            new_widget_scaling_float = int(new_widget_scaling.replace("%", "")) / 100
            ctk.set_widget_scaling(new_widget_scaling_float)
        except:
            append_to_output("Invalid Number. Reverting back to default value.")
            widgetscalingComboBox_var.set("Default")
    
def change_window_scaling():
    new_window_scaling = windowscalingComboBox_var.get()
    if not new_window_scaling == "Default":
        if not "%" in new_window_scaling:
            new_window_scaling += "%"
            windowscalingComboBox_var.set(new_window_scaling)
        try:
            new_window_scaling_float = int(new_window_scaling.replace("%", "")) / 100
            ctk.set_window_scaling(new_window_scaling_float)
        except:
            append_to_output("Invalid Number. Reverting back to default value.")
            windowscalingComboBox_var.set("Default")

def change_automatic_dpi_awareness():
    new_automatic_dpi_awareness = dpiawarenessoptionmenu_var.get()
    if new_automatic_dpi_awareness == "Disabled":
        ctk.deactivate_automatic_dpi_awareness()
    
def open_file(directory, strfilename):
    if not directory == "No Directory Selected":
        ini_file_path = os.path.join(directory, 'Pal', 'Saved', 'Config', 'WindowsServer', 'PalWorldSettings.ini')
        if os.path.isfile(ini_file_path):
            try:
                subprocess.Popen(['start', '', ini_file_path], shell=True)
            except Exception as exData:
                append_to_output("Error opening file: " + str(exData))
        else:
            append_to_output("You need to select a valid directory first.")
            messagebox.showwarning("Invalid Directory", "You need to select a valid directory first")
    else:
        append_to_output("You need to select a valid directory first.")
        messagebox.showwarning("Invalid Directory", "You need to select a valid directory first")

def check_for_updates(strRequestType):
    if strRequestType == "Check":
        threading.Thread(target=update_application, args=(Github_Username, Github_Repository, Application_Executable_Name, "Check")).start()
    elif strRequestType == "Download":
        threading.Thread(target=update_application, args=(Github_Username, Github_Repository, Application_Executable_Name, "Download")).start()
    elif strRequestType == "Extract":
        threading.Thread(target=update_application, args=(Github_Username, Github_Repository, Application_Executable_Name, "Extract")).start()
    elif strRequestType == "Launch":
        threading.Thread(target=update_application, args=(Github_Username, Github_Repository, Application_Executable_Name, "Launch")).start()

def update_application(repo_owner: str, repo_name: str, file_name: str, request_type: str) -> None:
    """Checks for updates, downloads them, and launches the new version."""
    if request_type == "Check":
        app_update_status_label.configure(text="Checking for updates...")
        remote_version = get_latest_version(repo_owner, repo_name, update_progress_var)
        if remote_version == "Not Published Yet":
            app_update_status_label.configure(text="No Public Release Found.")
            update_progress_var.set(0)
            updateWindow.update_idletasks()
            return
        elif remote_version is None:
            app_update_status_label.configure(text="Failed to fetch the latest version.")
            update_progress_var.set(0)
            updateWindow.update_idletasks()
            return
        elif remote_version > Application_Local_Version:
            app_update_status_label.configure(text=f"New version found: {remote_version}")
            action_button.configure(text="Download Update", command=lambda: check_for_updates("Download"))
            update_progress_var.set(0)
            updateWindow.update_idletasks()
        elif remote_version == Application_Local_Version:
            app_update_status_label.configure(text=f"Already on the latest version: {Application_Local_Version}")
            update_progress_var.set(0)
            updateWindow.update_idletasks()
    elif request_type == "Download":
        app_update_status_label.configure(text="Downloading update...")
        zip_file = download_from_github(repo_owner, repo_name, remote_version, Application_Update_Directory, update_progress_var, updateWindow)
        if zip_file is None:
            app_update_status_label.configure(text="Failed to download update...")
            update_progress_var.set(0)
            updateWindow.update_idletasks()
            return
        else:
            app_update_status_label.configure(text="Download complete.")
            update_progress_var.set(0)
            updateWindow.update_idletasks()
            action_button.configure(text="Extract Update", command=lambda: check_for_updates("Extract"))
            append_to_output(f"Downloaded file: {zip_file}")
    elif request_type == "Extract":
            app_update_status_label.configure(text="Extracting update...")
            extract_zip_file(zip_file, Application_Update_Directory, update_progress_var, updateWindow)
            os.remove(zip_file)
            append_to_output(f"Removed downloaded file: {zip_file}")
            action_button.configure(text="Update Application", command=lambda: check_for_updates("Launch"))
    elif request_type == "Launch":
        file_path = f"{file_name}-v{remote_version}.exe"
        if os.path.exists(file_path):
            app_update_status_label.configure(text="Opening Updated version of the application...")
            try:
                subprocess.Popen(file_path)
            except Exception as exData:
                app_update_status_label.configure(text="Failed to open the updated application...")
                append_to_output(f"Failed to open the updated application: {exData}")

def update_window():
    global app_update_status_label, action_button, update_progress_var, updateWindow
    about_functions_optionmenu.configure(state='disabled')
    app_run_button.configure(state='disabled')
    updateWindow = ctk.CTkToplevel(root)
    updateWindow.title("Check for Updates")
    try:
        if os.path.isfile(LOGO_ICO_FILE) and operating_mode() == False:
            updateWindow.after(250, lambda: updateWindow.wm_iconbitmap(LOGO_ICO_FILE))
        else:
            updateWindow.wm_iconbitmap(sys.executable)
    except Exception as exData:
        append_to_output("Icon wasn't able to load due to error: " + str(exData))
    updateWindow.resizable(False, False)
    updateWindow.attributes('-topmost', True)
    updateWindow.focus_force()
    app_update_info_frame = ctk.CTkFrame(updateWindow)
    app_update_info_frame.pack(expand=True, fill="both")
    app_logo_image = ctk.CTkImage(light_image=Image.open(LOGO_PNG_FILE), dark_image=Image.open(LOGO_PNG_FILE), size=(56, 56))
    app_image_label = ctk.CTkLabel(app_update_info_frame, image=app_logo_image, text="")
    app_image_label.grid(column=0, row=0, padx=(10,5), pady=(10,5), rowspan=2, sticky="w")
    app_name_label = ctk.CTkLabel(app_update_info_frame, text=Application_Name)
    app_name_label.grid(column=1, row=0, padx=(5,0), pady=(10,0), sticky="w")
    app_update_status_label = ctk.CTkLabel(app_update_info_frame, text=f"Please check for updates first.")
    app_update_status_label.grid(column=1, row=1, padx=(5,0), pady=(0,0), sticky="w")
    app_update_frame = ctk.CTkFrame(updateWindow)
    app_update_frame.pack(expand=True, fill="both")
    update_progress_var = ctk.DoubleVar(value=0)
    update_progress = ctk.CTkProgressBar(app_update_frame, height=15, width=300, mode="determinate", variable=update_progress_var)
    update_progress.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
    action_button = ctk.CTkButton(app_update_frame, text="Check for Updates", command=lambda: check_for_updates("Check"))
    action_button.grid(column=0, row=1, padx=10, pady=10)
    close_button = ctk.CTkButton(app_update_frame, text="Close", command=lambda: close_update_screen(updateWindow) if updateWindow else None)
    close_button.grid(column=1, row=1, padx=10, pady=10)
    root.after(150, lambda: center_window_to_parent(updateWindow))
    updateWindow.protocol('WM_DELETE_WINDOW', lambda: close_update_screen(updateWindow) if updateWindow else None)

def close_update_screen(window : ctk):
    about_functions_optionmenu.configure(state='normal')
    app_run_button.configure(state='normal')
    window.destroy()

def download_from_github(
    repo_owner: str, repo_name: str, version: str, download_path: str, progress_bar: ctk.DoubleVar
) -> str | None:
    """
    Downloads the given release asset from GitHub to the specified directory.
    Returns the path to the downloaded file, or None if the download fails.
    """
    try:
        asset_url = get_release_asset_url(repo_owner, repo_name, version)
        if not asset_url:
            return None

        response = requests.get(asset_url, stream=True, timeout=30)
        response.raise_for_status()  # Raise an error for bad responses

        total_size = int(response.headers.get("content-length", 0))
        filename = asset_url.split("/")[-1]
        filepath = os.path.join(download_path, filename)

        with open(filepath, "wb") as file:
            tqdm_bar = tqdm.tqdm(
                desc=filename, total=total_size, unit="iB", unit_scale=True, unit_divisor=1024
            )
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    tqdm_bar.update(len(chunk))
                    progress_bar.set(tqdm_bar.n / total_size)
                    progress_bar.update_idletasks()

        return filepath

    except requests.exceptions.RequestException as exData:
        append_to_output(f"Error downloading file: {exData}")
    except KeyboardInterrupt:
        append_to_output("Download interrupted by user.")
    except Exception as e:
        append_to_output(f"Error downloading file: {exData}")
    finally:
        if tqdm_bar:
            tqdm_bar.close()
        if response:
            response.close()
        if filepath and not os.path.getsize(filepath):
            os.remove(filepath)

    return None

def get_release_asset_url(repo_owner, repo_name, version):
    """
    Fetches the URL of the latest release asset for the given repo and version.
    Returns None if no matching asset is found.
    """
    try:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{version}"
        response = requests.get(api_url)

        if response.status_code == 200:
            release_data = response.json()
            assets = release_data.get('assets', [])

            for asset in assets:
                if (asset.get('name', '').endswith('.zip') and
                        'windows-standalone' in asset.get('name', '')):
                    return asset.get('browser_download_url', None)

            return None
        else:
            return None
    except requests.exceptions.RequestException as exData:
        return None

def extract_zip_file(zip_file_path: str, extract_dir: str, progress_bar: ctk.DoubleVar, window: ctk) -> None:
    """
    Extracts the given zip file to the specified directory.
    """
    if not zip_file_path or not extract_dir:
        raise ValueError("Zip file path and extract directory must be provided.")

    if not os.path.isfile(zip_file_path):
        raise FileNotFoundError(f"Zip file '{zip_file_path}' does not exist.")

    if not os.path.isdir(extract_dir):
        raise FileNotFoundError(f"Extract directory '{extract_dir}' does not exist.")

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            num_files = len(zip_file.infolist())
            for file_info in tqdm.tqdm(zip_file.infolist(), desc="Extracting...", total=num_files, unit="file"):
                if file_info is None:
                    raise RuntimeError("Error extracting zip file: File info is null.")
                zip_file.extract(member=file_info, path=extract_dir)
                progress_bar.set(progress_bar.get() + 1 / num_files)
                window.update_idletasks()
    except zipfile.BadZipFile as exData:
        raise RuntimeError(f"Error extracting zip file: {exData}") from exData
    except TypeError as exData:
        raise RuntimeError(f"Error extracting zip file: TypeError: {exData}") from exData
    except Exception as exData:
        raise RuntimeError(f"Unexpected error during extraction: {exData}") from exData

def get_latest_version(owner: str, repo: str, progress_bar: ctk.CTkProgressBar) -> str | None:
    """
    Fetches the latest version of a GitHub repository.
    """
    if not owner or not repo:
        raise ValueError("Repository owner and name must be provided.")

    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()
        if not release_data:
            raise ValueError("Error fetching release info: Response is null.")

        latest_version = release_data.get("tag_name", "")
        if not latest_version:
            raise ValueError("Error fetching release info: Tag name is null.")

        progress_bar.set(1)
        return latest_version.replace("v", "")

    except requests.exceptions.HTTPError as exHTTPData:
        if exHTTPData.response.status_code == 404:
            try:
                response = requests.get(f"https://github.com/{owner}/{repo}/releases/latest")
                response.raise_for_status()
                actual_version = response.url.split('/').pop()
                if actual_version.startswith("v"):
                    progress_bar.set(1)
                    latest_version = actual_version.replace("v", "")
                    return latest_version
                elif actual_version.startswith("releases"):
                    progress_bar.set(1)
                    latest_version = "Not Published Yet"
                    return latest_version
                else:
                    progress_bar.set(1)
                    latest_version = None
                    return latest_version
            except requests.exceptions.RequestException as exData:
                raise ValueError(f"Error fetching release info: {exData}") from exData

        else:
            raise ValueError(f"Error fetching release info: {exHTTPData}") from exHTTPData

    except requests.exceptions.RequestException as exData:
        raise ValueError(f"Error fetching release info: {exData}") from exData

def about_window():
    about_window = ctk.CTkToplevel(root)
    about_window.title(f"{Application_Name} - About")
    about_window.geometry("300x200")
    about_window.resizable(False, False)
    about_window.protocol('WM_DELETE_WINDOW', lambda: about_window.destroy())
    about_window.grab_set()
    about_window.after(150, lambda: center_window_to_parent(about_window))

def show_recon_password():
    directory = server_directory_selection.cget("text")
    if not directory == "No Directory Selected":
        if globals()["rcon_pass"] == "":
            rcon_password.configure(text="No Password Set")
        else:
            if show_recon_password_checkbox_var.get() == True:
                rcon_password.configure(text=globals()["rcon_pass"] )
            else:
                rcon_password.configure(text="••••••••")
    else:
        rcon_password.configure(text="Unknown")

def donate(intDonateChoice : int):
    if intDonateChoice == 1:
        webbrowser.open("https://www.buymeacoffee.com/thewisestguy")
    elif intDonateChoice == 2:
        webbrowser.open("https://www.buymeacoffee.com/xkillermaverick")

def report_bug():
    webbrowser.open(f"https://github.com/{Github_Username}/{Github_Repository}/issues")

def functions_request_button_click():
    selected_function = functions_optionmenu.get()
    if selected_function == "Select a Option":
        messagebox.showinfo(Application_Name, "Please select an option before clicking the request button.")
    elif selected_function == "Start Server":
        start_server()
    elif selected_function == "Graceful Shutdown":
        graceful_shutdown()
    elif selected_function == "Force Shutdown":
        force_shutdown()
    elif selected_function == "Update Server":
        update_palworld_server()
    elif selected_function == "Validate Server Files":
        validate_palworld_server()
    elif selected_function == "Backup Server":
        backup_server()

def functions_run_button_click():
    selected_function = about_functions_optionmenu.get()
    if selected_function == "Select a Option":
        messagebox.showinfo(Application_Name, "Please select an option before clicking the run button.")
    elif selected_function == "Check for Updates":
        update_window()
    elif selected_function == "Report Bug":
        report_bug()
    elif selected_function == "Donate to Andrew1175":
        donate(1)
    elif selected_function == "Donate to xKillerMaverick":
        donate(2)
    elif selected_function == "Exit Application":
        exit()

def functions_open_button_click():
    selected_function = opensettings_optionmenu.get()
    if selected_function == "Select a Option":
        messagebox.showinfo(Application_Name, "Please select an option before clicking the open button.")
    elif selected_function == "Palworld World Settings":
        open_file(server_directory_selection.cget("text"), "PalWorldSettings.ini")
    elif selected_function == "Palworld Engine Settings":
        open_file(server_directory_selection.cget("text"), "Engine.ini")
    elif selected_function == "Palworld Game Settings":
        open_file(server_directory_selection.cget("text"), "GameUserSettings.ini")
    elif selected_function == "Palworld Save Folder":
        open_file(server_directory_selection.cget("text"), "Level.sav")
    elif selected_function == "PalDefender Settings":
        open_file(server_directory_selection.cget("text"), "PalGuard.json")
    elif selected_function == "RE-UE4SS Settings":
        open_file(server_directory_selection.cget("text"), "UE4SS-settings.ini")

def tray_button_click(icon, item):
    if str(item) == "Hide":
        root.withdraw()
        tray_menu_change(icon, item)
    elif str(item) == "Show":
        root.deiconify()
        tray_menu_change(icon, item)
    elif str(item) == "Check for Updates":
        update_window()
    elif str(item) == "About":
        about_window()
    elif str(item) == "Exit":
        exit()

def tray_menu_change(icon, item):
    if str(item) == "Hide":
        icon.menu = pystray.Menu(
        pystray.MenuItem("Show", tray_button_click),
        pystray.MenuItem("Check for Updates", tray_button_click),
        pystray.MenuItem("About", tray_button_click),
        pystray.MenuItem("Exit", tray_button_click),
        )
        icon.update_menu()
    elif str(item) == "Show":
        icon.menu = pystray.Menu(
        pystray.MenuItem("Hide", tray_button_click),
        pystray.MenuItem("Check for Updates", tray_button_click),
        pystray.MenuItem("About", tray_button_click),
        pystray.MenuItem("Exit", tray_button_click),
        )
        icon.update_menu()
def validate_time_input(time):
    # Validate the input format (HH:MM)
    if len(time) == 0:
        return True  # Allow empty input
    if not re.match(r'^(1[0-2]|0?[1-9]):[0-5][0-9]$', time.strip()):
        append_to_output("Invalid time format")
        return False  # Reject invalid format

    # Validate the hour and minute values
    hour, minute = map(int, time.split(':')[0:2])
    if not (0 <= hour <= 12 and 0 <= minute <= 59):
        append_to_output("Invalid time format")
        return False  # Reject invalid time
    return "time good"  # Accept valid input

def get_server_folder_name(server_file):
    if not os.path.exists(server_file):
        append_to_output("DedicatedServerName not found in the server file.")
        return None
    with open(server_file, 'r') as file:
        for line in file:
            if line.startswith("DedicatedServerName="):
                server_folder_name = line.strip().split("=", 1)[1]
                return server_folder_name
    append_to_output("DedicatedServerName not found in the server file.")
    return None

def discord_show():
    discordUrlEntry.configure(show="")
    show_discord_data_checkbox.configure(command=discord_hide)

def discord_hide():
    discordUrlEntry.configure(show="•")
    show_discord_data_checkbox.configure(command=discord_show)

def email_show():
    email_password_entry.configure(show="")
    show_email_password_checkbox.configure(command=email_hide)

def email_hide():
    email_password_entry.configure(show="•")
    show_email_password_checkbox.configure(command=email_show)

def autorun_check():
    if not os.path.isfile(strAutorunPath):
        run_at_startup_remove(globals()["strAutorunName"])
        append_to_output("Application removed from startup because it was not found. This may be due to a move or rename of the application.")

def autorun_application():
    if autorun_application_switch_var.get() == "True":
        globals()["strAutorunName"] = Application_Executable_Name
        globals()["strAutorunPath"] = Application_Executable_Path
        run_at_startup_set(Application_Executable_Name, Application_Executable_Path)
        append_to_output("Application added to startup.")
    else:
        run_at_startup_remove(globals()["strAutorunName"])
        globals()["strAutorunName"] = None
        globals()["strAutorunPath"] = None
        append_to_output("Application removed from startup.")

def load_and_display_file(textbox, filepath):
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            textbox.delete("0.0", "end")
            textbox.insert("0.0", content)
    except FileNotFoundError:
         textbox.delete("0.0", "end")
         textbox.insert("0.0", "File not found.")
    except Exception as exData:
        textbox.delete("0.0", "end")
        textbox.insert("0.0", f"An error occurred: {exData}")

def check_save_size():
    palworld_directory = server_directory_selection.cget("text")
    windows_server_folder = os.path.join(palworld_directory, "Pal", "Saved", "Config", "WindowsServer")
    server_file = os.path.join(windows_server_folder, "GameUserSettings.ini")
    save_last_minute = globals().get("save_last_minute")    
    server_folder_name = get_server_folder_name(server_file)
    saved_folder = os.path.join(palworld_directory, "Pal", "Saved")
    level_save_path = os.path.join(saved_folder, "SaveGames", "0", server_folder_name, "Level.sav")    
    current_minute = datetime.now().minute
    if save_last_minute != current_minute:
        if os.path.exists(level_save_path):
            current_size = os.path.getsize(level_save_path)
            last_modified = datetime.fromtimestamp(os.path.getmtime(level_save_path)).strftime("%Y-%m-%d %H:%M:%S")
            last_size = globals().get("last_level_save_size")
            unchanged_attempts = globals().get("unchanged_attempts", 0)
            if last_size is not None and current_size == last_size:
                unchanged_attempts += 1
                append_to_output(f"Caution: Server save failed.")
            else:
                unchanged_attempts = 0
            append_to_output(f"[Save][Current: {current_size}][Old: {last_size}][Checks: {unchanged_attempts}][Last Modified: {last_modified}]")
            globals()["last_level_save_size"] = current_size
            globals()["unchanged_attempts"] = unchanged_attempts
            if unchanged_attempts >= 3:
                append_to_output("Server is restarting due to a save failure.")
                globals()["last_level_save_size"] = None
                globals()["unchanged_attempts"] = 0
                nosave_shutdown()
        else:
            append_to_output(f"Level.sav file not found at: {level_save_path}")
        globals()["save_last_minute"] = current_minute

def initialize():
    resource_directory()
    objmenutray = pystray.Menu(
        pystray.MenuItem("Hide", tray_button_click),
        pystray.MenuItem("Check for Updates", tray_button_click),
        pystray.MenuItem("About", tray_button_click),
        pystray.MenuItem("Exit", tray_button_click),
    )
    try: 
        root.wm_iconbitmap(LOGO_ICO_FILE)
        tray_icon = pystray.Icon(Github_Repository, Image.open(LOGO_PNG_FILE), Application_Name, objmenutray)
    except Exception as ex_data:
        append_to_output(f"Icon wasn't able to load due to error: {ex_data}")
    load_theme_settings()
    threading.Thread(target=tray_icon.run, daemon=True).start()

############################## Root Code ######################################################
root = ctk.CTk()
root.title(Application_Name)
initialize()

tabControl = ctk.CTkTabview(root)
tabControl.pack(expand=True, fill="both")

homeTab = tabControl.add("Home")
settingTab = tabControl.add("Settings")
palworldTab = tabControl.add("Palworld")
notificationsTab = tabControl.add("Notifications")
personalizationTab =  tabControl.add("Personalization")
aboutTab = tabControl.add("About")

homeTab.columnconfigure(0, weight=1)
homeTab.columnconfigure(1, weight=1)
settingTab.columnconfigure(0, weight=1)
notificationsTab.columnconfigure(0, weight=1)
notificationsTab.columnconfigure(1, weight=1)
personalizationTab.columnconfigure(0, weight=1)
aboutTab.columnconfigure(0, weight=1)

###################### Main Tab ################################################################
###################### Interval Configurations ###################################################
interval_frame = ctk.CTkFrame(homeTab)
interval_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

interval_frame_button = ctk.CTkSegmentedButton(interval_frame, values=["Interval Configuration"], state="disabled")
interval_frame_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

restart_interval_switch_var = ctk.StringVar(value="False")
restart_interval_switch = ctk.CTkSwitch(interval_frame, text="Server Restart Interval (Hours):", variable=restart_interval_switch_var, command=enable_server_restart, onvalue="True", offvalue="False")
restart_interval_switch.grid(column=0, row=1, sticky="w")
restartEntry = ctk.CTkEntry(interval_frame, width=24)
restartEntry.grid(column=2, row=1, pady=(0, 4), sticky="w")

restartScheduleSwitch_var = ctk.StringVar(value="False")
restartScheduleSwitch = ctk.CTkSwitch(interval_frame, text="Daily Server Restart Time (12-hour):", variable=restartScheduleSwitch_var, command=enable_scheduled_restart, onvalue="True", offvalue="False")
restartScheduleSwitch.grid(column=0, row=2, padx=(0, 10), sticky="w")
restartTimeEntry_var = ctk.StringVar()
restartScheduleEntry = ctk.CTkEntry(interval_frame, textvariable=restartTimeEntry_var, width=48)
restartScheduleEntry.grid(column=2, row=2, padx=(0, 4), pady=(0, 4), sticky="w")
ampm_optionmenu_var = ctk.StringVar(value="AM")
ampm_optionmenu = ctk.CTkOptionMenu(interval_frame, variable=ampm_optionmenu_var, values=["AM", "PM"], width=60)
ampm_optionmenu.grid(column=3, row=2, pady=(0, 4), sticky="w")

monitor_interval_switch_var = ctk.StringVar(value="False")
monitor_interval_switch = ctk.CTkSwitch(interval_frame, text="Monitor Server Interval (Minutes):", variable=monitor_interval_switch_var, command=enable_monitor_server, onvalue="True", offvalue="False")
monitor_interval_switch.grid(column=0, row=3, sticky="w")
monitorEntry = ctk.CTkEntry(interval_frame, width=24)
monitorEntry.grid(column=2, row=3, pady=(0, 4), sticky="w")

backupIntervalSwitch_var = ctk.StringVar(value="False")
backupIntervalSwitch = ctk.CTkSwitch(interval_frame, text="Backup Server Interval (Hours):", variable=backupIntervalSwitch_var, command=enable_backup_interval, onvalue="True", offvalue="False")
backupIntervalSwitch.grid(column=0, row=4, sticky="w")
backupIntervalEntry = ctk.CTkEntry(interval_frame, width=24)
backupIntervalEntry.grid(column=2, row=4, pady=(0, 4), sticky="w")

saveIntervalSwitch_var = ctk.StringVar(value="False")
saveIntervalSwitch = ctk.CTkSwitch(interval_frame, text="Server Save Interval (Minutes):", variable=saveIntervalSwitch_var, command=enable_save_interval, onvalue="True", offvalue="False")
saveIntervalSwitch.grid(column=0, row=5, sticky="w")
saveIntervalEntry = ctk.CTkEntry(interval_frame, width=24)
saveIntervalEntry.grid(column=2, row=5, sticky="w")

deleteOldBackupsSwitch_var = ctk.StringVar(value="False")
deleteOldBackupsSwitch = ctk.CTkSwitch(interval_frame, text="Delete Backups Older Than (Days):", variable=deleteOldBackupsSwitch_var, command=enable_delete_backups, onvalue="True", offvalue="False")
deleteOldBackupsSwitch.grid(column=0, row=6, pady=(0, 4), sticky="w")
deleteOldBackupsEntry = ctk.CTkEntry(interval_frame, width=24)
deleteOldBackupsEntry.grid(column=2, row=6, sticky="w")

###################### Optional Configurations ###################################################

optional_config_frame = ctk.CTkFrame(homeTab)
optional_config_frame.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

optional_config_button = ctk.CTkSegmentedButton(optional_config_frame, values=["Optional Configurations"], state="disabled")
optional_config_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

send_email_switch_var = ctk.StringVar(value="False")
send_email_switch = ctk.CTkSwitch(optional_config_frame, text="Send Notification Email on crash", variable=send_email_switch_var, command=enable_send_email, onvalue="True", offvalue="False")
send_email_switch.grid(column=0, row=1, pady=(0, 4), sticky="w")

discordWebhookSwitch_var = ctk.StringVar(value="False")
discordWebhookSwitch = ctk.CTkSwitch(optional_config_frame, text="Send Discord channel message on crash", variable=discordWebhookSwitch_var, command=enable_send_discord_message, onvalue="True", offvalue="False")
discordWebhookSwitch.grid(column=0, row=2, pady=(0, 4), sticky="w")

update_server_startup_switch_var = ctk.StringVar(value="False")
update_server_startup_switch = ctk.CTkSwitch(optional_config_frame, text="Check for updates on server startup", variable=update_server_startup_switch_var, command=enable_server_updates_on_startup, onvalue="True", offvalue="False")
update_server_startup_switch.grid(column=0, row=3, pady=(0, 4), sticky="w")

backup_server_switch_var = ctk.StringVar(value="False")
backup_server_switch = ctk.CTkSwitch(optional_config_frame, text="Backup server during restarts", variable=backup_server_switch_var, command=enable_server_backups, onvalue="True", offvalue="False")
backup_server_switch.grid(column=0, row=4, pady=(0, 4), sticky="w")

autorun_application_switch_var = ctk.StringVar(value="False")
autorun_application_switch = ctk.CTkSwitch(optional_config_frame, text="Start Application on system startup", variable=autorun_application_switch_var, command=autorun_application, onvalue="True", offvalue="False")
autorun_application_switch.grid(column=0, row=5, pady=(0, 4), sticky="w")

###################### Server Functions ###################################################

server_functions_frame = ctk.CTkFrame(homeTab)
server_functions_frame.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")

server_functions_button = ctk.CTkSegmentedButton(server_functions_frame, values=["Server Functions"], state="disabled")
server_functions_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

functions_optionmenu = ctk.CTkOptionMenu(server_functions_frame, values=["Start Server", "Graceful Shutdown", "Force Shutdown", "Update Server", "Validate Server Files", "Backup Server"])
functions_optionmenu.grid(column=0, row=1, padx=(0,5), pady=10)
functions_optionmenu.set("Select a Option")

functions_go_button = ctk.CTkButton(server_functions_frame, text="Request", command=functions_request_button_click)
functions_go_button.grid(column=1, row=1)

###################### Network Information ###################################################

network_info_frame = ctk.CTkFrame(homeTab)
network_info_frame.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")

server_info_button = ctk.CTkSegmentedButton(network_info_frame, values=["Network Information"], state="disabled")
server_info_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

server_interal_ip_label = ctk.CTkLabel(network_info_frame, text="Server Internal IP:")
server_interal_ip_label.grid(column=0, row=1, padx=(0,3), sticky="w")

server_interal_ip_state_label = ctk.CTkLabel(network_info_frame, text="Unknown")
server_interal_ip_state_label.grid(column=1, row=1, sticky="w")

server_external_ip_label = ctk.CTkLabel(network_info_frame, text="Server External IP:")
server_external_ip_label.grid(column=0, row=2, padx=(0,3), sticky="w")

server_external_ip_state_label = ctk.CTkLabel(network_info_frame, text="Unknown")
server_external_ip_state_label.grid(column=1, row=2, sticky="w")

updateNetInfoButton = ctk.CTkButton(network_info_frame, text="Update Now", command=network_status_info)
updateNetInfoButton.grid(column=0, row=3, columnspan=2, padx=5, pady=5)


###################### Server Information ###################################################

server_info_frame = ctk.CTkFrame(homeTab)
server_info_frame.grid(column=1, row=1, padx=10, pady=10, sticky="nsew")

server_info_button = ctk.CTkSegmentedButton(server_info_frame, values=["Server Information"], state="disabled")
server_info_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

server_status_label = ctk.CTkLabel(server_info_frame, text="Server Status:")
server_status_label.grid(column=0, row=1, padx=(0,3), sticky="w")

server_status_state_label = ctk.CTkLabel(server_info_frame, text="Unknown")
server_status_state_label.grid(column=1, row=1, sticky="w")

server_version_label = ctk.CTkLabel(server_info_frame, text="Server Version:")
server_version_label.grid(column=0, row=2, padx=(0,3), sticky="w")

server_version_state_label = ctk.CTkLabel(server_info_frame, text="Unknown")
server_version_state_label.grid(column=1, row=2, sticky="w")

updateSvrInfoButton = ctk.CTkButton(server_info_frame, text="Update Now", command=server_status_info)
updateSvrInfoButton.grid(column=0, row=3, columnspan=2, padx=5, pady=5)


###################### Server Tab ###################################################
###################### Palworld Settings Frame ###################################################

server_settings_frame = ctk.CTkFrame(palworldTab)
server_settings_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

server_info_button = ctk.CTkSegmentedButton(server_settings_frame, values=["Server Information"], state="disabled")
server_info_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

show_recon_password_checkbox_var = ctk.StringVar(value="False")
show_recon_password_checkbox = ctk.CTkCheckBox(server_settings_frame, text="Show RCON Password", variable=show_recon_password_checkbox_var, command=show_recon_password, onvalue="True", offvalue="False")
show_recon_password_checkbox.grid(column=1, row=0, columnspan=2, pady=(0,5), sticky="w")

server_name_label = ctk.CTkLabel(server_settings_frame, text="Server Name:")
server_name_label.grid(column=0, row=1, sticky="w", padx=10)

server_name = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_name.grid(column=0, row=2, sticky="w", padx=10)

server_description_label = ctk.CTkLabel(server_settings_frame, text="Server Description:")
server_description_label.grid(column=0, row=3, sticky="w", padx=10)

server_description = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_description.grid(column=0, row=4, sticky="w", padx=10)

server_password_label = ctk.CTkLabel(server_settings_frame, text="Server Password:")
server_password_label.grid(column=0, row=5, sticky="w", padx=10)

server_password = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_password.grid(column=0, row=6, sticky="w", padx=10)

max_players_label = ctk.CTkLabel(server_settings_frame, text="Max Players:")
max_players_label.grid(column=1, row=1, sticky="w", padx=10)

max_players = ctk.CTkLabel(server_settings_frame, text="Unknown")
max_players.grid(column=1, row=2, sticky="w", padx=10)

server_port_label = ctk.CTkLabel(server_settings_frame, text="Server Port:")
server_port_label.grid(column=1, row=3, sticky="w", padx=10)

server_port = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_port.grid(column=1, row=4, sticky="w", padx=10)

server_id_label = ctk.CTkLabel(server_settings_frame, text="Server ID:")
server_id_label.grid(column=1, row=5, sticky="w", padx=10)

server_id = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_id.grid(column=1, row=6, sticky="w", padx=10)

rcon_port_label = ctk.CTkLabel(server_settings_frame, text="RCON Port:")
rcon_port_label.grid(column=2, row=1, sticky="w", padx=10)

rcon_port = ctk.CTkLabel(server_settings_frame, text="Unknown")
rcon_port.grid(column=2, row=2, sticky="w", padx=10)

rcon_state_label = ctk.CTkLabel(server_settings_frame, text="RCON Enabled:")
rcon_state_label.grid(column=2, row=3, sticky="w", padx=10)

rcon_state = ctk.CTkLabel(server_settings_frame, text="Unknown")
rcon_state.grid(column=2, row=4, sticky="w", padx=10)

rcon_password_label = ctk.CTkLabel(server_settings_frame, text="RCON Password:")
rcon_password_label.grid(column=2, row=5, sticky="w", padx=10)

rcon_password = ctk.CTkLabel(server_settings_frame, text="Unknown")
rcon_password.grid(column=2, row=6, sticky="w", padx=10)

server_platform_label = ctk.CTkLabel(server_settings_frame, text="Crossplay Platforms:")
server_platform_label.grid(column=3, row=1, sticky="w", padx=10)

server_platform_state_label = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_platform_state_label.grid(column=3, row=2, sticky="w", padx=10)

server_ue4ss_label = ctk.CTkLabel(server_settings_frame, text="RE-UE4SS:")
server_ue4ss_label.grid(column=3, row=3, sticky="w", padx=10)

server_ue4ss_state_label = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_ue4ss_state_label.grid(column=3, row=4, sticky="w", padx=10)

server_paldefender_label = ctk.CTkLabel(server_settings_frame, text="PalDefender:")
server_paldefender_label.grid(column=3, row=5, sticky="w", padx=10)

server_paldefender_state_label = ctk.CTkLabel(server_settings_frame, text="Unknown")
server_paldefender_state_label.grid(column=3, row=6, sticky="w", padx=10)

###################### Settings Launcher Frame ####################################

server_settings_launcher_frame = ctk.CTkFrame(palworldTab)
server_settings_launcher_frame.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

config_opener_button = ctk.CTkSegmentedButton(server_settings_launcher_frame, values=["Configuration Launcher"], state="disabled")
config_opener_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

opensettings_optionmenu = ctk.CTkOptionMenu(server_settings_launcher_frame, values=["Palworld World Settings", "Palworld Engine Settings", "Palworld Game Settings", "Palworld Save Folder", "PalDefender Settings", "RE-UE4SS Settings"])
opensettings_optionmenu.grid(column=0, row=1, sticky="w", padx=(0,5), pady=(10,0))
opensettings_optionmenu.set("Select a Option")

edit_server_config_button = ctk.CTkButton(server_settings_launcher_frame, text="Open", command=functions_open_button_click)
edit_server_config_button.grid(column=1, row=1, pady=(10,0), sticky="w")

###################### Server Configuration Frame ###################################################

server_config_frame = ctk.CTkFrame(settingTab)
server_config_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

server_config_button = ctk.CTkSegmentedButton(server_config_frame, values=["Server Configuration"], state="disabled")
server_config_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

server_directory_button = ctk.CTkButton(server_config_frame, text="Select Palworld Directory:", command=select_palworld_directory)
server_directory_button.grid(column=0, row=1, padx=10, pady=10)

server_directory_selection = ctk.CTkLabel(server_config_frame, text="No Directory Selected")
server_directory_selection.grid(column=1, row=1, sticky="w")

palworld_exe_result_label = ctk.CTkLabel(server_config_frame, text="Unknown")
palworld_exe_result_label.grid(column=2, row=1)

arrcon_directory_button = ctk.CTkButton(server_config_frame, text="Select ARRCON Directory:", command=select_arrcon_directory)
arrcon_directory_button.grid(column=0, row=2, padx=10, pady=10)

arrcon_directory_selection = ctk.CTkLabel(server_config_frame, text="No Directory Selected")
arrcon_directory_selection.grid(column=1, row=2, sticky="w")

arrcon_exe_result_label = ctk.CTkLabel(server_config_frame, text="Unknown")
arrcon_exe_result_label.grid(column=2, row=2)

steamcmd_directory_button = ctk.CTkButton(server_config_frame, text="Select SteamCMD Directory:", command=select_steamcmd_directory)
steamcmd_directory_button.grid(column=0, row=3, padx=10, pady=10)

steamcmd_directory_selection = ctk.CTkLabel(server_config_frame, text="No Directory Selected")
steamcmd_directory_selection.grid(column=1, row=3, sticky="w")

steamcmd_exe_result_label = ctk.CTkLabel(server_config_frame, text="Unknown")
steamcmd_exe_result_label.grid(column=2, row=3)

backup_directory_button = ctk.CTkButton(server_config_frame, text="Select Backup Directory:", command=select_backup_directory)
backup_directory_button.grid(column=0, row=4, padx=10, pady=10)

backup_directory_selection = ctk.CTkLabel(server_config_frame, text="No Directory Selected")
backup_directory_selection.grid(column=1, row=4, sticky="w")

backup_result_label = ctk.CTkLabel(server_config_frame, text="Unknown")
backup_result_label.grid(column=2, row=4)

server_start_args_label = ctk.CTkLabel(server_config_frame, text="Server Startup Arguments:")
server_start_args_label.grid(column=0, row=5, padx=10, pady=10)

server_start_args_entry = ctk.CTkEntry(server_config_frame, width=600)
server_start_args_entry.grid(column=1, row=5, columnspan=2, sticky="w")

###################### Alerts Tab ###################################################
###################### Email Configuration Frame ####################################
email_config_frame = ctk.CTkFrame(notificationsTab)
email_config_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

email_config_button = ctk.CTkSegmentedButton(email_config_frame, values=["Email Configuration"], state="disabled")
email_config_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

show_email_password_checkbox_var = ctk.StringVar(value="False")
show_email_password_checkbox = ctk.CTkCheckBox(email_config_frame, text="Show Email Password", variable=show_email_password_checkbox_var, command=email_show, onvalue="True", offvalue="False")
show_email_password_checkbox.grid(column=1, row=0, columnspan=2, padx=(20,0), pady=(0,5), sticky="w")

email_address_label = ctk.CTkLabel(email_config_frame, text="Email Address:")
email_address_label.grid(column=0, row=1, pady=(0, 4), padx=10, sticky="w")

email_address_entry = ctk.CTkEntry(email_config_frame, width=280)
email_address_entry.grid(column=1, row=1, pady=(0, 4), sticky="w")

email_password_label = ctk.CTkLabel(email_config_frame, text="Email Password:")
email_password_label.grid(column=0, row=2, pady=(0, 4), padx=10, sticky="w")

email_password_entry = ctk.CTkEntry(email_config_frame, show="•", width=280)
email_password_entry.grid(column=1, row=2, pady=(0, 4), sticky="w")

smtp_server_label = ctk.CTkLabel(email_config_frame, text="SMTP Server:")
smtp_server_label.grid(column=0, row=3, pady=(0, 4), padx=10, sticky="w")

smtp_server_entry = ctk.CTkEntry(email_config_frame)
smtp_server_entry.grid(column=1, row=3, pady=(0, 4), sticky="w")

smtp_port_label = ctk.CTkLabel(email_config_frame, text="SMTP Port:")
smtp_port_label.grid(column=0, row=4, padx=10, sticky="w")

smtp_port_entry = ctk.CTkEntry(email_config_frame, width=40)
smtp_port_entry.grid(column=1, row=4, sticky="w")

###################### Discord Configuration Frame ####################################

discord_frame = ctk.CTkFrame(notificationsTab)
discord_frame.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")

discord_button = ctk.CTkSegmentedButton(discord_frame, values=["Discord Configuration"], state="disabled")
discord_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

show_discord_data_checkbox_var = ctk.StringVar(value="False")
show_discord_data_checkbox = ctk.CTkCheckBox(discord_frame, text="Show Discord Data", variable=show_discord_data_checkbox_var, command=discord_show, onvalue="True", offvalue="False")
show_discord_data_checkbox.grid(column=1, row=0, columnspan=2, pady=(0,5), sticky="w")

discordLabel = ctk.CTkLabel(discord_frame, text="Discord Webhook URL:")
discordLabel.grid(column=0, row=1, pady=(0, 4), padx=10)

discordUrlEntry = ctk.CTkEntry(discord_frame, show="•", width=280)
discordUrlEntry.grid(column=1, row=1, pady=(0, 4))

discordTestButton = ctk.CTkButton(discord_frame, text="Send Test Message", command=send_discord_message)
discordTestButton.grid(column=0, row=2, columnspan=2, pady=2)

###################### Theme Configuration Frame ####################################

theme_mode_frame = ctk.CTkFrame(personalizationTab)
theme_mode_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

theme_mode_button = ctk.CTkSegmentedButton(theme_mode_frame, values=["Appearance Mode"], state="disabled")
theme_mode_button.grid(column=0, row=0, columnspan=2, pady=(0,10), sticky="w")

theme_radio_var = ctk.StringVar(value="System")
systemradiobutton = ctk.CTkRadioButton(theme_mode_frame, text="System Default", command=change_appearance_mode, variable=theme_radio_var, value="System")
systemradiobutton.grid(column=0, row=1, padx=(0,5), sticky="w")

darkradiobutton = ctk.CTkRadioButton(theme_mode_frame, text="Dark Mode", command=change_appearance_mode, variable=theme_radio_var, value="Dark")
darkradiobutton.grid(column=1, row=1, padx=(5,0), sticky="w")

lightradiobutton = ctk.CTkRadioButton(theme_mode_frame, text="Light Mode", command=change_appearance_mode, variable=theme_radio_var, value="Light")
lightradiobutton.grid(column=2, row=1, padx=(5,0), sticky="w")

theme_color_frame = ctk.CTkFrame(personalizationTab)
theme_color_frame.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

theme_color_button = ctk.CTkSegmentedButton(theme_color_frame, values=["Theme Color (Restart Required)"], state="disabled")
theme_color_button.grid(column=0, row=0, columnspan=3, pady=(0,10), sticky="w")

theme_color_radio_var = ctk.StringVar(value="blue")
blueradiobutton = ctk.CTkRadioButton(theme_color_frame, text="Blue", command=change_theme_color, variable=theme_color_radio_var, value="blue")
blueradiobutton.grid(column=0, row=1, sticky="w")

darkblueradiobutton = ctk.CTkRadioButton(theme_color_frame, text="Dark Blue", command=change_theme_color, variable=theme_color_radio_var, value="dark-blue")
darkblueradiobutton.grid(column=1, row=1, padx=(5,0), sticky="w")

greenradiobutton = ctk.CTkRadioButton(theme_color_frame, text="Green", command=change_theme_color, variable=theme_color_radio_var, value="green")
greenradiobutton.grid(column=2, row=1, padx=(5,0), sticky="w")

customradiobutton = ctk.CTkRadioButton(theme_color_frame, text="Custom", command=change_theme_color, variable=theme_color_radio_var, value="custom")
customradiobutton.grid(column=3, row=1, padx=(5,0), sticky="w")

theme_file_button = ctk.CTkButton(theme_color_frame, text="Select a Theme File", command=change_theme_color, state="disabled")
theme_file_button.grid(column=4, row=1, padx=(5,0), sticky="w")

scaling_frame = ctk.CTkFrame(personalizationTab)
scaling_frame.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")

scaling_button = ctk.CTkSegmentedButton(scaling_frame, values=["Application Scaling (Restart Required)"], state="disabled")
scaling_button.grid(column=0, row=0, columnspan=2, pady=(0,10), sticky="w")

widgetscalingLabel = ctk.CTkLabel(scaling_frame, text="DPI Awareness:")
widgetscalingLabel.grid(column=0, row=1, pady=(0,10), sticky="w")

dpiawarenessoptionmenu_var = ctk.StringVar(value="Enabled")
dpiawarenessoptionmenu = ctk.CTkOptionMenu(scaling_frame, values=["Enabled", "Disabled"], variable=dpiawarenessoptionmenu_var)
dpiawarenessoptionmenu.grid(column=1, row=1, pady=(0,10), sticky="w")

dpiawarenessButton = ctk.CTkButton(scaling_frame, text="Apply", command=change_automatic_dpi_awareness)
dpiawarenessButton.grid(column=2, row=1, pady=(0,10), sticky="w")

widgetscalingLabel = ctk.CTkLabel(scaling_frame, text="Content Scaling:")
widgetscalingLabel.grid(column=0, row=2, pady=(0,10), sticky="w")

widgetscalingComboBox_var = ctk.StringVar(value="Default")
widgetscalingComboBox = ctk.CTkComboBox(scaling_frame, values=["Default", "50%", "60%", "70%","80%", "90%", "100%", "110%", "120%", "130%", "140%", "150%"], variable=widgetscalingComboBox_var)
widgetscalingComboBox.grid(column=1, row=2, padx=(5,0), pady=(0,10), sticky="w")

widgetscalingButton = ctk.CTkButton(scaling_frame, text="Apply", command=change_widget_scaling)
widgetscalingButton.grid(column=2, row=2, padx=(5,0), pady=(0,10), sticky="w")

windowscalingLabel = ctk.CTkLabel(scaling_frame, text="Window Scaling:")
windowscalingLabel.grid(column=0, row=3, pady=(0,10), sticky="w")

windowscalingComboBox_var = ctk.StringVar(value="Default")
windowscalingComboBox = ctk.CTkComboBox(scaling_frame, values=["Default", "50%", "60%", "70%","80%", "90%", "100%", "110%", "120%", "130%", "140%", "150%"], variable=windowscalingComboBox_var)
windowscalingComboBox.grid(column=1, row=3, padx=(5,0), sticky="w")

windowscalingButton = ctk.CTkButton(scaling_frame, text="Apply", command=change_window_scaling)
windowscalingButton.grid(column=2, row=3, padx=(5,0), sticky="w")

###################### About Tab ###################################################

app_info_frame = ctk.CTkFrame(aboutTab)
app_info_frame.grid(column=0, row=0, padx=10, pady=10, sticky="nsew")

app_info_button = ctk.CTkSegmentedButton(app_info_frame, values=["About Application"], state="disabled")
app_info_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="w")

app_logo_image = ctk.CTkImage(light_image=Image.open(LOGO_PNG_FILE), dark_image=Image.open(LOGO_PNG_FILE), size=(56, 56))

app_image_label = ctk.CTkLabel(app_info_frame, image=app_logo_image, text="")
app_image_label.grid(column=0, row=1, padx=(0,5), pady=5, rowspan=2, sticky="w")

app_name_label = ctk.CTkLabel(app_info_frame, text=Application_Name)
app_name_label.grid(column=1, row=1, padx=(5,0), pady=(5,0), sticky="w")

app_version_label = ctk.CTkLabel(app_info_frame, text=f"Version {Application_Local_Version} (Forked build)")
app_version_label.grid(column=1, row=2, padx=(5,0), pady=(0,0), sticky="w")

app_info_buttons_frame = ctk.CTkFrame(aboutTab)
app_info_buttons_frame.grid(column=0, row=2, padx=10, pady=10, sticky="nsew")

about_functions_optionmenu = ctk.CTkOptionMenu(app_info_buttons_frame, values=["Check for Updates", "Report a Bug", "Donate to Andrew1175", "Donate to xKillerMaverick", "Exit Application"])
about_functions_optionmenu.grid(column=0, row=0, padx=(0,5), sticky="w")
about_functions_optionmenu.set("Select a Option")

app_run_button = ctk.CTkButton(app_info_buttons_frame, text="Run", command=functions_run_button_click)
app_run_button.grid(column=1, row=0, padx=(0,5), sticky="w")

support_frame = ctk.CTkFrame(aboutTab)
support_frame.grid(column=0, row=3, padx=10, pady=10, sticky="nsew")
support_frame.columnconfigure(0, weight=1)

about_label = ctk.CTkLabel(support_frame, text="This application is completely free and no features will ever be behind a paywall." + "\n" + "This application was created by Andrew1175 and then later modified by xKillerMaverick." + "\n" + "If you would like to support the development of this application, please consider donating to Andrew1175 or xKillerMaverick." + "\n" + "This application is not affiliated with Palworld or any of its developers. This application is a fan-made tool for the game.")
about_label.grid(column=0, row=0)

supporters_frame = ctk.CTkFrame(aboutTab)
supporters_frame.grid(column=0, row=4, padx=10, pady=10, sticky="nsew")
supporters_frame.columnconfigure(0, weight=1)

donations_label = ctk.CTkLabel(supporters_frame, justify="center",  text="Special Thanks from Andrew1175 to the Following Supporters: daisame.bsky.social, CBesty")
donations_label.grid(column=0, row=0)

changelog_frame = ctk.CTkFrame(aboutTab)
changelog_frame.grid(column=0, row=5, padx=10, pady=10, sticky="nsew")
changelog_frame.columnconfigure(0, weight=1)

app_info_button = ctk.CTkSegmentedButton(changelog_frame, values=["Application Changelog"], state="disabled")
app_info_button.grid(column=0, row=0, columnspan=2, pady=(0,5), sticky="nsew")

changelog_textbox = ctk.CTkTextbox(changelog_frame, wrap="word", height=190, width=680, state="disabled")
changelog_textbox.grid(column=0, row=1, sticky="nsew")

###################### Console Output Frame ###################################################

outputFrame = ctk.CTkFrame(root)
outputFrame.pack(side="bottom", expand=True, fill="both")

output_button = ctk.CTkSegmentedButton(outputFrame, values=["Console Window:"], state="disabled")
output_button.pack()

# text widget for the output
output_text = ctk.CTkTextbox(outputFrame, wrap="word", height=80, width=680, state="disabled")
output_text.pack(padx=10, pady=10, expand=True, fill="both")

load_settings()
load_widget_settings()

root.protocol("WM_DELETE_WINDOW", on_exit)
root.after(10, lambda: center_window(root))
root.mainloop()
