#!/bin/bash

# Activate venv if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Install with pre-built wheels
pip install --upgrade pip wheel setuptools
pip install --only-binary :all: pandas==2.2.0 || pip install pandas==2.2.0 --no-build-isolation

# Install other requirements one by one
pip install Flask==3.1.3
pip install numpy==1.26.4
pip install scikit-learn==1.5.0
pip install scikit-surprise==1.1.3
pip install scipy==1.13.1
pip install Werkzeug==3.1.8
pip install python-dateutil==2.8.2
pip install joblib==1.4.0
pip install pymongo==4.6.0
pip install python-dotenv==1.0.0
pip install bcrypt==4.1.1

echo "✓ All packages installed!"
