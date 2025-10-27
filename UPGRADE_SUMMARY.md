# Chainlit & LangGraph Upgrade - Quick Reference

**Version:** 0.3.1 → 0.4.0
**Date:** 2025-10-27

---

## TL;DR

### What's Changing?
- **Chainlit:** 1.3.1 → 2.8.3 (MAJOR upgrade, breaking changes)
- **LangGraph:** 0.2.45 → 1.0.1 (MINOR upgrade, backward compatible)

### Timeline
**3-5 days** (26-33 hours)

### Risk Level
🟠 **MEDIUM-HIGH** (mainly due to Chainlit config changes)

### Code Changes Required
✅ **MINIMAL** - Mostly configuration file updates

---

## Quick Start

### 1. Backup Everything
```bash
# Run these commands before starting
poetry export -f requirements.txt -o requirements-backup.txt --without-hashes
cp .chainlit/config.toml .chainlit/config.toml.backup
cp pyproject.toml pyproject.toml.backup
docker exec postgres pg_dump -U postgres postgres > backup-$(date +%Y%m%d).sql
```

### 2. Update Dependencies
```bash
# Edit pyproject.toml
chainlit = "^2.8.3"    # Change from "1.3.1"
langgraph = "^1.0.1"   # Change from "^0.2.31"

# Install
poetry lock
poetry install
```

### 3. Update Configuration
Edit `.chainlit/config.toml` and **DELETE** these sections:
- Lines 41-53: `[features.audio]`
- Lines 90-119: `[UI.theme]`
- Line 19: `follow_symlink` (if uncommented)
- Line 80: `custom_font` (if uncommented)

Update:
```toml
[meta]
generated_by = "2.8.3"  # Change from "1.2.0"
```

### 4. Test
```bash
poetry run chainlit run app.py
# Open http://localhost:8000
# Test login, send messages, upload files
```

### 5. Commit & Push
```bash
git add -A
git commit -m "feat: upgrade to Chainlit 2.8.3 and LangGraph 1.0.1"
git push -u origin claude/upgrade-chainlit-langraph-011CUXSzH8vJY23G3tyoznkW
```

---

## Critical Changes

### ⚠️ Configuration File Breaking Changes

**MUST DELETE from `.chainlit/config.toml`:**

1. **Audio section (Lines 41-53):**
   ```toml
   # ❌ DELETE THIS ENTIRE SECTION
   [features.audio]
       min_decibels = -45
       # ... rest of audio config
   ```
   Why? Audio API completely reworked in Chainlit 2.0

2. **Theme section (Lines 90-119):**
   ```toml
   # ❌ DELETE THIS ENTIRE SECTION
   [UI.theme]
       default = "dark"
   [UI.theme.light]
       # ...
   [UI.theme.dark]
       # ...
   ```
   Why? Theme config moved to separate `theme.json` file

3. **Deprecated fields:**
   ```toml
   # ❌ DELETE OR ENSURE COMMENTED
   # follow_symlink = false
   # custom_font = "..."
   ```

### ✅ Code Changes

**Good news:** Almost NO code changes needed!

- ✅ Your imports work as-is
- ✅ Your `StateGraph` usage unchanged
- ✅ Your decorators work as-is
- ✅ Your authentication callbacks work
- ✅ Your streaming works
- ✅ Your database models work

**Only if you use:** (you don't)
- `langgraph.prebuilt.create_react_agent` → Change to `langchain.agents.create_react_agent`

---

## What You Get

### Chainlit 2.8.3 Benefits
- 🔒 **Better Security:** Cookie-based auth, CVE fixes
- 🎨 **New UI:** Complete rewrite with Shadcn/Tailwind
- ⚡ **Better Performance:** Optimized frontend
- 🎯 **Custom Elements:** New feature for custom UI
- 🛡️ **More Stable:** Community-maintained with formal agreement

### LangGraph 1.0.1 Benefits
- ✅ **Production Ready:** v1.0 milestone reached
- 🚀 **New Features:** Node caching, deferred nodes, commands
- 🔄 **Backward Compatible:** Your code works as-is
- 📈 **Better Performance:** Optimizations under the hood
- 🏢 **Battle Tested:** Used by Uber, LinkedIn, Klarna

---

## Testing Checklist

### Must Test
- [ ] App starts without errors
- [ ] Login works (username: admin, password: admin)
- [ ] Can select all 5 workflows
- [ ] Can send message and get response
- [ ] Streaming works (see tokens appear)
- [ ] Chat history persists (refresh page)
- [ ] Settings changes work
- [ ] File upload works (Resume Optimizer)
- [ ] Image upload works (Multimodal Chat)

### Should Test
- [ ] All unit tests pass: `poetry run pytest -v`
- [ ] Dark/light theme toggle
- [ ] Tool calls work (datetime, web search)
- [ ] No errors in browser console
- [ ] No errors in server logs

---

## Rollback Plan

If something goes wrong:

```bash
# Quick rollback (restore everything)
cp .chainlit/config.toml.backup .chainlit/config.toml
cp pyproject.toml.backup pyproject.toml
poetry install
docker exec -i postgres psql -U postgres postgres < backup-*.sql
docker compose restart
```

---

## Timeline

| Phase | Duration | What |
|-------|----------|------|
| 0. Prep | 2-3h | Backups, testing current system |
| 1. Dependencies | 3-4h | Update packages |
| 2. Config | 2-3h | Update config.toml |
| 3. Code | 4-6h | Verify imports, test |
| 4. Database | 2h | Check migrations |
| 5. Testing | 8h | Full integration testing |
| 6. Docker | 3-4h | Update containers |
| 7. Docs | 2-3h | Update README, CHANGELOG |
| **Total** | **26-33h** | **3-5 days** |

---

## Common Issues & Solutions

### Issue: "Unknown config field" error on startup
**Solution:** Remove deprecated fields from `.chainlit/config.toml`

### Issue: Login not working
**Solution:**
- Check `CHAINLIT_AUTH_SECRET` is set in `.env`
- Clear browser cookies
- Try incognito/private mode

### Issue: Workflows not appearing
**Solution:**
- Check logs for "Chat profiles created: X"
- Verify `discover_workflows()` runs
- Check for import errors

### Issue: "Module not found" errors
**Solution:**
- Run `poetry install` again
- Check `poetry.lock` was updated
- Restart Python process

### Issue: Tests failing
**Solution:**
- Update test fixtures for new versions
- Check pytest-asyncio compatibility
- Review test output for specific errors

---

## Need Help?

### Documentation
- **Full Migration Plan:** [MIGRATION_PLAN.md](MIGRATION_PLAN.md) (this file has EVERYTHING)
- **Chainlit Docs:** https://docs.chainlit.io/guides/migration/2.0.0
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/

### Community
- **Chainlit GitHub:** https://github.com/Chainlit/chainlit/issues
- **Chainlit Discord:** https://discord.gg/chainlit
- **LangChain Discord:** https://discord.gg/langchain

---

## Decision Matrix

### Should I upgrade now?

**YES, if:**
- ✅ You want latest security fixes
- ✅ You want better UI/UX
- ✅ You want access to new features
- ✅ You have 3-5 days for upgrade + testing
- ✅ You can schedule maintenance window

**WAIT, if:**
- ❌ You have critical production deadlines
- ❌ You can't test thoroughly
- ❌ You don't have database backups
- ❌ You rely on deprecated features

---

## Pre-Flight Checklist

Before starting the upgrade:

- [ ] Read full migration plan ([MIGRATION_PLAN.md](MIGRATION_PLAN.md))
- [ ] Database backup created and verified
- [ ] Config files backed up
- [ ] Current system tested and working
- [ ] Stakeholders informed
- [ ] Maintenance window scheduled
- [ ] Rollback plan understood
- [ ] Testing checklist ready
- [ ] 3-5 days allocated for work

---

## After Upgrade

### Immediate (Day 1)
- [ ] Monitor logs for errors
- [ ] Test all workflows
- [ ] User acceptance testing
- [ ] Performance check

### Short-term (Week 1)
- [ ] Monitor production usage
- [ ] Collect user feedback
- [ ] Fix any issues found
- [ ] Optimize based on metrics

### Long-term (Month 1-3)
- [ ] Explore new Chainlit 2.0 features
- [ ] Implement LangGraph 1.0 optimizations
- [ ] Consider Python 3.11+ upgrade
- [ ] Document lessons learned

---

## Quick Commands Reference

```bash
# Backup
poetry export -f requirements.txt -o backup.txt --without-hashes
docker exec postgres pg_dump -U postgres postgres > backup.sql

# Upgrade
poetry lock
poetry install

# Test
poetry run pytest -v
poetry run chainlit run app.py

# Rollback
cp config.toml.backup config.toml
poetry install
docker exec -i postgres psql -U postgres postgres < backup.sql

# Check versions
poetry show chainlit langgraph
python -c "import chainlit; print(chainlit.__version__)"
python -c "import langgraph; print(langgraph.__version__)"
```

---

**Ready to upgrade?** Follow the detailed plan in [MIGRATION_PLAN.md](MIGRATION_PLAN.md)

**Questions?** Check the FAQ section or reach out to the community.

**Last Updated:** 2025-10-27
