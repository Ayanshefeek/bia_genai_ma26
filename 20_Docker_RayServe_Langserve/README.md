# Trainer Follow-Along – Deployment & Cost Control

## Suggested Demo Flow (60 mins)
| Time | Activity | Script / Tool |
|------|-----------|----------------|
| 0–15m | Docker Multi-stage build | app/docker_app/Dockerfile |
| 15–30m | Ray Serve Autoscaling | rayserve_app.py |
| 30–45m | LangServe Adapter | langserve_app.py |
| 45–60m | Budget Alerts | budget_alert.py / Notebook 02 |

---

### 1️⃣ Docker Multi-stage
Run in terminal:
```bash
cd app/docker_app
docker build -t agentops-demo .
docker run --rm agentops-demo
```
Explain build stages and resulting image size.

### 2️⃣ Ray Serve Autoscaling
```bash
python app/rayserve_app.py
```
Then visit: `http://127.0.0.1:8000/ask` using curl or Postman.

### 3️⃣ LangServe Adapter
```bash
python app/langserve_app.py
```
Visit Swagger UI at `http://127.0.0.1:8000/docs`.

### 4️⃣ Budget Alerts
```bash
python app/budget_alert.py
```
Discuss cost logging and alert thresholds.

### 5️⃣ Visualization
Open notebook `02_budget_visualization.ipynb` and show graphs.


Use where python or pip to get the python3.12 path
C:/Users/DELL/AppData/Local/Programs/Python/Python313/python.exe E:\BIA\Cost_Deployment\app\langser_client.py
