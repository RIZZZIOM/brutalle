
![](img/banner.png)

# BRUTALLE 🛠️

**brutalle** is a Python-based command-line tool designed to feel like a mini hacking toolkit. It’s got some neat functionalities like reverse shell listening, file transfer over SSH, a self-destruct mechanism, and an interactive shell mode — all things that make this script feel a bit more *"cyber"* while actually being a fun way to learn about network programming, system commands, and Python libraries!

# FEATURES ✨

- **Interactive Shell Mode**: Offers a basic shell interface where you can execute commands, use tab to complete filenames and view command history.
- **Reverse Shell Listener**: Sets up a reverse shell listener to accept incoming connections from a remote system.
- **SSH File Transfer**: Securely transfer files to and from a target system over SSH.
- **Self-Destruct Mechanism**: When you're done, use `kill` to delete the tool and any files created by it, leaving no trace behind.

# REQUIREMENTS 📝

- **Python 3.x**
- **Required Libraries**:
  - `paramiko` for SSH connection and file transfer.
  - `readline` or `pyreadline3` (for Windows) to enable command history and tab completion.
  - `shutil`, `subprocess`, and other built-in libraries included with Python.

# INSTALLATION 🚀

Clone the repository and navigate to it:

```bash
git clone <url>
cd brutalle
```

### **For Windows**:
1. Run the setup script to install dependencies:

    ```bash
    python setup.py
    ```

2. Run the tool:

    ```bash
    python brutalle.py
    ```

### **For Linux**:
1. Make the scripts executable and run the setup:

    ```bash
    chmod +x brutalle.py setup.py
    ./setup.py
    ```

2. Run the main script:

    ```bash
    ./brutalle.py
    ```

# USAGE 📖

Here’s a quick rundown of the available commands, their arguments, and usage examples.

| **COMMAND** | **ARGUMENTS**    | **DESCRIPTION**                           | **EXAMPLE USAGE**              |
|-------------|------------------|-------------------------------------------|--------------------------------|
| `help`      | None             | Lists all available commands              | `help`                         |
| `shell`     | None             | Starts interactive shell mode             | `shell`                        |
| `reverse`   | port             | Starts a reverse shell listener on a port | `reverse 4444`                 |
| `put`       | target, username | Uploads a file to the target via SSH      | `put 192.168.1.10 myusername`  |
| `get`       | target, username | Downloads a file from the target via SSH  | `get 192.168.1.10 myusername`  |
| `exit`      | None             | Exits the tool                            | `exit`                         |
| `kill`      | None             | Executes the self-destruct sequence       | `kill`                         |

> **Note**: Make sure SSH login credentials are handy when using `put` or `get`, as the script will prompt you for the password.

# CONTRIBUTING 🤝

Contributions are welcome! Feel free to fork the repo, make your changes, and submit a pull request. If you’re adding features, please try to include relevant tests, and keep things consistent with the existing style.

# LICENSE 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

--- 

