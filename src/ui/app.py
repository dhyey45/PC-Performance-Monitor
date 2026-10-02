import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QButtonGroup, QFrame, QGridLayout,
                               QHBoxLayout, QHeaderView, QLabel, QListWidget, QListWidgetItem,
                               QMainWindow, QProgressBar, QPushButton, QStackedWidget,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from src.alerts import AlertManager
from src.monitor import collect
from src.performance import History, compute_score, grade
from src.processes import top_processes
from src.ui.theme import ACCENT, STYLE, status_color
from src.ui.widgets import AreaChart, MetricCard, RingGauge

ASSETS = Path(__file__).resolve().parents[2] / "assets"


def card(layout_cls=QVBoxLayout, margins=(20, 16, 20, 16)):
    f = QFrame()
    f.setObjectName("card")
    lay = layout_cls(f)
    lay.setContentsMargins(*margins)
    return f, lay


def label(text, name):
    l = QLabel(text)
    l.setObjectName(name)
    return l


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Performance Monitor")
        self.resize(1180, 780)
        self.history, self.alerts, self.bars = History(), AlertManager(), {}
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        self.pages = QStackedWidget()
        h.addWidget(self._sidebar())
        h.addWidget(self.pages, 1)
        for build in (self._dashboard, self._processes, self._history, self._alerts):
            self.pages.addWidget(build())
        self.pages.currentChanged.connect(lambda i: self._refresh_history() if i == 2 else None)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    # ---------- layout ----------
    def _sidebar(self):
        f = QFrame()
        f.setObjectName("sidebar")
        f.setFixedWidth(210)
        v = QVBoxLayout(f)
        v.setContentsMargins(16, 26, 16, 18)
        v.addWidget(label("◉  PerfMonitor", "logo"))
        v.addSpacing(20)
        self.group = QButtonGroup(self)
        for i, name in enumerate(("Dashboard", "Processes", "History", "Alerts")):
            b = QPushButton(name)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setChecked(i == 0)
            b.setCursor(Qt.PointingHandCursor)
            self.group.addButton(b, i)
            v.addWidget(b)
        self.group.idClicked.connect(self.pages.setCurrentIndex)
        v.addStretch()
        v.addWidget(label("● Live · refreshes every second", "cardSub"))
        return f

    def _page(self, title):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(28, 26, 28, 24)
        v.setSpacing(16)
        v.addWidget(label(title, "h1"))
        return page, v

    def _dashboard(self):
        page, v = self._page("Dashboard")
        top, t = card(QHBoxLayout, (24, 16, 24, 16))
        self.score_ring = RingGauge("SCORE", ACCENT["cpu"], unit="")
        self.score_ring.setFixedSize(150, 150)
        info = QVBoxLayout()
        info.addStretch()
        self.grade_lbl, self.tip_lbl = label("", "grade"), label("", "cardSub")
        info.addWidget(label("PERFORMANCE SCORE", "cardTitle"))
        info.addWidget(self.grade_lbl)
        info.addWidget(self.tip_lbl)
        info.addStretch()
        t.addWidget(self.score_ring)
        t.addSpacing(20)
        t.addLayout(info, 1)
        v.addWidget(top)
        grid = QGridLayout()
        grid.setSpacing(16)
        self.cards = {"cpu": MetricCard("CPU", ACCENT["cpu"]), "ram": MetricCard("MEMORY", ACCENT["ram"]),
                      "gpu": MetricCard("GPU", ACCENT["gpu"]), "temp": MetricCard("TEMPERATURE", ACCENT["temp"])}
        for i, c in enumerate(self.cards.values()):
            grid.addWidget(c, i // 2, i % 2)
        v.addLayout(grid, 1)
        self.disk_box, self.disk_lay = card()
        self.disk_lay.setSpacing(8)
        self.disk_title = label("STORAGE", "cardTitle")
        self.disk_lay.addWidget(self.disk_title)
        v.addWidget(self.disk_box)
        return page

    def _processes(self):
        page, v = self._page("Processes")
        box, lay = card()
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["PID", "NAME", "CPU %", "MEMORY (MB)"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        lay.addWidget(self.table)
        v.addWidget(box, 1)
        return page

    def _history(self):
        page, v = self._page("Performance history")
        row = QHBoxLayout()
        row.setSpacing(16)
        self.stats = {}
        for key, title in (("avg_score", "AVG SCORE · 24H"), ("min_score", "LOWEST SCORE"),
                           ("avg_cpu", "AVG CPU"), ("avg_ram", "AVG MEMORY")):
            box, lay = card()
            self.stats[key] = label("–", "cardValue")
            lay.addWidget(label(title, "cardTitle"))
            lay.addWidget(self.stats[key])
            row.addWidget(box)
        v.addLayout(row)
        box, lay = card()
        lay.addWidget(label("SCORE · LAST 60 MINUTES", "cardTitle"))
        self.hist_chart = AreaChart(ACCENT["cpu"])
        lay.addWidget(self.hist_chart, 1)
        v.addWidget(box, 1)
        return page

    def _alerts(self):
        page, v = self._page("Alerts")
        box, lay = card()
        self.alert_list = QListWidget()
        lay.addWidget(self.alert_list)
        v.addWidget(box, 1)
        return page

    # ---------- updates ----------
    def refresh(self):
        s = collect()
        score, parts = compute_score(s)
        self.history.record(s, score)
        self.score_ring.animate_to(score, status_color(score))
        self.grade_lbl.setText(grade(score))
        worst = min(parts, key=parts.get)
        self.tip_lbl.setText("Everything looks smooth." if parts[worst] > 90
                             else f"Biggest drag on performance: {worst.upper()}")

        c, m, g = s.cpu, s.memory, s.gpu
        freq = f" · {c['freq_mhz'] / 1000:.1f} GHz" if c["freq_mhz"] else ""
        self.cards["cpu"].update_metric(f"{c['percent']:.0f}%", f"{c['cores']} cores · {c['threads']} threads{freq}", c["percent"])
        self.cards["ram"].update_metric(f"{m['percent']:.0f}%", f"{m['used_gb']:.1f} / {m['total_gb']:.1f} GB", m["percent"])
        if g:
            self.cards["gpu"].update_metric(f"{g['util']:.0f}%", f"{g['name']} · {g['mem_used_gb']:.1f}/{g['mem_total_gb']:.1f} GB", g["util"])
        else:
            self.cards["gpu"].update_metric("N/A", "No NVIDIA GPU detected")
        temps = {k: v for k, v in s.temps.items() if v is not None}
        if temps:
            self.cards["temp"].update_metric(f"{max(temps.values()):.0f}°C",
                                             " · ".join(f"{k.upper()} {v:.0f}°C" for k, v in temps.items()),
                                             max(temps.values()))
        else:
            self.cards["temp"].update_metric("N/A", "No temperature sensor available")
        self._update_storage(s.storage)

        for a in self.alerts.check(s):
            item = QListWidgetItem(f"{datetime.fromtimestamp(a.ts):%H:%M:%S}   {a.level.upper()}   {a.message}")
            item.setForeground(QColor("#F87171" if a.level == "critical" else "#FBBF24"))
            self.alert_list.insertItem(0, item)
        if self.pages.currentIndex() == 1:
            self._update_processes()

    def _update_storage(self, st):
        self.disk_title.setText(f"STORAGE     ↓ {st['read_mb_s']:.1f} MB/s    ↑ {st['write_mb_s']:.1f} MB/s")
        for p in st["partitions"][:5]:
            if p["mount"] not in self.bars:
                lbl, bar = QLabel(), QProgressBar()
                bar.setTextVisible(False)
                self.disk_lay.addWidget(lbl)
                self.disk_lay.addWidget(bar)
                self.bars[p["mount"]] = (lbl, bar)
            lbl, bar = self.bars[p["mount"]]
            lbl.setText(f"{p['mount']}   {p['used_gb']:.0f} / {p['total_gb']:.0f} GB  ({p['percent']:.0f}%)")
            bar.setValue(int(p["percent"]))

    def _update_processes(self):
        rows = top_processes(15)
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate((r["pid"], r["name"], f"{r['cpu']:.1f}", f"{r['mem_mb']:.0f}")):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def _refresh_history(self):
        sm = self.history.summary(24)
        self.stats["avg_score"].setText(f"{sm['avg_score']:.0f}")
        self.stats["min_score"].setText(f"{sm['min_score']:.0f}")
        self.stats["avg_cpu"].setText(f"{sm['avg_cpu']:.0f}%")
        self.stats["avg_ram"].setText(f"{sm['avg_ram']:.0f}%")
        self.hist_chart.set_data(self.history.recent_scores(60))


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    app.setWindowIcon(QIcon(str(ASSETS / "icon.svg")))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
