# Chainlit & LangGraph Upgrade Checklist

**Version:** 0.3.1 → 0.4.0
**Target:** Chainlit 2.8.3, LangGraph 1.0.1
**Date Started:** __________
**Completed:** __________

---

## Pre-Upgrade

### Planning
- [ ] Read UPGRADE_SUMMARY.md
- [ ] Read MIGRATION_PLAN.md
- [ ] Stakeholders informed
- [ ] Maintenance window scheduled: __________
- [ ] Team roles assigned

### Backups
- [ ] Export dependencies: `poetry export -f requirements.txt -o backup.txt`
- [ ] Backup config: `cp .chainlit/config.toml .chainlit/config.toml.backup`
- [ ] Backup pyproject: `cp pyproject.toml pyproject.toml.backup`
- [ ] Backup database: `docker exec postgres pg_dump > backup.sql`
- [ ] Verify backups exist and are not empty
- [ ] Test current system works

### Preparation
- [ ] Create rollback script
- [ ] Document current behavior
- [ ] Take UI screenshots
- [ ] Run and document current test results

---

## Phase 1: Dependencies (3-4 hours)

### LangGraph Upgrade
- [ ] Edit pyproject.toml: `langgraph = "^1.0.1"`
- [ ] Run: `poetry lock --no-update`
- [ ] Run: `poetry install`
- [ ] Verify: `poetry show langgraph` shows 1.0.1
- [ ] Test imports work
- [ ] Test graph compilation
- [ ] Run unit tests

### Chainlit Upgrade
- [ ] Edit pyproject.toml: `chainlit = "^2.8.3"`
- [ ] Run: `poetry lock`
- [ ] Run: `poetry install`
- [ ] Verify: `poetry show chainlit` shows 2.8.3
- [ ] Test imports work

### LangChain Updates
- [ ] Update langchain-openai: `"^0.3.0"`
- [ ] Update langchain-anthropic: `"^0.3.0"`
- [ ] Run: `poetry lock && poetry install`
- [ ] Test LLM factory loads

### Verification
- [ ] Run: `poetry check`
- [ ] Export new requirements: `poetry export > requirements-new.txt`
- [ ] No dependency conflicts

**Issues Encountered:**
_____________________________________________
_____________________________________________

---

## Phase 2: Configuration (2-3 hours)

### Backup
- [ ] Create: `.chainlit/config.toml.pre-migration`

### Remove Deprecated Sections
- [ ] Delete `[features.audio]` section (lines 41-53)
- [ ] Delete `[UI.theme]` section (lines 90-119)
- [ ] Delete/comment `follow_symlink` (line 19)
- [ ] Delete/comment `custom_font` (line 80)

### Update Metadata
- [ ] Update `[meta] generated_by = "2.8.3"`

### Keep These Sections
- [ ] `[project]` - unchanged
- [ ] `[features]` - unchanged
- [ ] `[features.spontaneous_file_upload]` - unchanged
- [ ] `[UI]` - basic settings only

### Optional: Theme File
- [ ] Create `.chainlit/theme.json` (if custom theme needed)
- [ ] Validate JSON syntax

### Test Configuration
- [ ] Start app: `poetry run chainlit run app.py --port 8001`
- [ ] Check for config errors in logs
- [ ] App starts successfully
- [ ] Open http://localhost:8001 in browser

**Issues Encountered:**
_____________________________________________
_____________________________________________

---

## Phase 3: Code Migration (4-6 hours)

### Verify Imports
- [ ] Search for `langgraph.prebuilt`: `grep -r "langgraph.prebuilt"`
- [ ] No matches found (or updated if found)
- [ ] Test all imports: `python -c "import app"`

### Test Components
- [ ] Storage client imports correctly
- [ ] All workflow classes load
- [ ] LLM factory works
- [ ] State serializer works

### Verify Patterns
- [ ] Session access patterns work
- [ ] Auth callbacks unchanged
- [ ] Streaming patterns work
- [ ] Tool routing works

### Run All Tests
- [ ] `poetry run pytest -v`
- [ ] All tests pass
- [ ] Review any warnings

**Issues Encountered:**
_____________________________________________
_____________________________________________

---

## Phase 4: Database (2 hours)

### Check Schema
- [ ] Start postgres: `docker compose up -d postgres`
- [ ] List tables: `docker exec postgres psql -c "\dt"`
- [ ] Check alembic: `poetry run alembic current`

### Migrations
- [ ] Generate if needed: `alembic revision --autogenerate`
- [ ] Review migration file
- [ ] Run: `alembic upgrade head`

### Validate
- [ ] Check langgraphs table: `\d langgraphs`
- [ ] Test state serialization roundtrip
- [ ] Query existing data intact

**Issues Encountered:**
_____________________________________________
_____________________________________________

---

## Phase 5: Testing (8 hours)

### Unit Tests
- [ ] Run full suite: `pytest -v`
- [ ] Test LLM module
- [ ] Test workflows
- [ ] All tests pass

### Application Startup
- [ ] Start all services: `docker compose up`
- [ ] No errors in logs
- [ ] "Chat profiles created: 4" appears
- [ ] UI loads at http://localhost:8000

### Authentication
- [ ] Login with admin/admin works
- [ ] Session persists across refresh
- [ ] Cookie set correctly
- [ ] Logout works (if available)

### Workflow Discovery
- [ ] Chat profile selector shows 4 workflows:
  - [ ] Simple Chat
  - [ ] Multimodal Chat
  - [ ] Resume Optimizer
  - [ ] Lean Canvas Chat

### Simple Chat Workflow
- [ ] Select "Simple Chat"
- [ ] Settings panel appears
- [ ] Send message: "What's 2+2?"
- [ ] Streaming response works
- [ ] AI responds correctly
- [ ] No errors in logs

### Tool Calling
- [ ] Send: "What time is it?"
- [ ] Datetime tool executes
- [ ] AI responds with time
- [ ] Send: "Search for AI news" (if TAVILY_API_KEY)
- [ ] Search tool executes
- [ ] Results displayed

### Settings
- [ ] Change model in settings
- [ ] Send new message
- [ ] New model used
- [ ] Settings persist

### State Persistence
- [ ] Send 3-4 messages
- [ ] Refresh page
- [ ] Chat history restored
- [ ] Can continue conversation
- [ ] Close/reopen tab
- [ ] Thread restored from database

### File Upload
- [ ] Select "Resume Optimizer"
- [ ] Upload PDF file
- [ ] File processes successfully
- [ ] AI provides analysis
- [ ] File visible in MinIO: `docker exec minio mc ls`

### Multimodal
- [ ] Select "Multimodal Chat"
- [ ] Upload image (PNG/JPG)
- [ ] Add text: "What's in this image?"
- [ ] Image displayed in chat
- [ ] AI describes image

### UI Elements
- [ ] Chat input works
- [ ] Send button works
- [ ] File upload button works
- [ ] Settings panel opens/closes
- [ ] Profile selector works
- [ ] Dark/light theme toggle
- [ ] Responsive on mobile size
- [ ] No visual glitches

### Error Handling
- [ ] Test with missing API key (error handled)
- [ ] Stop MinIO, try upload (error handled)
- [ ] Network interruption (graceful handling)

### Performance
- [ ] Response time < 2s (first token)
- [ ] Streaming smooth
- [ ] Memory usage reasonable: `docker stats`

**Issues Encountered:**
_____________________________________________
_____________________________________________
_____________________________________________
_____________________________________________

---

## Phase 6: Docker (3-4 hours)

### Dockerfile Updates (Optional)
- [ ] Consider Python 3.11 upgrade
- [ ] Add curl for healthcheck
- [ ] Add HEALTHCHECK directive
- [ ] Build test: `docker compose build --no-cache`

### Docker Compose Updates
- [ ] Add healthchecks to services
- [ ] Add depends_on with conditions
- [ ] Test: `docker compose down && docker compose up`

### Production Checklist
- [ ] All env vars set in .env
- [ ] Secrets not hardcoded
- [ ] Volumes configured
- [ ] Backup strategy documented
- [ ] Healthchecks working: `docker compose ps`

**Issues Encountered:**
_____________________________________________
_____________________________________________

---

## Phase 7: Documentation (2-3 hours)

### README.md
- [ ] Update version badge to 0.4.0
- [ ] Update Chainlit badge to 2.8.3
- [ ] Update LangGraph badge to 1.0.1
- [ ] Add migration notes section
- [ ] Update requirements (Python 3.10+)

### CHANGELOG.md
- [ ] Add [0.4.0] entry
- [ ] Document breaking changes
- [ ] Document additions
- [ ] Document security fixes
- [ ] Add migration guide link

### Version Files
- [ ] Update chat_workflow/version.py to 0.4.0
- [ ] Update pyproject.toml version to 0.4.0
- [ ] Commit version bump

### Configuration Docs
- [ ] Create/update .chainlit/README.md
- [ ] Document new config structure
- [ ] Document theme.json usage

**Issues Encountered:**
_____________________________________________
_____________________________________________

---

## Final Validation

### Smoke Tests
- [ ] Fresh docker compose up
- [ ] Login works
- [ ] Send message in each workflow
- [ ] Upload file works
- [ ] Settings work
- [ ] No errors in logs

### Performance Check
- [ ] Response time acceptable
- [ ] Memory usage normal
- [ ] No memory leaks
- [ ] Streaming smooth

### Security Check
- [ ] CHAINLIT_AUTH_SECRET set
- [ ] Cookies have httpOnly flag
- [ ] No secrets in logs
- [ ] API keys not exposed

---

## Commit & Push

### Git Operations
- [ ] Stage changes: `git add -A`
- [ ] Review changes: `git status`
- [ ] Commit: `git commit -m "feat: upgrade to Chainlit 2.8.3 and LangGraph 1.0.1"`
- [ ] Push: `git push -u origin claude/upgrade-chainlit-langraph-011CUXSzH8vJY23G3tyoznkW`

### Verification
- [ ] Push successful
- [ ] CI/CD pipeline passes (if configured)
- [ ] Branch visible on GitHub

---

## Post-Upgrade

### Immediate (Day 1)
- [ ] Monitor logs for 24 hours
- [ ] User acceptance testing
- [ ] Performance benchmarking
- [ ] Security audit

### Short-term (Week 1)
- [ ] Monitor production metrics
- [ ] Collect user feedback
- [ ] Address any issues
- [ ] Document lessons learned

### Long-term (Month 1-3)
- [ ] Explore new features
- [ ] Optimize based on usage
- [ ] Plan next improvements

---

## Rollback Executed?

- [ ] Yes, rollback was necessary
- [ ] No, upgrade successful

### If Rollback:
- Reason: _____________________________________________
- Time to rollback: _____________________________________________
- Issues encountered: _____________________________________________
- Lessons learned: _____________________________________________

---

## Sign-off

**Upgrade completed by:** _____________________
**Date:** _____________________
**Duration:** _____ hours (estimated 26-33h)
**Issues:** _____ critical, _____ minor
**Status:** ☐ Success ☐ Partial ☐ Rollback

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________
_____________________________________________

---

## Quick Reference

### Emergency Rollback
```bash
./rollback.sh
```

### Restart Services
```bash
docker compose down
docker compose up -d
```

### Check Versions
```bash
poetry show chainlit langgraph
```

### View Logs
```bash
docker compose logs -f chainlit
```

### Database Backup
```bash
docker exec postgres pg_dump -U postgres postgres > emergency-backup.sql
```

---

**Keep this checklist for your records!**
