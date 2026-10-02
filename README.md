# 🖥️ PC Performance Monitor

A modern, real-time desktop system monitoring application built with **Python, PySide6, and psutil**.

PC Performance Monitor collects hardware and system statistics and presents them through a clean, dark-themed dashboard with live monitoring, performance scoring, process tracking, history, and intelligent alerts.

---

## ✨ Features

### 📊 Real-Time System Monitoring

Monitor your system continuously with live updates:

* **CPU**

  * Overall CPU usage
  * Physical cores
  * Logical threads
  * Current clock speed
  * Per-core monitoring support

* **Memory**

  * RAM usage percentage
  * Used memory
  * Total memory
  * Swap usage

* **GPU**

  * GPU utilization
  * VRAM usage
  * GPU name
  * GPU temperature
  * NVIDIA GPU support through NVML

* **Temperature**

  * CPU temperature when supported
  * GPU temperature through NVIDIA NVML
  * Graceful fallback when sensors are unavailable

* **Storage**

  * Disk usage
  * Used and available space
  * Read speed
  * Write speed
  * Multiple drive support

---

## ⚡ Performance Score

The application converts system metrics into a simple **0–100 performance score**.

The score considers:

* CPU load
* Memory usage
* GPU utilization
* Temperature
* Storage usage

It also provides a performance grade:

| Score    | Grade           |
| -------- | --------------- |
| 90–100   | Excellent       |
| 75–89    | Good            |
| 55–74    | Fair            |
| Below 55 | Needs Attention |

The scoring system is implemented in:

```text
src/performance/score.py
```

---

## 📈 Performance History

Performance samples are stored locally using **SQLite**.

The History page provides:

* Average performance score
* Lowest recorded score
* Average CPU usage
* Average memory usage
* Recent performance chart
* Persistent history across application restarts

Database location:

```text
~/.pc-performance-monitor/history.db
```

---

## ⚙️ Process Monitor

View the processes currently running on your computer.

The process monitor displays:

* Process ID
* Process name
* CPU usage
* Memory usage

Processes are automatically sorted by CPU usage.

---

## 🚨 Intelligent Alerts

The application monitors system thresholds and generates alerts when resource usage becomes unusually high.

Default thresholds include:

```text
CPU          90%
RAM          90%
GPU          95%
Temperature  85°C
Storage      90%
```

Alerts include:

* Warning level
* Critical level
* Timestamp
* Triggered metric
* Current value
* Configured threshold
* Cooldown protection to prevent repeated alerts

Thresholds can be customized in:

```text
src/alerts/alert_manager.py
```

---

## 🎨 User Interface

The application uses **PySide6** to provide a native desktop interface.

The interface contains four main sections:

```text
Dashboard
Processes
History
Alerts
```

The application refreshes live system information every second.

---

## 🛠️ Tech Stack

| Technology  | Purpose               |
| ----------- | --------------------- |
| Python      | Core application      |
| PySide6     | Desktop GUI           |
| psutil      | System monitoring     |
| NVIDIA NVML | NVIDIA GPU statistics |
| SQLite      | Performance history   |
| pytest      | Automated testing     |

---

## 📁 Project Structure

```text
pc-performance-monitor/
│
├── assets/
│   └── icon.svg
│
├── src/
│   ├── alerts/
│   │   └── alert_manager.py
│   │
│   ├── monitor/
│   │   ├── collector.py
│   │   ├── cpu.py
│   │   ├── gpu.py
│   │   ├── memory.py
│   │   ├── snapshot.py
│   │   ├── storage.py
│   │   └── temperature.py
│   │
│   ├── performance/
│   │   ├── history.py
│   │   └── score.py
│   │
│   ├── processes/
│   │   └── process_monitor.py
│   │
│   ├── ui/
│   │   ├── app.py
│   │   ├── theme.py
│   │   └── widgets.py
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_alerts.py
│   └── test_score.py
│
├── requirements.txt
├── pytest.ini
├── LICENSE
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/pc-performance-monitor.git
cd pc-performance-monitor
```

### 2. Create a virtual environment

#### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m src.main
```

---

## 🧪 Running Tests

Run the complete automated test suite:

```bash
pytest -q
```

The tests cover:

* Performance score calculation
* Score behavior under system load
* Optional GPU handling
* Alert thresholds
* Alert severity
* Alert cooldown behavior

---

## 🖥️ Platform Notes

### Windows

CPU, RAM, storage, process monitoring, and NVIDIA GPU monitoring are supported.

CPU temperature availability depends on the operating system's exposed hardware sensors.

### Linux

CPU temperature monitoring is supported when the relevant hardware sensors are exposed through `psutil`.

### NVIDIA GPU

NVIDIA GPU monitoring requires:

* An NVIDIA GPU
* Installed NVIDIA drivers
* NVIDIA Management Library support

If an NVIDIA GPU is unavailable, the application gracefully displays:

```text
GPU: N/A
```

---

## 🔒 Privacy

PC Performance Monitor is designed to run locally.

System metrics and performance history are processed locally on the machine.

No external server is required for the core monitoring functionality.

---

## 🗺️ Roadmap

Planned improvements:

* [ ] AMD GPU support
* [ ] Intel GPU support
* [ ] CSV performance export
* [ ] System tray mode
* [ ] Configurable settings screen
* [ ] Custom alert thresholds through the UI
* [ ] Additional performance charts
* [ ] Automatic report generation

---

## 🤝 Contributing

Contributions, ideas, bug reports, and improvements are welcome.

To contribute:

```bash
git clone https://github.com/YOUR_USERNAME/pc-performance-monitor.git
```

Create a new branch:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them, and submit a pull request.

---

## 📜 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Dhyey Patel**

Built as a practical project to explore:

* Python
* System programming concepts
* Hardware monitoring
* Desktop application development
* Data visualization
* Software architecture
* Automated testing

⭐ If you find this project interesting, consider giving it a star!
