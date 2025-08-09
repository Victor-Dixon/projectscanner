# GitHub Personal Access Token Guide

## 🔐 Why You Need a GitHub Token

The current scanner only captures **public repositories**. To scan your **private repositories**, you need a GitHub Personal Access Token.

## 📋 How to Create a GitHub Personal Access Token

### Step 1: Go to GitHub Settings
1. Log into your GitHub account
2. Click your profile picture → **Settings**
3. Scroll down to **Developer settings** (bottom left)
4. Click **Personal access tokens** → **Tokens (classic)**

### Step 2: Generate New Token
1. Click **Generate new token** → **Generate new token (classic)**
2. Give it a descriptive name like "project-scanner Library"
3. Set expiration (recommend 90 days for security)
4. Select scopes:
   - ✅ **repo** (Full control of private repositories)
   - ✅ **read:org** (Read organization data)
   - ✅ **read:user** (Read user data)

### Step 3: Copy the Token
1. Click **Generate token**
2. **Copy the token immediately** (you won't see it again!)
3. Store it securely

## 🚀 Using the Enhanced Scanner

### Command Line Usage
```bash
# Scan with private repository access
python github_library_scanner_private.py YOUR_USERNAME --token YOUR_TOKEN

# Example
python github_library_scanner_private.py dadudekc --token ghp_xxxxxxxxxxxxxxxxxxxx

# Scan with options
python github_library_scanner_private.py YOUR_USERNAME --token YOUR_TOKEN --max-repos 50 --force-rescan
```

### Security Best practice-projectss
1. **Never commit tokens to Git**
2. **Use environment variables**:
   ```bash
   export GITHUB_TOKEN=your_token_here
   python github_library_scanner_private.py YOUR_USERNAME --token $GITHUB_TOKEN
   ```
3. **Set token expiration** (90 days recommended)
4. **Use minimal required scopes**

## 🔍 What the Enhanced Scanner Captures

### Public vs Private Repository Detection
- ✅ **Public repositories**: All metadata and code analysis
- ✅ **Private repositories**: All metadata and code analysis
- 📊 **Separate tracking** of public vs private projects
- 🔒 **Privacy indicators** in the library

### Enhanced Features
- **Private repository cloning** with token authentication
- **Separate naming** for private repos (adds `_private` suffix)
- **Privacy-aware reporting** (shows public/private counts)
- **Enhanced security** with token-based authentication

## 📊 Expected Results

With a token, you'll see:
```
🔍 Fetching repositories for user: dadudekc
🔐 Using GitHub token for private repository access
📦 Found 45 repositories
  • Public repositories: 28
  • Private repositories: 17
```

## 🛠️ Troubleshooting

### Common Issues
1. **"Not Found" errors**: Check token permissions
2. **"Bad credentials"**: Token expired or invalid
3. **"Rate limit exceeded"**: Wait and retry
4. **"Repository not found"**: Token doesn't have access

### Token Permissions Required
- `repo` - Full control of private repositories
- `read:org` - Read organization data  
- `read:user` - Read user data

## 🔒 Security Notes

- **Tokens are sensitive**: Treat like passwords
- **Rotate regularly**: Generate new tokens every 90 days
- **Minimal scope**: Only grant necessary permissions
- **Environment variables**: Don't hardcode in scripts
- **Git ignore**: Add token files to .gitignore

## 📈 Benefits of Private Repository Scanning

1. **Complete portfolio analysis** including private work
2. **Full project diversity** understanding
3. **Comprehensive skill assessment** 
4. **Private project insights** for career development
5. **Complete codebase library** for AI training

## 🎯 Next Steps

1. **Create your GitHub token** following the steps above
2. **Run the enhanced scanner** with your token
3. **Compare results** with the public-only scan
4. **Analyze the differences** in your portfolio
5. **Use the complete library** for AI training and analysis

The enhanced scanner will give you a **complete picture** of your development portfolio, including all your private work and experiments! 