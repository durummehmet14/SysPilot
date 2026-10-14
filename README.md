# SysPilot

**A Lightweight Desktop IT Diagnostics Tool Built with Python**

SysPilot is a desktop application designed to simplify basic system monitoring and network troubleshooting. It provides essential system information, real-time resource monitoring, and network diagnostic tools through a graphical interface.

## Features

- **System Monitoring:** Monitor CPU, RAM, and disk usage.
- **Network Information:** View network interfaces, local IP addresses, and gateway information.
- **Network Diagnostics:** Test gateway connectivity, internet connectivity, and DNS resolution.
- **Process Management:** View running processes, including their PIDs, CPU usage, and memory consumption.
- **Process Termination:** Terminate selected processes with confirmation.
- **Graphical User Interface:** A dark-themed interface built with PySide6.
- **Responsive Diagnostics:** Run network checks in a separate thread to help keep the interface responsive.

## Technologies

- Python
- PySide6
- psutil
- Git & GitHub

## Requirements

- Python 3.10 or later
- pip
- Linux or another environment compatible with the required Python dependencies

## Installation

Clone the repository:

```bash
git clone https://github.com/durummehmet14/SysPilot.git
cd SysPilot
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install PySide6 psutil
```

## Usage

Run the application:

```bash
python gui.py
```

Use the dashboard to monitor system resources, inspect network information, run connectivity tests, and manage running processes.

## Project Goals

SysPilot is a personal project focused on practical IT support, system administration, and troubleshooting. Its goal is to bring commonly used diagnostic tasks together in one accessible desktop application.

## Future Improvements

- Disk health monitoring
- Low disk space warnings
- More detailed network diagnostics
- System information export
- Additional troubleshooting tools

## Author

**Mehmet Durum**

- GitHub: [@durummehmet14](https://github.com/durummehmet14)

---

*SysPilot is an ongoing learning project. Features and documentation may evolve as development continues.*
