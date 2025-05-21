# Anthill IQ Chatbot Vercel Deployment Guide

This guide explains how to deploy the optimized Anthill IQ chatbot to Vercel.

## Prerequisites

- A Vercel account
- Git installed on your machine
- Railway PostgreSQL database (already set up)

## Deployment Steps

### 1. Push to GitHub

Make sure your code is pushed to a GitHub repository. Vercel will use this repository for deployment.

### 2. Import Project in Vercel

1. Log in to your Vercel account
2. Click "Add New" → "Project"
3. Select your GitHub repository with the Anthill IQ chatbot code
4. Configure the project:
   - Framework Preset: `Other`
   - Root Directory: (keep as default)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

### 3. Set Environment Variables

In the Vercel project settings, add these environment variables:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://postgres:uEutQJRqyRbgOlzwhsGGgczYXaeBqgxI@yamabiko.proxy.rlwy.net:14599/railway
```

Replace with your actual values if they differ.

### 4. Deploy

Click "Deploy" and wait for the deployment to complete.

## What's Optimized

To overcome the Vercel 250MB deployment size limit, the following optimizations were made:

1. **Minimal Dependencies**: Using only essential packages:
   - openai
   - python-dotenv
   - requests
   - psycopg2-binary

2. **File Exclusions**:
   - We've configured `.vercelignore` and `vercel.json` to exclude unnecessary files
   - `api/backend_for_vercel/` and other large directories are excluded
   - Frontend assets are excluded where possible

3. **Simplified Database**: 
   - Using direct psycopg2 connections instead of SQLAlchemy
   - Minimal table structures
   - Reduced error logging

4. **Base Functionality Only**:
   - The API provides just the essential chatbot and user registration functions
   - Removed all optional features not needed for core functionality

## Troubleshooting

### Size Issues

If deployment still exceeds the 250MB limit:

1. Run `vercel --debug` locally to see what files are being included
2. Add more patterns to `.vercelignore` if needed
3. Further remove unused Python imports
4. Try using the `excludeFiles` option in `vercel.json` to exclude large files

### Database Connection Issues

If the database connection fails:

1. Verify the DATABASE_URL environment variable is correct
2. Check if Railway database is accessible from Vercel's IP range
3. Try increasing the connection timeout in `simple_db.py`

## Testing

Before deploying, you can validate the setup by running the test script:

```
python test_vercel.py
```

All modules should import successfully. 