# Installation Guide - Python 3.11 Compatible

## Step-by-Step Setup

### Step 1: Navigate to Project Directory
```bash
cd ~/Desktop/ibrahim/Recomendation\ System\ For\ Elibrary
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```
You should see `(venv)` prefix in your terminal.

### Step 4: Upgrade pip
```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Verify Installation
```bash
python -c "import flask, pandas, sklearn, surprise; print('✓ All packages installed successfully!')"
```

## Run the Application

### Option 1: Web App (Main)
```bash


# Open browser: http://localhost:5000
```

### Option 2: Command Line Tools
```bash
python run_hybrid.py
python run_recommendation.py
python run_content.py
python generate_distinct_datasets.py
```

## Troubleshooting

### Issue: `source: command not found` (Windows)
**Solution:** Use this instead:
```bash
venv\Scripts\activate
```

### Issue: Permission denied on setup.sh
**Solution:** Make it executable:
```bash
chmod +x setup.sh
./setup.sh
```

### Issue: Module not found errors
**Solution:** Ensure venv is activated (should see `(venv)` prefix):
```bash
source venv/bin/activate
```

### Issue: Port 5000 already in use
**Solution:** Edit `app.py`, change the last line to:
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Use different port
```

## Python 3.11 Compatible Versions

The `requirements.txt` contains these versions tested for Python 3.11:
- Flask 3.1.3
- pandas 2.2.0
- numpy 1.26.4
- scikit-learn 1.5.0
- scikit-surprise 1.1.3
- scipy 1.13.1
