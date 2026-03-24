#!/bin/bash
# LibraryDSA — One-command setup
# Run: bash setup.sh

echo ""
echo "  LibraryDSA — KNU Central Library"
echo "  COE 363 Data Structures Project"
echo "  ─────────────────────────────────"
echo ""

# 1. Virtual environment
echo "→ Creating virtual environment..."
python -m venv venv

# 2. Activate
source venv/bin/activate || venv\Scripts\activate.bat 2>/dev/null

# 3. Install Django
echo "→ Installing Django..."
pip install django --quiet

# 4. Migrate
echo "→ Running migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations books
python manage.py migrate

# 5. Seed data
echo "→ Seeding sample data..."
python manage.py seed

echo ""
echo "  ✓ Ready! Run the server with:"
echo ""
echo "    source venv/bin/activate"
echo "    python manage.py runserver"
echo ""
echo "  Then open: http://127.0.0.1:8000"
echo ""
echo "  Demo logins:"
echo "    librarian / admin1234   (Library Admin)"
echo "    kwame     / student1234 (Student)"
echo ""
