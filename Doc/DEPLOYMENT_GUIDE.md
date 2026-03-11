# 🚀 Deployment Guide - Get Your Live Demo URL

## Step-by-Step: Deploy to Streamlit Cloud (FREE)

### Prerequisites
- ✅ GitHub account
- ✅ Your code pushed to GitHub repository

---

## 📋 Step 1: Prepare Your Repository

Make sure your GitHub repo has these files in the root:

```
ai-formulary-intelligence/
├── app.py                    ✓ Must be in root
├── requirements.txt          ✓ Must be in root
├── README.md
└── [other files...]
```

**Important:** `app.py` and `requirements.txt` MUST be in the root folder!

---

## 🌐 Step 2: Deploy to Streamlit Cloud

### A. Go to Streamlit Cloud

1. Visit: **https://share.streamlit.io**

2. Click **"Sign in"** (top right)

3. Choose **"Continue with GitHub"**

4. Authorize Streamlit to access your GitHub

---

### B. Create New App

1. Click **"New app"** button

2. Fill in the deployment form:

   ```
   Repository: your-username/ai-formulary-intelligence
   Branch: main
   Main file path: app.py
   App URL (optional): choose a custom name
   ```

3. Click **"Deploy!"**

---

### C. Wait for Deployment

You'll see:
```
⏳ Deploying your app...
📦 Installing requirements...
🚀 Building app...
✅ Your app is live!
```

**Takes 2-3 minutes**

---

## 🎉 Step 3: Get Your URL

Once deployed, your app will be at:

```
https://YOUR-APP-NAME.streamlit.app
```

**Example URLs:**
- `https://formulary-intelligence.streamlit.app`
- `https://ai-formulary-demo.streamlit.app`
- `https://paryay-formulary-app.streamlit.app`

---

## 📝 Step 4: Update Your README

Add your live URL to the README.md:

```markdown
## 🌐 Live Demo

**Try it now:** https://your-actual-url.streamlit.app

Upload your formulary files and see instant analysis!
```

Commit and push:
```bash
git add README.md
git commit -m "Add live demo URL"
git push
```

---

## 🔧 Troubleshooting

### "App is not loading"
- Check that `app.py` is in the root of your repo
- Verify `requirements.txt` has all dependencies
- Check the app logs in Streamlit Cloud dashboard

### "Module not found" error
- Make sure `requirements.txt` lists all packages:
  ```
  streamlit==1.31.0
  pandas==2.2.0
  ```

### "File not found" error
- Ensure file paths in `app.py` are correct
- Make sure you're not referencing local files that aren't in the repo

---

## 🎯 Quick Checklist

Before deploying, verify:

- [ ] `app.py` is in root folder
- [ ] `requirements.txt` is in root folder  
- [ ] Both files are committed and pushed to GitHub
- [ ] Repository is public (or Streamlit Cloud has access)
- [ ] Code works locally (`streamlit run app.py`)

---

## 🔄 Updating Your Live App

After your app is deployed, any changes you push to GitHub will automatically redeploy!

```bash
# Make changes to app.py
git add app.py
git commit -m "Update analysis features"
git push

# Streamlit Cloud automatically redeploys in ~2 minutes
```

---

## 💡 Pro Tips

1. **Custom URL:** Choose a memorable app name during deployment
2. **Private Repos:** Work with Streamlit Cloud paid plans
3. **Secrets:** Use Streamlit secrets for API keys (don't commit them!)
4. **Analytics:** Check Streamlit Cloud dashboard for usage stats

---

## 📞 Need Help?

- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io

---

## 🎉 Once Deployed

Your app will be:
- ✅ Live 24/7
- ✅ Accessible worldwide
- ✅ Automatically updated when you push to GitHub
- ✅ Free to use and share

**Share your URL on LinkedIn, in your resume, with recruiters!**
