from contextlib import asynccontextmanager
import threading
from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import Alert, Reading, SessionLocal, init_db
from app.mqtt_service import run_sensor_simulator, start_mqtt, stop_mqtt
from app.planner import compare_algorithms

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@asynccontextmanager
async def lifespan(_app):
    init_db(); start_mqtt()
    worker = threading.Thread(target=run_sensor_simulator, daemon=True, name="sensor-simulator"); worker.start()
    yield
    stop_mqtt()

app = FastAPI(title="Smart Lab Monitoring & Autonomous Inspection", description="Simulated lab telemetry, threshold alerts, and robot path-planning prototype.", version="0.1.0", lifespan=lifespan)

@app.get("/health")
def health(): return {"status":"ok", "service":"smart-lab-api"}

@app.get("/api/readings")
def readings(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.query(Reading).order_by(Reading.id.desc()).limit(limit).all()
    return [{"id":x.id,"sensor_id":x.sensor_id,"temperature_c":x.temperature_c,"vibration":x.vibration,"equipment_status":x.equipment_status,"recorded_at":x.recorded_at.isoformat() if x.recorded_at else None} for x in rows]

@app.get("/api/alerts")
def alerts(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(Alert.id.desc()).limit(limit).all()
    return [{"id":x.id,"sensor_id":x.sensor_id,"severity":x.severity,"message":x.message,"temperature_c":x.temperature_c,"vibration":x.vibration,"created_at":x.created_at.isoformat() if x.created_at else None} for x in rows]

@app.get("/api/path/compare")
def path_compare(): return compare_algorithms()

@app.get("/", response_class=HTMLResponse)
def dashboard(): return HTML

HTML = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Smart Lab Monitor</title><style>body{max-width:1050px;margin:25px auto;padding:0 16px;background:#101827;color:#e8eef8;font:16px system-ui}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}.card{background:#19263a;border:1px solid #30415a;border-radius:12px;padding:16px;margin:12px 0}.muted{color:#9fb0c9}.value{font-size:2rem;font-weight:700}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px;border-bottom:1px solid #30415a}.alert{color:#ffbd8a}</style></head><body><h1>Smart Laboratory Monitor</h1><p class="muted">Simulated telemetry · threshold alerts · path-planning prototype</p><div class="grid"><div class="card"><div class="muted">Temperature</div><div id="temp" class="value">—</div>°C</div><div class="card"><div class="muted">Vibration</div><div id="vib" class="value">—</div></div><div class="card"><div class="muted">Recent readings</div><div id="count" class="value">—</div></div><div class="card"><div class="muted">Recent alerts</div><div id="acount" class="value">—</div></div></div><div class="card"><h2>Recent readings</h2><table><thead><tr><th>Sensor</th><th>Temperature</th><th>Vibration</th><th>Recorded</th></tr></thead><tbody id="rows"></tbody></table></div><div class="card"><h2>Anomaly alerts</h2><div id="alerts" class="muted">Loading…</div></div><div class="card"><h2>Path planning comparison</h2><div id="paths">Loading…</div><p class="muted"><a href="/api/path/compare">Raw algorithm results</a></p></div><p class="muted">All data is simulated; this is not a certified safety system.</p><script>const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));async function refresh(){try{const [r,a,p]=await Promise.all([fetch('/api/readings?limit=12').then(x=>x.json()),fetch('/api/alerts?limit=12').then(x=>x.json()),fetch('/api/path/compare').then(x=>x.json())]);const x=r[0];document.getElementById('temp').textContent=x?x.temperature_c.toFixed(1):'—';document.getElementById('vib').textContent=x?x.vibration.toFixed(3):'—';document.getElementById('count').textContent=r.length;document.getElementById('acount').textContent=a.length;document.getElementById('rows').innerHTML=r.map(x=>`<tr><td>${esc(x.sensor_id)}</td><td>${x.temperature_c.toFixed(1)}</td><td>${x.vibration.toFixed(3)}</td><td>${esc(x.recorded_at)}</td></tr>`).join('')||'<tr><td colspan="4">Waiting for telemetry…</td></tr>';document.getElementById('alerts').innerHTML=a.map(x=>`<p class="alert"><b>${esc(x.sensor_id)}</b> — ${esc(x.message)}</p>`).join('')||'No recent alerts';document.getElementById('paths').innerHTML='<table><tr><th>Algorithm</th><th>Path length</th><th>Nodes explored</th><th>Time (ms)</th></tr>'+Object.entries(p.results).map(([n,x])=>`<tr><td>${esc(n)}</td><td>${x.path_length}</td><td>${x.nodes_explored}</td><td>${x.execution_time_ms}</td></tr>`).join('')+'</table>'}catch(e){console.error(e)}}refresh();setInterval(refresh,3000)</script></body></html>'''
