
import platform
import subprocess
import re
import socket
import psutil
from datetime import datetime


def print_header():
    print("=" * 45)
    print("             SYSPILOT")
    print("       Kisisel IT Teshis Araci")
    print("=" * 45)


def get_system_info():
    print("\n[1] SISTEM BILGILERI")
    print("-" * 45)

    print(f"Bilgisayar adi  : {socket.gethostname()}")
    print(f"Isletim sistemi : {platform.system()}")
    print(f"Sistem surumu   : {platform.release()}")
    print(f"Makine mimarisi : {platform.machine()}")
    print(f"Python surumu   : {platform.python_version()}")


def format_bytes(size):
    return f"{size / (1024 ** 3):.2f} GB"


def get_resource_usage():
    print("\n[2] SISTEM KAYNAKLARI")
    print("-" * 45)

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    print(f"CPU kullanimi      : %{cpu:.1f}")
    print(f"RAM kullanimi      : %{memory.percent:.1f}")
    print(f"Toplam RAM         : {format_bytes(memory.total)}")
    print(f"Kullanilabilir RAM : {format_bytes(memory.available)}")
    print(f"Ana disk kullanimi : %{disk.percent:.1f}")
    print(f"Disk bos alani     : {format_bytes(disk.free)}")


def get_uptime():
    print("\n[3] SISTEM CALISMA SURESI")
    print("-" * 45)

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = int(datetime.now().timestamp() - psutil.boot_time())

    days, remainder = divmod(uptime, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    print(f"Son acilis : {boot_time:%d.%m.%Y %H:%M:%S}")
    print(f"Calisma    : {days} gun, {hours} saat, {minutes} dakika")


def get_network_info():
    print("\n[4] AG TESHisI")
    print("-" * 45)

    try:
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True,
            check=True
        )

        routes = result.stdout.splitlines()
        gateway = None
        interface = None

        for route in routes:
            if route.startswith("default"):
                gateway_match = re.search(r"default via (\S+)", route)
                interface_match = re.search(r"dev (\S+)", route)

                if gateway_match:
                    gateway = gateway_match.group(1)

                if interface_match:
                    interface = interface_match.group(1)

                break

        if interface:
            ip_result = subprocess.run(
                ["ip", "-4", "-o", "addr", "show", "dev", interface],
                capture_output=True,
                text=True,
                check=True
            )

            ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+/\d+)", ip_result.stdout)
            ip_address = ip_match.group(1) if ip_match else "Bulunamadi"

            print(f"Ağ arayüzü  : {interface}")
            print(f"Yerel IP    : {ip_address}")
            print(f"Ağ geçidi   : {gateway or 'Bulunamadi'}")
        else:
            print("Varsayilan ag rotasi bulunamadi.")

    except FileNotFoundError:
        print("'ip' komutu bulunamadi.")
    except subprocess.CalledProcessError:
        print("Ag bilgileri okunamadi.")



def main():
    print_header()
    get_system_info()
    get_resource_usage()
    get_uptime()
    get_network_info()

    print("\nAnaliz tamamlandi.")


if __name__ == "__main__":
    main()
