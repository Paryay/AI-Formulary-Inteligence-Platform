# 🤖 AI Formulary Intelligence Platform

Intelligent formulary change detection and analysis system for healthcare organizations.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B)](https://your-app.streamlit.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌐 Live Demo

**🔗 [Try it now →](https://your-app.streamlit.app)**

Upload your own formulary files and see instant analysis. No installation required!

*(Deploy your app first, then replace the URL above with your actual Streamlit URL)*

---

## ⚡ Quick Start

### Option 1: Interactive Web Demo (Easiest)

Visit the live demo above - upload files and analyze instantly!

### Option 2: Run Locally

```bash
# Clone repository
git clone https://github.com/your-username/ai-formulary-intelligence.git
cd ai-formulary-intelligence

# Install dependencies
pip install -r requirements.txt

# Launch Streamlit app
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### Option 3: Command-Line Tools

```bash
# Analyze single carrier
python src/formulary_delta_processor.py february.csv \
    --carrier "CarrierName" \
    --keys RXCUI

# Batch process multiple carriers
python src/batch_processor.py data/

# Generate SQL for database loading
python src/generate_sql.py \
    --carrier UHC \
    --timestamp 20240215_103045 \
    --keys RXCUI
```

---

## 📊 Features

### Interactive Web App
- ✅ Upload and compare formulary files
- ✅ Automatic change detection (added/deleted/modified)
- ✅ Support for multiple file formats (pipe, CSV, TSV)
- ✅ Real-time analysis (processes 500K+ records in seconds)
- ✅ Export results as CSV
- ✅ Download summary reports

### Command-Line Tools
- ✅ Batch processing for multiple carriers
- ✅ Historical tracking and archiving
- ✅ SQL script generation for database loads
- ✅ Detailed change categorization
- ✅ AI-powered insights (optional with Claude API)

### Change Detection Types
- Formulary additions and deletions
- Tier changes (1→2, 2→3, etc.)
- Prior Authorization (PA) updates
- Step Therapy (ST) requirements
- Quantity Limit (QL) modifications
- Copay/coinsurance changes
- Specialty designation updates

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Interactive Web Interface          │
│         (Streamlit App)                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Analysis Engine (Python)           │
│  • Multi-format parser                  │
│  • Delta detection                      │
│  • Change categorization                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Output & Integration Layer           │
│  • CSV exports                          │
│  • SQL generation                       │
│  • Summary reports                      │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
ai-formulary-intelligence/
│
├── app.py                    # Streamlit web application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── src/                      # Core analysis modules
│   ├── ai_formulary_analyzer.py
│   ├── formulary_delta_processor.py
│   ├── claude_api_integration.py
│   ├── batch_processor.py
│   └── generate_sql.py
│
├── web/                      # Alternative web interface
│   └── index.html
│
├── docs/                     # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   └── ARCHITECTURE.md
│
└── examples/                 # Sample data
    └── sample_output/
```

---

## 🎯 Use Cases

**Pharmacy Operations**
- Identify drugs requiring new prior authorization
- Track quantity limit changes
- Monitor formulary additions/deletions

**Clinical Teams**
- Detect therapeutic substitutions
- Review specialty designation changes
- Assess patient impact of restrictions

**Finance Teams**
- Calculate cost impact of tier changes
- Estimate copay shift to members
- Project administrative burden

**IT/Data Teams**
- Generate SQL for incremental database updates
- Export change data for downstream systems
- Automate monthly processing workflows

---

## 💻 Tech Stack

- **Python 3.8+** - Core language
- **Streamlit** - Interactive web interface
- **Pandas** - Data processing and analysis
- **Claude AI** - Intelligent insights (optional)

---

## 📈 Performance

- Processes 500,000+ records in ~30 seconds
- Handles files up to 100MB+
- Tested with CMS PUF formulary data (57MB files)
- Efficient delta detection using set operations

---

## 🚀 Deployment

### Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Click "Deploy"

Your app will be live at: `https://your-app.streamlit.app`

**[Full deployment guide →](docs/DEPLOYMENT_GUIDE.md)**

---

## 📖 Documentation

- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Step-by-step deployment to Streamlit Cloud
- [Architecture Overview](docs/ARCHITECTURE.md) - Technical design details
- [User Guide](docs/USER_GUIDE.md) - How to use the platform
- [API Reference](docs/API_REFERENCE.md) - Integration documentation

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---



**

**Built to solve real healthcare data challenges. Questions? Open an issue!**
