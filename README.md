# Unofficial FindMyDeviceServer Python Client

This is an unofficial Python package that allows you to interact with the [FindMyDeviceServer](https://gitlab.com/Nulide/findmydeviceserver) API. FindMyDeviceServer is a server designed to communicate with the FMD Android app, helping you locate and control your devices.

It's main use is currently a reimplementation of the crypto and authentication involved when communicating with the api. 

## ✨ Features and working commands

- Authenticate to the FindMyDeviceServer API.
- Send a "ring" to the server


## 📦 Installation

```sh
pip install findmydevice
```

## 🚀 Quick start

In this example, we create a reactor based on the data from this URL https://api.balkongas.de/metrics/6f1d3382-6b95-4adc-9d6f-6785ae0456f3/json/latest/


```python
from findmydevice import FMDClient
import logging 

logging.basicConfig(level=logging.DEBUG)
client = FMDClient('http://xyz.de', 'fmd_id', 'fmd_password')
client.authenticate()
client.ring()
```


## 🚀 Development

### 1️⃣ Setup a Local Development Environment

1. **Clone the repository**
   ```sh
   git clone https://github.com/kinkerl/findmydevice_python.git
   cd findmydevice_python
   ```
2. **Create a virtual environment**
   ```sh
   python -m venv .venv
   ```
3. **Activate the virtual environment**
   - **macOS/Linux:**
     ```sh
     source .venv/bin/activate
     ```
   - **Windows (CMD):**
     ```sh
     .venv\Scripts\activate
     ```
   - **Windows (PowerShell):**
     ```sh
     .venv\Scripts\Activate.ps1
     ```
4. **Install dependencies**
   ```sh
   pip install -e .[dev]
   ```

### 2️⃣ Running Tests
To run tests using `pytest`, use:
```sh
pytest
```

### 3️⃣ Building the Package
To build the package, run:
```sh
python -m build
```
This will generate a `dist/` directory with `.tar.gz` and `.whl` files.

### 4️⃣ Uploading to PyPI
1. **Ensure you have Twine installed**
   ```sh
   pip install twine
   ```
2. **Upload the package**
   ```sh
   twine upload dist/*
   ```
3. **Verify installation from PyPI**
   ```sh
   pip install findmydevice
   ```

