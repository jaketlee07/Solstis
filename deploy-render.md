# 🚀 Deploy to Render (Free Full-Stack)

## Quick Setup

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub

### 2. Deploy Both Services
- Click "New +" → "Blueprint"
- Connect your GitHub repository
- Render will automatically detect the `render.yaml` file
- Click "Apply"

### 3. Set Environment Variables
In the Render dashboard, set:
- `OPENAI_API_KEY` = your OpenAI API key

### 4. Your URLs
- **Frontend**: `https://solstis-frontend.onrender.com`
- **Backend**: `https://solstis-api.onrender.com`

## Manual Setup (Alternative)

### Backend Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Set:
   - **Name**: `solstis-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r api/requirements.txt`
   - **Start Command**: `cd api && gunicorn app:app`
4. Add environment variable: `OPENAI_API_KEY`

### Frontend Service
1. Click "New +" → "Static Site"
2. Connect your GitHub repo
3. Set:
   - **Name**: `solstis-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
4. Add environment variable: `REACT_APP_API_URL` = your backend URL

## Benefits
✅ **Completely Free** - 750 hours/month
✅ **Automatic HTTPS** - Both services
✅ **Global CDN** - Fast loading worldwide
✅ **Auto Deploy** - Updates on every push
✅ **Custom Domains** - Add your own domain later
✅ **SSL Certificates** - Included automatically

## Monitoring
- Check deployment logs in Render dashboard
- Monitor usage in the free tier limits
- Set up notifications for deployments 