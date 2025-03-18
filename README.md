# OpenCreditServer
---

### Build & Run:
```bash
docker build -t open_credit_server:latest .
docker run --name open_credit_server --rm -d -p5000:8000 open_credit_server:latest

# For log watching
docker logs -f open_credit_server
```


### How to run for local dev:
#### Windows - cmd:
```powershell
python3 -m venv venv
./venv/bin/activate.bat
pip3 install -r requirements.txt
python3 run.py
```

#### Windows - PowerShell:
```powershell
python3 -m venv venv
./venv/bin/activate.ps1
pip3 install -r requirements.txt
python3 run.py
```

#### Linux / Mac:
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 run.py
```