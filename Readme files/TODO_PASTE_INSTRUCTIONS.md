# TODO: Where to paste code / content (Mengo-Hub)
This TODO file maps each requested change from your text file to the exact files/locations to edit, and includes ready-to-paste snippets or commands. Follow items in order and mark them done as you go.

---
## 1) Add "About MSS" section to every user's dashboard
- Purpose: show Mengo Senior School info to all roles.
- Files to edit (frontend):
  - public/index.html (student dashboard) or templates/dashboard.html
  - public/admin.html (admin dashboard)
  - public/teacher.html (teacher dashboard)
- Backend: ensure route provides about text: flask_app.py or premium_routes.py

Paste snippet (HTML) into each dashboard content area (replace placeholder):

```html
<section id="about-mss" class="card">
  <h2>About Mengo Senior School</h2>
  <p><strong>Founded:</strong> 1895 — Uganda's oldest secondary school.</p>
  <p><strong>Core values:</strong> Fearing God; Respect for persons & property; Integrity.</p>
  <p><strong>Mission:</strong> To provide quality, holistic education that prepares students for service in church, state, and society.</p>
  <p><a href="https://mengoss.sc.ug" target="_blank">mengoss.sc.ug</a></p>
</section>
```
Recommended backend change (paste in flask_app.py near dashboard route):

```py
# ensure 'about_mss' is injected into dashboard templates
@app.context_processor
def inject_site_info():
    about = {
        'title': 'Mengo Senior School',
        'founded': 1895,
        'mission': 'To provide quality, holistic education...',
        'url': 'https://mengoss.sc.ug'
    }
    return dict(about_mss=about)
```

Or store in DB (system_settings table):

```sql
INSERT INTO system_settings(setting_key, setting_value) VALUES ('about_mss', '{"title":"Mengo Senior School","founded":1895,...}');
```

--- 9999
## 2) Role-based dashboards (Headteacher, Deputies, Deans)
- Files/actions:
  - templates/admin_headteacher.html (create)
  - templates/admin_deputy.html (create)
  - backend: routes in premium_routes.py or add new blueprint admin_routes.py
- Paste: create partial templates that reuse the about_mss section and show role-specific widgets.

Example route (paste into premium_routes.py or flask_app.py):

```py
@app.route('/admin/role/<role>')
@require_admin_token
def admin_role_dashboard(role):
    # load role metrics
    metrics = get_role_metrics(role)
    return render_template('admin_role.html', role=role, metrics=metrics)
```

--- 999
## 3) Upload teacher notes (Word/PDF/TXT) and store metadata
- Files:
  - public/uploads/notes/ (create folder)
  - premium_routes.py: add POST /api/admin/notes/upload
  - premium_features.py or services/notes_service.py: handle saving and DB record
- DB: add notes table or reuse documents table (schema.sql)

Paste snippet (route) into premium_routes.py:

```py
@app.route('/api/admin/notes/upload', methods=['POST'])
@require_admin_token
def upload_notes():
    f = request.files['file']
    subject = request.form.get('subject')
    level = request.form.get('level')
    filename = secure_filename(f.filename)
    path = os.path.join('public', 'uploads', 'notes', filename)
    f.save(path)
    # insert metadata into DB
    db = get_db(); db.execute('INSERT INTO notes(...) VALUES(...)')
    return jsonify(success=True, url='/uploads/notes/'+filename)
```

---
## 4) Audio features (overlays, playlists, waveforms)
- Files:
  - premium_routes.py: audio endpoints already exist (/api/premium/audio/...)
  - public/audio_player.js (create) — paste player code
  - public/audio/beats/ (storage)
  - admin UI: public/admin.html add "Audio Presets" panel
- Paste HTML for audio player into student dashboard where you want player rendered.
- For waveform visualization, paste WaveSurfer.js integration into public/js/audio_player.js

Example audio player placeholder (paste in dashboard):
```html
<div id="audio-study">
  <div id="player"></div>
  <button onclick="generateBeat(10,30)">Generate 10Hz 30min</button>
</div>
<script src="/audio_player.js"></script>
```

--- 999
## 5) Badges & Certificates admin UI
- Files:
  - admin_controls_guide.md (docs) — already added
  - premium_features.py: add badge logic
  - premium_routes.py: add endpoints /api/admin/badges
  - public/admin.html: add Badges manager UI
Paste badge JSON example into API seed or admin UI copy area.

---
## 6) Storage audit (limit 1 GB)
- Files:
  - utilities/storage_audit.py (create)
  - admin route: /api/admin/storage/audit in premium_routes.py
- Paste audit function (scan public/uploads and summarize) into utilities/storage_audit.py

Example snippet:

```py
def storage_audit(root='public/uploads'):
    total = 0; files=[]
    for dirpath,_,fnames in os.walk(root):
        for f in fnames:
            p=os.path.join(dirpath,f); s=os.path.getsize(p); total+=s; files.append((p,s))
    return {'total_bytes': total, 'largest': sorted(files, key=lambda x:x[1], reverse=True)[:10]}
```

--- 999
## 7) Paper setting & upload of elements (Word files)
- Files:
  - public/admin_papers.html (UI)
  - premium_routes.py: POST /api/admin/papers/set
  - public/uploads/papers/elements/ (store Word templates)
Paste the paper format JSON example into admin UI "Create Paper" form and use it to call the API.

--- 999
## 8) Chat (group & individual) + toggle
- Files:
  - websocket_ai.py (already has namespace /ai). Add chat events.
  - public/js/chat.js (create) for frontend
  - admin toggle stored in system_settings table (feature flag)
Paste new socket handlers into websocket_ai.py (on 'chat_message' event) and in public/js/chat.js implement UI.

---
## 9) Local AI models integration (you already have models in models/)
- Files to edit:
  - .env: set GPTALL_MODEL_PATH=models
  - ai_service.py: ensure load_local_model uses GPTALL_MODEL_PATH and LOCAL_MODEL name
Paste into ai_service.py near local model loader:

```py
from gpt4all import GPT4All
MODEL_PATH = os.getenv('GPTALL_MODEL_PATH','models')
LOCAL_MODEL = os.getenv('LOCAL_MODEL','Llama-3.2-3B-Instruct-Q4_0.gguf')

def load_local():
    return GPT4All(LOCAL_MODEL, model_path=MODEL_PATH)
```

--- 999
## 10) Multi-AI fallback & scheduling
- Files:
  - ai_service.py: implement routing logic and rate-limit checks
  - config: .env entries for providers
- Paste TASK_ROUTING and RATE_LIMITS dictionary into ai_service.py; implement choose_provider() function.

--- 999
## 11) OCR / Text scanner
- Files:
  - premium_routes.py: POST /api/premium/ocr
  - utilities/ocr_service.py (create) — use pytesseract or easyocr
- Paste OCR wrapper into utilities/ocr_service.py

Example:
```py
import pytesseract
from PIL import Image

def ocr_image(path):
    img=Image.open(path); text=pytesseract.image_to_string(img)
    return text
```

---
## 12) N8N integration (you have docs)
- Files:
  - n8n_workflows/run_mengo_task.py (create)
  - public/demos/n8n_sample.json (create demo)
- Paste the Python call example into that file and test via N8N HTTP request.

---
## 13) Password generator integration
- Files:
  - password_generator.py (exists)
  - admin route: /api/admin/passwords/generate & /api/admin/passwords/view
- Paste secure generation route into premium_routes.py or admin_routes.py; ensure only super admin with certificate can call /view.

---
## 14) PostgreSQL migration (switch from SQLite)
- Files to edit:
  - flask_app.py: replace get_db() to connect to Postgres
  - schema.sql: run on Postgres
  - populate_db.py: adapt to psycopg2

Paste the connection snippet into flask_app.py as shown in COMPREHENSIVE_REQUIREMENTS.md.

---
## 15) scikit-learn vs sklearn
- Action: Use `scikit-learn` package; imports in code remain `import sklearn.`
- Files to update: requirements.txt (done). Search code for any `import sklearn` — leave as-is. If you used package name `sklearn` anywhere else, no change needed.

---
## 16) License & footer on every page
- Files:
  - LICENSE.md (create)
  - templates/base.html or public/footer.html — add footer code

Paste footer HTML to base template as shown in COMPREHENSIVE_REQUIREMENTS.md.

---
## 17) Demo content
- Files:
  - public/demos/3d/animal_cell.glb (add sample)
  - public/demos/audio/sample_10hz.wav
  - public/demos/papers/sample_math.docx
  - public/demos/n8n_sample.json
Place sample files in those folders and update demo links in README and admin demo panel.

---
## Quick priority checklist (mark when done)
- [ ] Add About MSS HTML to dashboards (index.html, admin.html, teacher.html)
- [ ] Inject about_mss via context_processor or DB entry
- [ ] Create role-based admin dashboards (headteacher, deputies)
- [ ] Upload notes API + UI
- [ ] Audio UI + waveform + overlays
- [ ] Badges & certificates admin panel
- [ ] Storage audit + 1GB enforcement alerts
- [ ] Paper setting UI + upload elements
- [ ] Group & individual chat + admin toggle
- [ ] Local AI model loader (use your models in models/)
- [ ] Multi-AI fallback & scheduling implementation
- [ ] OCR endpoint and service
- [ ] N8N workflow script + demo
- [ ] Integrate password generator (super admin only view)
- [ ] Create LICENSE.md and footer
- [ ] Migrate to PostgreSQL (when ready)

---
If you want, I can create template files for each UI and paste-ready code for each route. Tell me which top 3 items you want implemented first and I will generate the code/PR for them.

