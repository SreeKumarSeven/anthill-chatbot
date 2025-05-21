#!/bin/bash
# Prepare Anthill IQ Chatbot for Vercel deployment
# This script helps prepare the project for deployment on Vercel

echo "Preparing Anthill IQ Chatbot for Vercel deployment..."

# Run tests to ensure everything imports correctly
echo "Running import tests..."
python test_vercel.py

if [ $? -ne 0 ]; then
    echo "Tests failed! Please fix the issues before deploying."
    exit 1
fi

# Clean up unnecessary files
echo "Cleaning up unnecessary files..."

# Remove unnecessary directories to reduce package size
if [ -d "api/backend_for_vercel/__pycache__" ]; then
    rm -rf api/backend_for_vercel/__pycache__
fi

if [ -d "api/__pycache__" ]; then
    rm -rf api/__pycache__
fi

if [ -d "__pycache__" ]; then
    rm -rf __pycache__
fi

# Verify requirements.txt exists in api folder
if [ ! -f "api/requirements.txt" ]; then
    echo "ERROR: api/requirements.txt not found"
    exit 1
fi

# Verify key files exist
echo "Verifying key files..."
files_to_check=("api/index.py" "api/simple_db.py" "api/service_account_handler.py" "vercel.json" ".vercelignore")

for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: $file not found!"
        exit 1
    fi
done

echo "Verification complete! Project is ready for Vercel deployment."
echo ""
echo "Next steps:"
echo "1. Commit and push changes to GitHub"
echo "2. Import project in Vercel"
echo "3. Set environment variables (OPENAI_API_KEY, DATABASE_URL)"
echo "4. Deploy"
echo ""
echo "See VERCEL-DEPLOY-GUIDE.md for detailed instructions." 