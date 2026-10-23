# 🚀 DEPLOYMENT_GUIDE.md — DisasterShield AI Fire TV Edition
### Step-by-Step Production Deployment on Render

This guide provides beginner-friendly, exact steps to deploy **DisasterShield AI (Fire TV Edition)** on [Render](https://render.com) using your new GitHub repository:
**`https://github.com/Adarshyadav24-cyber/DisasterShield-AI-FireTV.git`**

---

## 📌 Architecture Overview

DisasterShield AI is packaged as a **single unified Python Web Service**:
- **Backend:** Flask REST server ([firetv_server.py](file:///c:/Users/ay351/OneDrive/Desktop/DisasterShield%20AI/DisasterShield-AI/firetv_server.py)) running via `gunicorn`.
- **Frontend:** 10-foot Fire TV application ([firetv/index.html](file:///c:/Users/ay351/OneDrive/Desktop/DisasterShield%20AI/DisasterShield-AI/firetv/index.html)), CSS design system, and 2D spatial D-pad engine served at the root `/`.
- **Health Check:** `/api/health` endpoint responding with `HTTP 200`.
- **Zero Localhost Hardcoding:** All client API calls use relative paths (`/api/status`, `/api/ask`, `/api/sector`), eliminating CORS issues and ensuring it works on any domain.

---

## 🛠️ Step 1: Push Code to your New GitHub Repository

In Windows PowerShell:

```powershell
# Navigate to the repository
cd "C:\Users\ay351\OneDrive\Desktop\DisasterShield AI\DisasterShield-AI"

# Add the new GitHub remote (or update origin)
git remote add firetv-origin https://github.com/Adarshyadav24-cyber/DisasterShield-AI-FireTV.git

# Push the firetv-dev branch directly to main on your new repo
git push firetv-origin firetv-dev:main
```

---

## 🌐 Step 2: Create the Web Service on Render

### Option A: Using the Render Dashboard (Manual Setup)

1. Log in to [Render.com](https://dashboard.render.com/) (Sign in with GitHub).
2. Click **New +** in the top navigation and select **Web Service**.
3. Under **Connect a repository**, find and select:
   **`Adarshyadav24-cyber/DisasterShield-AI-FireTV`**
4. Configure the service settings:
   - **Name:** `disastershield-ai-firetv` (or your choice)
   - **Region:** `Oregon (US West)` or closest to your location
   - **Branch:** `main`
   - **Root Directory:** *(leave blank / default)*
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn firetv_server:app --bind 0.0.0.0:$PORT`
   - **Instance Type:** `Free`
5. Click **Advanced** and set **Health Check Path**:
   - `/api/health`
6. Click **Create Web Service**.

### Option B: Using Render Blueprint (Automatic Setup)
Render automatically detects the included `render.yaml` file:
1. In Render Dashboard, click **New +** -> **Blueprint**.
2. Connect `Adarshyadav24-cyber/DisasterShield-AI-FireTV`.
3. Render automatically reads `render.yaml` and provisions the Web Service with the correct build and start commands.

---

## ⚙️ Step 3: Configure Environment Variables on Render

In your Render service dashboard under **Environment**:

| Key | Default Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.9` | Ensures Python 3.11 runtime |
| `ENABLE_LIVE_WEATHER` | `true` | Enables Open-Meteo public weather telemetry |
| `DEFAULT_LOCATION_NAME` | `Prayagraj, Uttar Pradesh` | Default command sector coordinates |
| `GEMMA_ENDPOINT_URL` | `http://localhost:11434` | Optional local Ollama server |
| `GEMMA_MODEL_NAME` | `gemma4:e2b` | Model name (falls back to Safe Demo Mode if offline) |
| `ADMIN_VERIFY_PIN` | `1122` | PIN for administrator verification desk |

> **Note on AI Inference:** On Render's free tier, no local Ollama instance is running. DisasterShield AI's resilient architecture automatically and transparently operates in **Safe Demo Mode**, displaying verified NDMA deterministic guidance explicitly labeled as `DEMO MODE (RULE-BASED)`.

---

## 🔍 Step 4: Verify Deployment and Check Health

1. In Render, watch the **Events** and **Logs** tab.
2. When the build completes, Render displays:
   `==> Your service is live at https://disastershield-ai-firetv.onrender.com`
3. Test the health check endpoint:
   Open `https://<YOUR_RENDER_URL>/api/health` in your browser. It should return:
   ```json
   {
     "app": "DisasterShield AI",
     "platform": "Amazon Fire TV / Fire OS Compatible",
     "status": "HEALTHY",
     "tagline": "Early Awareness. Verified Information. Safer Decisions."
   }
   ```
4. Open `https://<YOUR_RENDER_URL>/` to view the full 10-foot Fire TV interface.

---

## 📺 Step 5: Test on Fire TV / Simulator

### A. Testing on Physical Amazon Fire TV Stick
1. Turn on your Fire TV Stick.
2. Open the **Amazon Silk Browser** (search "Silk Browser" in Fire TV search if not installed).
3. Type your live Render URL:
   `https://<YOUR_RENDER_URL>/`
4. Use the **Fire TV Remote Control D-pad** (Up, Down, Left, Right, Select/OK, Back) to navigate all 8 screens!

### B. Testing in Desktop Browser with Fire TV Remote Simulator
1. Open `https://<YOUR_RENDER_URL>/` on your computer.
2. Press `F11` to enter 1080p fullscreen mode.
3. Use your **Arrow Keys** (D-Pad), **Enter** (Select), and **Backspace** (Back).
4. Alternatively, use the on-screen **Virtual Fire TV Remote Controller** (bottom-right; press `R` to toggle).
