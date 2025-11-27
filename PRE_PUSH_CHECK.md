# Pre-Push Security Check

## Quick Verification Before Pushing to GitHub

Run these commands to verify no sensitive data is being committed:

### 1. Check What Will Be Committed

```bash
git status
```

### 2. Review Staged Files

```bash
git diff --cached
```

### 3. Verify Sensitive Files Are Ignored

```bash
# Check if .env files are ignored
git check-ignore backend/.env frontend/.env

# Check if local.properties is ignored
git check-ignore frontend/android/local.properties

# Check if log files are ignored
git check-ignore logs/*.log backend/logs/*.log
```

### 4. Search for Potential Secrets

```bash
# Search for hardcoded IPs (should only find examples/placeholders)
git grep -E "172\.16\.|192\.168\.|10\.0\.2\.2" -- "*.dart" "*.py"

# Search for potential passwords (should find none)
git grep -i "password.*=" -- "*.dart" "*.py" | grep -v "DB_PASSWORD" | grep -v "example" | grep -v "your_"

# Search for API keys (should find none)
git grep -i "api.*key" -- "*.dart" "*.py" | grep -v "example"
```

### 5. Verify .gitignore is Working

```bash
git status --ignored | grep -E "\.env|local\.properties|\.log|build/"
```

## ✅ Safe to Push If:

- ✅ No `.env` files appear in `git status`
- ✅ `local.properties` is ignored
- ✅ No log files are tracked
- ✅ `api_service.dart` has placeholder URL (`10.0.2.2` or `YOUR_COMPUTER_IP`)
- ✅ No hardcoded passwords or API keys
- ✅ `backend/.env.example` exists (template only)

## ❌ DO NOT Push If:

- ❌ `.env` files are tracked
- ❌ `local.properties` is tracked
- ❌ Log files contain sensitive data
- ❌ Hardcoded IP addresses (except `10.0.2.2` for emulator)
- ❌ Hardcoded passwords or API keys
- ❌ Database files (`.db`, `.sqlite`)

## Quick Fix Commands

If you find sensitive data:

```bash
# Remove from staging
git reset HEAD <file>

# Remove from git but keep locally
git rm --cached <file>

# Add to .gitignore
echo "<file>" >> .gitignore
```

## Final Check

Before pushing, run:

```bash
# See what will be pushed
git log origin/main..HEAD --oneline

# Review all changes
git diff origin/main..HEAD
```

---

**Remember**: Once pushed to GitHub, sensitive data becomes public. Always verify before pushing!

