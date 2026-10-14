
import platform
import socket
import subprocess

import psutil
from PySide6.QtCore import QTimer, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QTableWidget,
    QMessageBox,
    QTableWidgetItem,

)


STYLE = """
QMainWindow, QWidget {
    background-color: #171719;
    color: #eeeeef;
    font-family: sans-serif;
    font-size: 13px;
}
QFrame#card {
    background-color: #222225;
    border: 1px solid #343438;
    border-radius: 12px;
}
QLabel#muted { color: #a0a0a8; }
QLabel#metric {
    color: #f4f4f5;
    font-size: 25px;
    font-weight: bold;
}
QLabel#sectionTitle {
    font-size: 15px;
    font-weight: bold;
}
QPushButton {
    background-color: #8f2638;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 16px;
    font-weight: bold;
}
QPushButton:hover { background-color: #aa3045; }
QPushButton:disabled {
    background-color: #4a3035;
    color: #b8aeb0;
}
"""


def run_command(command, timeout=3):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def get_network_info():
    info = {
        "interface": "Bulunamadı",
        "ip": "Bulunamadı",
        "gateway": "Bulunamadı",
    }

    route = run_command(["ip", "route", "show", "default"])

    for line in route.splitlines():
        tokens = line.split()

        if "via" in tokens:
            info["gateway"] = tokens[tokens.index("via") + 1]

        if "dev" in tokens:
            info["interface"] = tokens[tokens.index("dev") + 1]

        break

    interface = info["interface"]

    if interface != "Bulunamadı":
        address = run_command(
            ["ip", "-4", "-o", "addr", "show", "dev", interface]
        )

        for line in address.splitlines():
            tokens = line.split()

            if "inet" in tokens:
                info["ip"] = tokens[tokens.index("inet") + 1]
                break

    return info


def make_card(title, value="--", subtitle=""):
    card = QFrame()
    card.setObjectName("card")

    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(7)

    title_label = QLabel(title)
    title_label.setObjectName("muted")

    value_label = QLabel(value)
    value_label.setObjectName("metric")

    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("muted")
    subtitle_label.setWordWrap(True)

    layout.addWidget(title_label)
    layout.addWidget(value_label)
    layout.addWidget(subtitle_label)
    layout.addStretch()

    return card, value_label, subtitle_label


class DiagnosticWorker(QThread):
    result_ready = Signal(str)

    def run(self):
        results = []
        net = get_network_info()
        gateway = net["gateway"]

        # Ağ geçidi testi
        if gateway != "Bulunamadı":
            ok = SysPilot.ping_host(gateway)
            status = "BAŞARILI" if ok else "BAŞARISIZ"
            results.append(f"{status} — Ağ geçidi ({gateway})")
        else:
            results.append("ATLANDI — Ağ geçidi bulunamadı")

        # İnternet erişimi testi
        ok = SysPilot.ping_host("1.1.1.1")
        status = "BAŞARILI" if ok else "BAŞARISIZ"
        results.append(f"{status} — İnternet erişimi (1.1.1.1)")

        # DNS testi
        try:
            socket.getaddrinfo("example.com", 443)
            results.append("BAŞARILI — DNS çözümlemesi")
        except socket.gaierror:
            results.append("BAŞARISIZ — DNS çözümlemesi")
        except OSError as error:
            results.append(f"HATA — DNS: {error}")

        self.result_ready.emit("\n".join(results))
    


class SysPilot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SysPilot | IT Diagnostic Assistant")
        self.resize(900, 680)
        self.setMinimumSize(740, 560)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title_layout = QVBoxLayout()

        title = QLabel("SysPilot")
        title.setStyleSheet(
            "font-size: 30px; font-weight: bold; color: #f4f4f5;"
        )

        subtitle = QLabel("Sistem izleme ve IT tanılama paneli")
        subtitle.setObjectName("muted")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.scan_button = QPushButton("Taramayı Başlat")
        self.scan_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_button.clicked.connect(self.run_diagnostics)
        self.close_button = QPushButton("Kapat")
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #343438;
                color: #eeeeef;
                border: 1px solid #55555b;
                border-radius: 8px;
                padding: 11px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8f2638;
            }
        """)
        self.close_button.clicked.connect(self.close)

        header.addLayout(title_layout)
        header.addStretch()
        header.addWidget(self.scan_button)
        header.addWidget(self.close_button)
        root.addLayout(header)

        # System metric cards
        grid = QGridLayout()
        grid.setSpacing(12)

        cpu_card, self.cpu_value, self.cpu_sub = make_card(
            "CPU KULLANIMI", "--", "İşlemci yükü"
        )
        ram_card, self.ram_value, self.ram_sub = make_card(
            "RAM KULLANIMI", "--", "Bellek kullanımı"
        )
        disk_card, self.disk_value, self.disk_sub = make_card(
            "DİSK KULLANIMI", "--", "Kök dizin"
        )
        net_card, self.net_value, self.net_sub = make_card(
            "AĞ ARAYÜZÜ", "--", "Aktif ağ"
        )

        grid.addWidget(cpu_card, 0, 0)
        grid.addWidget(ram_card, 0, 1)
        grid.addWidget(disk_card, 1, 0)
        grid.addWidget(net_card, 1, 1)

        root.addLayout(grid)

        # System details
        details_card = QFrame()
        details_card.setObjectName("card")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(16, 14, 16, 14)

        details_title = QLabel("Sistem Bilgileri")
        details_title.setObjectName("sectionTitle")

        self.system_label = QLabel()
        self.system_label.setWordWrap(True)
        self.system_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.network_label = QLabel()
        self.network_label.setWordWrap(True)
        self.network_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        details_layout.addWidget(details_title)
        details_layout.addWidget(self.system_label)
        details_layout.addWidget(self.network_label)
        root.addWidget(details_card)

        # Diagnostic results
        results_card = QFrame()
        results_card.setObjectName("card")
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(16, 14, 16, 14)

        results_title = QLabel("Tanılama Sonuçları")
        results_title.setObjectName("sectionTitle")

        self.results_label = QLabel(
            "Henüz tarama yapılmadı. Testleri başlatmak için düğmeye bas."
        )
        self.results_label.setWordWrap(True)
        self.results_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        results_layout.addWidget(results_title)
        results_layout.addWidget(self.results_label)
        root.addWidget(results_card)

        # Running processes section
        process_card = QFrame()
        process_card.setObjectName("card")

        process_layout = QVBoxLayout(process_card)
        process_layout.setContentsMargins(16, 14, 16, 14)
        process_layout.setSpacing(10)

        process_header = QHBoxLayout()

        process_title = QLabel("Çalışan İşlemler")
        process_title.setObjectName("sectionTitle")

        self.process_refresh_button = QPushButton("Listeyi Yenile")
        self.process_refresh_button.clicked.connect(
            self.refresh_processes
        )

        process_header.addWidget(process_title)
        process_header.addStretch()
        process_header.addWidget(self.process_refresh_button)

        process_layout.addLayout(process_header)

        self.process_table = QTableWidget(0, 4)
        self.process_table.setHorizontalHeaderLabels(
            ["İşlem Adı", "PID", "CPU (%)", "RAM (MB)"]
        )

        self.process_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.process_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setSortingEnabled(False)
        self.process_table.verticalHeader().setVisible(False)

        self.process_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.process_table.setMinimumHeight(180)
        self.process_table.setMaximumHeight(300)

        process_layout.addWidget(self.process_table)

        self.terminate_button = QPushButton("Seçili İşlemi Sonlandır")
        self.terminate_button.setStyleSheet("""
            QPushButton {
                background-color: #8f2638;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #aa3045;
            }
        """)
        self.terminate_button.clicked.connect(
            self.terminate_selected_process
        )
        process_layout.addWidget(self.terminate_button)

        root.addWidget(process_card)


        self.status_label = QLabel("Hazır")
        self.status_label.setObjectName("muted")
        root.addWidget(self.status_label)

        psutil.cpu_percent(interval=None)
        self.refresh_data()
        self.refresh_processes()

    def terminate_selected_process(self):
        row = self.process_table.currentRow()

        if row < 0:
            QMessageBox.information(
                self,
                "İşlem seçilmedi",
                "Lütfen tablodan bir işlem seç."
            )
            return

        pid_item = self.process_table.item(row, 1)
        name_item = self.process_table.item(row, 0)

        if pid_item is None or name_item is None:
            return

        try:
            pid = int(pid_item.text())
            process_name = name_item.text()

            if pid == 1 or pid == psutil.Process().pid:
                QMessageBox.warning(
                    self,
                    "İşlem korunuyor",
                    "Bu işlem güvenlik nedeniyle sonlandırılamaz."
                )
                return

            answer = QMessageBox.question(
                self,
                "İşlemi sonlandır",
                f"{process_name} (PID: {pid}) işlemini "
                "sonlandırmak istiyor musun?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

            process = psutil.Process(pid)

            # PID aynı kalsa bile işlemin değişmiş olma ihtimalini azaltır.
            if process.name() != process_name:
                QMessageBox.warning(
                    self,
                    "İşlem değişti",
                    "İşlem bilgisi değişmiş. Listeyi yenileyip tekrar dene."
                )
                self.refresh_processes()
                return

            process.terminate()

            QMessageBox.information(
                self,
                "İstek gönderildi",
                f"{process_name} işlemine sonlandırma isteği gönderildi."
            )

            self.refresh_processes()

        except psutil.NoSuchProcess:
            QMessageBox.warning(
                self, "İşlem bulunamadı",
                "İşlem zaten kapanmış olabilir."
            )
        except psutil.AccessDenied:
            QMessageBox.warning(
                self, "Erişim reddedildi",
                "Bu işlemi sonlandırmak için yetkin yok."
            )
        except (ValueError, OSError) as error:
            QMessageBox.warning(
                self, "Hata",
                f"İşlem sonlandırılamadı:\n{error}"
            )


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(3000)

    def refresh_data(self):
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        net = get_network_info()

        try:
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_text = (
                f"{disk.used / (1024 ** 3):.1f} GB / "
                f"{disk.total / (1024 ** 3):.1f} GB kullanılıyor"
            )
        except OSError:
            disk_percent = 0
            disk_text = "Disk bilgisi alınamadı"

        self.cpu_value.setText(f"{cpu:.0f}%")
        self.cpu_sub.setText("Anlık işlemci kullanımı")

        self.ram_value.setText(f"{memory.percent:.0f}%")
        self.ram_sub.setText(
            f"{memory.used / (1024 ** 3):.1f} GB / "
            f"{memory.total / (1024 ** 3):.1f} GB kullanılıyor"
        )

        self.disk_value.setText(f"{disk_percent:.0f}%")
        self.disk_sub.setText(disk_text)

        self.net_value.setText(net["interface"])
        self.net_sub.setText(f"Yerel IP: {net['ip']}")

        self.system_label.setText(
            f"İşletim sistemi: {platform.system()} {platform.release()}\n"
            f"Dağıtım: {platform.platform()}\n"
            f"Bilgisayar adı: {socket.gethostname()}\n"
            f"Mimari: {platform.machine()} | "
            f"Python: {platform.python_version()}\n"
            f"Çalışma süresi: {self.get_uptime()}"
        )

        self.network_label.setText(
            f"Ağ arayüzü: {net['interface']}  |  "
            f"Yerel IP: {net['ip']}  |  "
            f"Ağ geçidi: {net['gateway']}"
        )
    

    def refresh_processes(self):
        self.process_refresh_button.setEnabled(False)
        self.process_refresh_button.setText("Yükleniyor...")

        try:
            processes = []

            for proc in psutil.process_iter(
                ["pid", "name", "memory_info"]
            ):
                try:
                    info = proc.info
                    memory_info = info.get("memory_info")

                    if not memory_info:
                        continue

                    cpu = proc.cpu_percent(interval=None)
                    ram_mb = memory_info.rss / (1024 * 1024)

                    processes.append({
                        "name": info.get("name") or "Bilinmiyor",
                        "pid": info["pid"],
                        "cpu": cpu,
                        "ram": ram_mb,
                    })

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            # En fazla RAM kullanan işlemler üstte görünsün.
            processes.sort(
                key=lambda item: item["ram"],
                reverse=True,
            )

            self.process_table.setRowCount(len(processes))

            for row, proc in enumerate(processes):
                values = [
                    proc["name"],
                    str(proc["pid"]),
                    f"{proc['cpu']:.1f}",
                    f"{proc['ram']:.1f}",
                ]

                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)

                    if column in (1, 2, 3):
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignCenter
                        )

                    self.process_table.setItem(
                        row, column, item
                    )

            self.status_label.setText(
                f"{len(processes)} işlem listelendi"
            )

        except Exception as error:
            self.status_label.setText(
                f"İşlem listesi alınamadı: {error}"
            )

        finally:
            self.process_refresh_button.setEnabled(True)
            self.process_refresh_button.setText("Listeyi Yenile")


    @staticmethod
    def get_uptime():
        try:
            with open("/proc/uptime", encoding="utf-8") as file:
                seconds = int(float(file.readline().split()[0]))

            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes = seconds // 60

            return f"{days} gün, {hours} saat, {minutes} dakika"
        except (OSError, ValueError, IndexError):
            return "Bilinmiyor"

    @staticmethod
    def ping_host(host, timeout=3):
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout), host],
                capture_output=True,
                text=True,
                timeout=timeout + 2,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def run_diagnostics(self):
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Taranıyor...")
        self.status_label.setText("Tanılama arka planda çalışıyor...")
        self.results_label.setText("Testler devam ediyor...")

        self.worker = DiagnosticWorker()
        self.worker.result_ready.connect(self.show_diagnostic_results)
        self.worker.finished.connect(self.diagnostics_finished)
        self.worker.start()

    def show_diagnostic_results(self, results):
        self.results_label.setText(results)

    def diagnostics_finished(self):
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Taramayı Başlat")
        self.status_label.setText("Tanılama tamamlandı")


def main():
    app = QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)

    window = SysPilot()
    window.show()

    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
