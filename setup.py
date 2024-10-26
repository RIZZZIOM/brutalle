#!/bin/python3

import platform
import subprocess
import sys


def install_package(package):
    """
    Installs a specified Python package using pip.

    Parameters:
        package (str): The name of the package to install.
    """
    if platform.system() == "Windows":
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    else:
        subprocess.check_call(["pip install", package])

def main():
    """
    Installs the required packages for the project.

    This function checks the operating system and installs the appropriate 
    packages to ensure compatibility with the script. Outputs installation status.
    """
    # Required packages
    packages = [
        "paramiko",
        "pyreadline3" if platform.system() == "Windows" else "readline"
    ]

    print("Installing required packages...")

    # Install each package
    for package in packages:
        try:
            print(f"Installing {package}...")
            install_package(package)
            print(f"{package} installed successfully!")
        except Exception as e:
            print(f"Error installing {package}: {e}")

    print("All packages installed successfully!")

if __name__ == "__main__":
    main()
