# GitHub Push Instructions

## Issue: Workflow Permission Required

The push failed because GitHub requires the `workflow` scope for Personal Access Tokens when pushing repositories that contain `.github/workflows` files.

## Solutions

### Option 1: Update GitHub Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Or visit: https://github.com/settings/tokens

2. Either:
   - **Create a new token** with `workflow` scope, OR
   - **Edit your existing token** and add the `workflow` scope

3. Required scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)

4. Update your Git credentials:
   ```bash
   # If using credential helper, you may need to update stored credentials
   git config --global credential.helper osxkeychain
   # Then try pushing again - it will prompt for the new token
   ```

5. Try pushing again:
   ```bash
   git push github main
   ```

### Option 2: Use SSH Instead of HTTPS

1. Set up SSH key on GitHub (if not already done):
   - Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
   - Add to GitHub: https://github.com/settings/keys

2. Change remote URL to SSH:
   ```bash
   git remote set-url github git@github.com:Sabuanchuparayil/saleor.git
   ```

3. Push using SSH:
   ```bash
   git push github main
   ```

### Option 3: Push via GitHub CLI (Alternative)

1. Install GitHub CLI: `brew install gh`

2. Authenticate: `gh auth login`

3. Push the changes:
   ```bash
   git push github main
   ```

## Current Status

✅ Commit created successfully: `98301af68b - Add Railway deployment configuration`
- Files committed:
  - `railway.toml`
  - `Procfile`
  - `RAILWAY_SETUP.md`

⏸️ Push pending - waiting for authentication with `workflow` scope

## Quick Fix (Choose One)

**Fastest:** Update your GitHub token to include `workflow` scope, then:
```bash
cd /Users/apple/Desktop/saleor
git push github main
```

**Alternative:** Switch to SSH:
```bash
cd /Users/apple/Desktop/saleor
git remote set-url github git@github.com:Sabuanchuparayil/saleor.git
git push github main
```

