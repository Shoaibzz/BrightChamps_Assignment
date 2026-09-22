BrightChamps Demo Recovery AI Prototype
What this is
A working Python/Streamlit prototype for the BrightChamps FDA take-home case.

The proposed intervention is:

Scheduled demo -> no-show -> AI-assisted recovery message -> existing rep queue -> reschedule -> measure recovery

Files
app.py — Streamlit application
BrightChamps_FDA_Case_Dataset.csv — case dataset
requirements.txt — Python dependencies
Run locally
pip install -r requirements.txt
streamlit run app.py
The CSV can either be placed next to app.py or uploaded from the sidebar.

Optional AI setup
The prototype works without an API key using a safe fallback message.

To enable Gemini:

Windows PowerShell
$env:GEMINI_API_KEY="YOUR_KEY"
streamlit run app.py
macOS/Linux
export GEMINI_API_KEY="YOUR_KEY"
streamlit run app.py
The AI uses Gemini 2.5 Flash to generate a concise recovery message from the anonymised lead attributes.

AI guardrails
The prompt explicitly prevents the model from inventing:

parent/child names
reasons for the no-show
prices
discounts
availability
internal scoring
The model only generates the communication; the business logic and measurement remain transparent Python logic.

Why this fits the case
The build demonstrates:

Funnel analysis
Leak quantification
Operational recovery queue
AI-assisted message generation
Rep handoff
Experiment measurement
Revenue sensitivity
The priority score is intentionally transparent and is not presented as a trained ML model. A production version could later learn recovery propensity from historical intervention outcomes.

<img width="1859" height="895" alt="image" src="https://github.com/user-attachments/assets/c66a82de-ec9d-4273-a201-2ceb92dc9d73" />

