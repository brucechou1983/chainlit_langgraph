# Chainlit & LangGraph Upgrade Migration Plan

**Project:** chainlit_langgraph
**Current Version:** 0.3.1
**Target Version:** 0.4.0
**Date Created:** 2025-10-27
**Prepared By:** Claude Code

---

## Executive Summary

### Version Upgrades

| Package | Current | Target | Impact |
|---------|---------|--------|--------|
| **Chainlit** | 1.3.1 | 2.8.3 | 🔴 HIGH - Major breaking changes |
| **LangGraph** | 0.2.45 | 1.0.1 | 🟢 LOW - Backward compatible |
| **LangChain** | 0.3.7 | 0.3.x | 🟢 LOW - Keep current |
| **Python** | 3.10 | 3.10+ | ✅ Compatible |

### Key Metrics

- **Estimated Effort:** 3-5 days (26-33 hours)
- **Risk Level:** Medium-High
- **Code Changes Required:** Minimal (mostly configuration)
- **Data Migration Required:** No (schema compatible)
- **Rollback Difficulty:** Low (git revert + backup restore)

### Critical Success Factors

1. ✅ Configuration file cleanup (`.chainlit/config.toml`)
2. ✅ Comprehensive testing of all 5 workflows
3. ✅ Database backup before upgrade
4. ✅ Authentication flow validation
5. ✅ State persistence verification

---

## Current System Analysis

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Chainlit Application                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Auth      │  │  Workflows   │  │   LLM Factory    │   │
│  │  (Password/ │  │  (5 custom)  │  │  (6 providers)   │   │
│  │   OAuth)    │  └──────────────┘  └──────────────────┘   │
│  └─────────────┘                                             │
│         │                    │                    │           │
│         └────────────────────┴────────────────────┘           │
│                              │                                │
│                      LangGraph Engine                         │
│                    (StateGraph + Tools)                       │
└─────────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
   ┌─────▼──────┐       ┌─────▼──────┐      ┌──────▼──────┐
   │ PostgreSQL │       │   MinIO    │      │  LLM APIs   │
   │  (State &  │       │  (Files)   │      │ (Multiple)  │
   │   Threads) │       └────────────┘      └─────────────┘
   └────────────┘
```

### Dependency Tree

```
chainlit-langgraph (0.3.1)
├── chainlit==1.3.1 ❌ NEEDS UPGRADE
│   ├── sqlalchemy==2.0.36 ✅
│   └── asyncpg==0.29.0 ✅
├── langgraph==0.2.45 ⚠️ NEEDS UPGRADE
│   ├── langgraph-checkpoint==2.0.2 ✅
│   └── langchain-core==0.3.15 ✅
├── langchain==0.3.7 ✅
├── langchain-anthropic==0.2.4 ⚠️ MINOR UPDATE
├── langchain-openai==0.2.5 ⚠️ MINOR UPDATE
├── langchain-google-genai==2.0.4 ✅
├── langchain-google-vertexai==2.0.7 ✅
├── langchain-groq==0.2.1 ✅
├── langchain-ollama==0.2.0 ✅
├── boto3==1.35.41 ✅
├── alembic==1.13.3 ✅
├── psycopg2-binary==2.9.9 ✅
└── pypdf==5.0.1 ✅
```

### Critical Usage Patterns

**Chainlit Decorators (app.py):**
- `@cl.on_chat_start` (Line 164) - Workflow initialization
- `@cl.on_message` (Line 197) - Message handling with streaming
- `@cl.on_chat_end` (Line 52) - State persistence
- `@cl.on_chat_resume` (Line 86) - Session restoration
- `@cl.on_settings_update` (Line 183) - Settings management
- `@cl.set_chat_profiles` (Line 155) - Workflow selection
- `@cl.password_auth_callback` (Line 143) - Authentication
- `@maybe_oauth_callback` (Line 132) - OAuth integration

**LangGraph Patterns (chat_workflow/workflows/):**
- `StateGraph` with custom state classes
- `graph.compile()` for runnable creation
- `graph.astream_events(state, version="v1")` for streaming
- Custom node implementations with tool routing
- Message history management with `operator.add`

**Custom Integrations:**
- Multi-provider LLM factory (6 providers)
- Dynamic workflow discovery system
- State serialization for LangChain messages
- MinIO S3-compatible storage
- SQLAlchemy data layer with custom tables

---

## Breaking Changes Analysis

### Chainlit 1.3.1 → 2.8.3

#### 🔴 CRITICAL: Configuration File Changes

**Location:** `.chainlit/config.toml`

**Changes Required:**

1. **Remove deprecated fields:**
   ```toml
   # ❌ DELETE THESE LINES
   follow_symlink = false  # Line 19 (commented)
   custom_font = "..."     # Line 80 (commented)
   ```

2. **Remove `[features.audio]` section (Lines 41-53):**
   ```toml
   # ❌ DELETE THIS ENTIRE SECTION
   [features.audio]
       min_decibels = -45
       initial_silence_timeout = 3000
       silence_timeout = 1500
       max_duration = 15000
       chunk_duration = 1000
       sample_rate = 44100
   ```
   **Reason:** Audio API completely reworked. Use new callbacks if needed:
   - `@cl.on_audio_start`
   - `@cl.on_audio_chunk`
   - `@cl.on_audio_end`

3. **Remove `[UI.theme]` section (Lines 90-119):**
   ```toml
   # ❌ DELETE THIS ENTIRE SECTION
   [UI.theme]
       default = "dark"
   [UI.theme.light]
       ...
   [UI.theme.dark]
       ...
   ```
   **Reason:** Theme customization moved to separate `theme.json` file.

4. **Update metadata:**
   ```toml
   [meta]
   generated_by = "2.8.3"  # Change from "1.2.0"
   ```

**Impact Assessment:**
- **Risk:** High (app may fail to start)
- **Effort:** 30 minutes
- **Testing:** Immediate validation required
- **Rollback:** Restore from `.chainlit/config.toml.backup`

#### 🟠 HIGH: Authentication Changes

**What Changed:**
- Backend now uses **cookie-based authentication** instead of direct JWT
- More secure (httpOnly cookies, CSRF protection)
- No code changes required for basic password auth

**Your Code Status:**
```python
# app.py:143-152 - Password Auth
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # ✅ This will work as-is
    return cl.User(...)

# app.py:132-140 - OAuth
@maybe_oauth_callback
def oauth_callback(provider_id, token, raw_user_data, default_user):
    # ✅ This will work as-is
    return default_user
```

**Testing Required:**
- [ ] Login with password (admin/admin)
- [ ] OAuth flow (if configured)
- [ ] Session persistence across page reloads
- [ ] Logout functionality
- [ ] Cookie security headers present

#### 🟠 MEDIUM: Actions API Changes

**Only applies if using `cl.Action`**

**Status:** ✅ **NOT USED** in your codebase

**Reference for future:**
```python
# OLD (1.3.1):
cl.Action(name="...", value="string", description="...")

# NEW (2.8.3):
cl.Action(
    name="...",
    payload={"key": "value"},  # Now accepts dict
    tooltip="...",             # Renamed from description
    icon="MessageSquare"       # NEW: Lucide icons
)
```

#### 🟡 MEDIUM: Session Object Changes

**What Changed:**
```python
# OLD (1.3.1):
cl.context.session.http_referer   # ❌ Removed
cl.context.session.http_cookie    # ❌ Removed
cl.context.session.languages      # ❌ Removed

# NEW (2.8.3):
cl.context.session.environ        # ✅ Contains all HTTP headers
```

**Your Code Status:**
```python
# app.py:59, 166, 173, 179
thread_id = cl.context.session.thread_id        # ✅ Still works
chat_profile = cl.context.session.chat_profile  # ✅ Still works
```

**Impact:** ✅ **NONE** - You only access `thread_id` and `chat_profile`

#### 🟡 LOW: UI Rewrite (Shadcn/Tailwind)

**What Changed:**
- Complete frontend rewrite with Shadcn/Tailwind
- New custom element feature
- Better theme customization
- Cleaner codebase

**Impact on Your App:**
- Visual appearance may have minor differences
- Custom CSS may need adjustments (if used)
- Better performance and UX

**Testing Required:**
- [ ] All UI elements render correctly
- [ ] Chat input/output working
- [ ] File upload UI functional
- [ ] Settings panel displays properly
- [ ] Dark/light theme switching
- [ ] Mobile responsiveness

#### 🟢 LOW: Security Updates

**Required Updates:**
- FastAPI >= 0.115.3 (CVE-2024-47874 fix)
- Starlette >= 0.41.2
- Python 3.8 support dropped (you're on 3.10 ✅)

**Impact:** Automatic via dependency resolution

---

### LangGraph 0.2.45 → 1.0.1

#### ✅ EXCELLENT NEWS: Backward Compatible!

**Official Statement:**
> "LangGraph 1.0 maintains full backward compatibility with 0.6.6+. No breaking changes until 2.0."

**Your Code Status:**

```python
# chat_workflow/workflows/base.py
from langgraph.graph import StateGraph, END  # ✅ Still works

class BaseState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], operator.add]  # ✅ Still works
    chat_profile: str

class BaseWorkflow(ABC):
    def create_graph(self) -> StateGraph:  # ✅ Still works
        graph = StateGraph(MyState)
        graph.add_node("chat", self.chat_node)
        graph.add_edge("chat", END)
        return graph

# app.py:213
graph.astream_events(state, version="v1", stream_mode="values")  # ✅ Still works
```

**Impact:** ✅ **ZERO CODE CHANGES REQUIRED**

#### ⚠️ DEPRECATED: langgraph.prebuilt

**What Changed:**
```python
# ❌ DEPRECATED (still works but will be removed in 2.0):
from langgraph.prebuilt import create_react_agent

# ✅ NEW LOCATION:
from langchain.agents import create_react_agent
```

**Your Code Status:**
```bash
$ grep -r "langgraph.prebuilt" chat_workflow/
# No matches found ✅
```

**Impact:** ✅ **NONE** - You don't use prebuilt agents

#### 🆕 NEW FEATURES (Optional)

**Available in LangGraph 1.0:**

1. **Node Caching** - Skip redundant computations
   ```python
   graph.add_node("expensive_node", compute_heavy_fn, cache=True)
   ```

2. **Deferred Nodes** - Delay execution until all upstream paths complete
   ```python
   graph.add_node("summarize", summarize_fn, deferred=True)
   ```

3. **Command API** - Dynamic, edgeless agent flows
   ```python
   from langgraph.types import Command
   # More flexible than traditional edges
   ```

4. **Tool State Updates** - Tools can directly modify graph state
   ```python
   def tool_with_state_update(state):
       # Tool can return state modifications
       return {"result": "...", "state_update": {...}}
   ```

5. **Supervisor Library** - Hierarchical multi-agent systems
   ```python
   from langgraph.supervisor import create_supervisor
   ```

**Recommendation:** Explore these features in Phase 8 (post-upgrade optimization)

---

## Phase-by-Phase Execution Plan

### PHASE 0: Preparation & Backup
**Duration:** 2-3 hours
**Risk:** Low
**Blocking:** None

#### Checklist

- [ ] **0.1 Verify Current State**
  ```bash
  cd /home/user/chainlit_langgraph
  git status
  git log --oneline -5
  docker ps
  ```

- [ ] **0.2 Export Dependencies**
  ```bash
  poetry export -f requirements.txt -o requirements-backup-v0.3.1.txt --without-hashes
  poetry show > poetry-show-backup-v0.3.1.txt
  ```

- [ ] **0.3 Backup Configuration**
  ```bash
  cp .chainlit/config.toml .chainlit/config.toml.backup
  cp pyproject.toml pyproject.toml.backup
  cp poetry.lock poetry.lock.backup
  ```

- [ ] **0.4 Database Backup**
  ```bash
  # Start database if not running
  docker compose up -d postgres

  # Create backup
  docker exec postgres pg_dump -U postgres postgres > backup-pre-upgrade-$(date +%Y%m%d).sql

  # Verify backup
  ls -lh backup-pre-upgrade-*.sql
  ```

- [ ] **0.5 Test Current System**
  ```bash
  # Run existing tests
  poetry run pytest -v

  # Start application
  docker compose up -d
  curl http://localhost:8000

  # Take screenshots of UI
  # Document current behavior
  ```

- [ ] **0.6 Create Rollback Script**
  ```bash
  cat > rollback.sh << 'EOF'
  #!/bin/bash
  echo "🔄 Rolling back to v0.3.1..."

  # Restore config files
  cp .chainlit/config.toml.backup .chainlit/config.toml
  cp pyproject.toml.backup pyproject.toml
  cp poetry.lock.backup poetry.lock

  # Restore dependencies
  poetry install

  # Restore database
  docker exec -i postgres psql -U postgres postgres < backup-pre-upgrade-*.sql

  echo "✅ Rollback complete!"
  EOF
  chmod +x rollback.sh
  ```

---

### PHASE 1: Dependency Upgrades
**Duration:** 3-4 hours
**Risk:** Medium
**Blocking:** Phase 0

#### Step 1.1: Update LangGraph (Lower Risk First)

- [ ] **Update pyproject.toml:**
  ```toml
  [tool.poetry.dependencies]
  langgraph = "^1.0.1"  # Was: "^0.2.31"
  ```

- [ ] **Lock and install:**
  ```bash
  poetry lock --no-update
  poetry install
  ```

- [ ] **Verify installation:**
  ```bash
  poetry show langgraph
  # Should show 1.0.1
  ```

- [ ] **Test import:**
  ```bash
  poetry run python -c "
  from langgraph.graph import StateGraph, END
  from langgraph import __version__
  print(f'✅ LangGraph {__version__} imported successfully')
  "
  ```

- [ ] **Test workflow compilation:**
  ```bash
  poetry run python -c "
  from chat_workflow.workflows.simple_chat import SimpleChatWorkflow
  workflow = SimpleChatWorkflow()
  graph = workflow.create_graph()
  compiled = graph.compile()
  print('✅ Graph compiles successfully')
  "
  ```

- [ ] **Run tests:**
  ```bash
  poetry run pytest chat_workflow/tests/test_simple_chat.py -v
  ```

**Expected Result:** ✅ All tests pass (backward compatible)

#### Step 1.2: Update Chainlit (Higher Risk)

- [ ] **Update pyproject.toml:**
  ```toml
  [tool.poetry.dependencies]
  chainlit = "^2.8.3"  # Was: "1.3.1"
  ```

- [ ] **Lock and install:**
  ```bash
  poetry lock
  poetry install
  ```

- [ ] **Verify installation:**
  ```bash
  poetry show chainlit
  # Should show 2.8.3
  ```

- [ ] **Test import:**
  ```bash
  poetry run python -c "
  import chainlit as cl
  from chainlit import __version__
  print(f'✅ Chainlit {__version__} imported successfully')
  "
  ```

**Expected Result:** ✅ May show deprecation warnings about config (normal)

#### Step 1.3: Update LangChain Packages

- [ ] **Update pyproject.toml:**
  ```toml
  [tool.poetry.dependencies]
  langchain-openai = "^0.3.0"      # Was: "^0.2.1"
  langchain-anthropic = "^0.3.0"   # Was: "^0.2.1"
  # Others remain the same
  ```

- [ ] **Lock and install:**
  ```bash
  poetry lock
  poetry install
  ```

- [ ] **Test LLM factory:**
  ```bash
  poetry run python -c "
  from chat_workflow.llm.factory import llm_factory
  from chat_workflow.llm.providers.openai import OpenAIProvider
  print('✅ LLM providers loaded successfully')
  print(f'Registered providers: {list(llm_factory._providers.keys())}')
  "
  ```

#### Step 1.4: Verify All Dependencies

- [ ] **Check dependency tree:**
  ```bash
  poetry show --tree | grep -E "(chainlit|langgraph|langchain)"
  ```

- [ ] **Check for conflicts:**
  ```bash
  poetry check
  ```

- [ ] **Export new lockfile:**
  ```bash
  poetry export -f requirements.txt -o requirements-upgraded-v0.4.0.txt --without-hashes
  ```

---

### PHASE 2: Configuration Migration
**Duration:** 2-3 hours
**Risk:** High
**Blocking:** Phase 1

#### Step 2.1: Update .chainlit/config.toml

- [ ] **Create backup:**
  ```bash
  cp .chainlit/config.toml .chainlit/config.toml.pre-migration
  ```

- [ ] **Remove deprecated lines:**
  ```bash
  # Edit .chainlit/config.toml
  # Delete or ensure commented out:
  # - Line 19: follow_symlink
  # - Line 80: custom_font
  # - Lines 41-53: [features.audio] section
  # - Lines 90-119: [UI.theme] section
  ```

- [ ] **Update [UI] section to keep only:**
  ```toml
  [UI]
  name = "Assistant"
  default_collapse_content = true
  cot = "full"
  ```

- [ ] **Update [meta] section:**
  ```toml
  [meta]
  generated_by = "2.8.3"
  ```

- [ ] **Verify final config:**
  ```bash
  cat .chainlit/config.toml | grep -E "^\[|^[a-z]" | head -20
  ```

**Expected sections remaining:**
- `[project]`
- `[features]`
- `[features.spontaneous_file_upload]`
- `[UI]`
- `[meta]`

#### Step 2.2: Create Theme File (Optional)

If you want custom theming:

- [ ] **Create .chainlit/theme.json:**
  ```bash
  cat > .chainlit/theme.json << 'EOF'
  {
    "default": "dark",
    "light": {
      "primary": {
        "main": "#F80061",
        "dark": "#980039",
        "light": "#FFE7EB"
      },
      "text": {
        "primary": "#212121",
        "secondary": "#616161"
      },
      "background": "#FAFAFA",
      "paper": "#FFFFFF"
    },
    "dark": {
      "primary": {
        "main": "#F80061",
        "dark": "#980039",
        "light": "#FFE7EB"
      },
      "text": {
        "primary": "#EEEEEE",
        "secondary": "#BDBDBD"
      },
      "background": "#121212",
      "paper": "#1E1E1E"
    }
  }
  EOF
  ```

- [ ] **Verify JSON syntax:**
  ```bash
  python -m json.tool .chainlit/theme.json > /dev/null && echo "✅ Valid JSON"
  ```

#### Step 2.3: Test Configuration

- [ ] **Start application:**
  ```bash
  poetry run chainlit run app.py --port 8001
  ```

- [ ] **Check for config errors:**
  ```bash
  # Look for startup errors
  # Should see: "Chainlit is running at http://localhost:8001"
  # Should NOT see: "Unknown config field" or "Invalid config"
  ```

- [ ] **Test in browser:**
  ```
  Open http://localhost:8001
  Check console for errors
  Verify theme loads correctly
  ```

---

### PHASE 3: Code Migration
**Duration:** 4-6 hours
**Risk:** Medium
**Blocking:** Phase 1

#### Step 3.1: Verify Imports

- [ ] **Check for langgraph.prebuilt usage:**
  ```bash
  grep -r "from langgraph.prebuilt" chat_workflow/
  grep -r "import langgraph.prebuilt" chat_workflow/
  grep -r "create_react_agent" chat_workflow/
  ```

**Expected:** No matches found ✅

- [ ] **Test all imports:**
  ```bash
  poetry run python -c "
  import app
  from chat_workflow.workflows.base import BaseWorkflow, BaseState
  from chat_workflow.workflows.simple_chat import SimpleChatWorkflow
  from chat_workflow.workflows.multimodal_chat import MultimodalChatWorkflow
  from chat_workflow.workflows.resume_optimizer import ResumeOptimizerWorkflow
  from chat_workflow.workflows.lean_canvas_chat import LeanCanvasChatWorkflow
  print('✅ All imports successful')
  "
  ```

#### Step 3.2: Validate Storage Client

- [ ] **Test MinIO storage client:**
  ```bash
  poetry run python -c "
  from chainlit.data.base import BaseStorageClient
  from chat_workflow.storage_client import MinIOStorageClient
  print('✅ Storage client inherits from correct base class')
  "
  ```

- [ ] **Check upload_file signature:**
  ```bash
  poetry run python -c "
  import inspect
  from chat_workflow.storage_client import MinIOStorageClient
  sig = inspect.signature(MinIOStorageClient.upload_file)
  print(f'upload_file signature: {sig}')
  # Verify parameters match BaseStorageClient interface
  "
  ```

#### Step 3.3: Validate Session Access

Your code only accesses:
- `cl.context.session.thread_id` ✅ Still available
- `cl.context.session.chat_profile` ✅ Still available

- [ ] **Test session access:**
  ```python
  # Add to test file or run manually after startup
  # Verify these work in @cl.on_chat_start:
  thread_id = cl.context.session.thread_id
  chat_profile = cl.context.session.chat_profile
  ```

No changes required ✅

#### Step 3.4: Validate Authentication

- [ ] **Test password auth callback signature:**
  ```bash
  poetry run python -c "
  import inspect
  from app import auth_callback
  sig = inspect.signature(auth_callback)
  print(f'auth_callback signature: {sig}')
  # Should be: (username: str, password: str)
  "
  ```

- [ ] **Test OAuth callback signature:**
  ```bash
  poetry run python -c "
  import inspect
  from app import oauth_callback
  sig = inspect.signature(oauth_callback)
  print(f'oauth_callback signature: {sig}')
  # Should be: (provider_id, token, raw_user_data, default_user)
  "
  ```

No changes required ✅

#### Step 3.5: Validate Workflow Patterns

- [ ] **Test all workflows compile:**
  ```bash
  poetry run python << 'EOF'
  from chat_workflow.workflows.workflow_factory import WorkflowFactory
  from chat_workflow.module_discovery import discover_workflows

  discover_workflows()
  workflows = WorkflowFactory.list_workflows()
  print(f"Found {len(workflows)} workflows: {workflows}")

  for name in workflows:
      workflow = WorkflowFactory.create(name)
      graph = workflow.create_graph()
      compiled = graph.compile()
      print(f"✅ {name} compiles successfully")
  EOF
  ```

---

### PHASE 4: Database Schema Validation
**Duration:** 2 hours
**Risk:** Medium
**Blocking:** Phase 3

#### Step 4.1: Check Chainlit Schema

- [ ] **Start database:**
  ```bash
  docker compose up -d postgres
  ```

- [ ] **List current tables:**
  ```bash
  docker exec postgres psql -U postgres -d postgres -c "\dt"
  ```

**Expected tables:**
- `users`
- `threads`
- `steps`
- `elements`
- `feedbacks`
- `langgraphs` (custom)

- [ ] **Check Chainlit migrations:**
  ```bash
  docker exec postgres psql -U postgres -d postgres -c "
  SELECT version_num, description
  FROM alembic_version;
  "
  ```

#### Step 4.2: Test Alembic Migrations

- [ ] **Check for new migrations:**
  ```bash
  poetry run alembic heads
  poetry run alembic current
  ```

- [ ] **Generate migration if needed:**
  ```bash
  poetry run alembic revision --autogenerate -m "upgrade_chainlit_2_8_3"
  ```

- [ ] **Review generated migration:**
  ```bash
  # Check alembic/versions/ for new file
  # Review SQL statements
  # Ensure no destructive changes to langgraphs table
  ```

- [ ] **Apply migration (if generated):**
  ```bash
  poetry run alembic upgrade head
  ```

#### Step 4.3: Validate Custom Tables

- [ ] **Check langgraphs table:**
  ```bash
  docker exec postgres psql -U postgres -d postgres -c "
  \d langgraphs
  "
  ```

**Expected columns:**
- `thread_id` (String, PK)
- `state` (JSON)
- `workflow` (String)

- [ ] **Test data integrity:**
  ```bash
  docker exec postgres psql -U postgres -d postgres -c "
  SELECT COUNT(*) as total_graphs,
         COUNT(DISTINCT workflow) as unique_workflows
  FROM langgraphs;
  "
  ```

#### Step 4.4: Test State Serialization

- [ ] **Test serialization roundtrip:**
  ```bash
  poetry run python << 'EOF'
  from chat_workflow.state_serializer import StateSerializer
  from chat_workflow.workflows.base import BaseState
  from langchain_core.messages import HumanMessage, AIMessage

  # Create test state
  test_state = {
      "messages": [
          HumanMessage(content="Hello"),
          AIMessage(content="Hi there!")
      ],
      "chat_profile": "simple_chat"
  }

  # Serialize
  serialized = StateSerializer.serialize(test_state)
  print(f"Serialized: {serialized}")

  # Deserialize
  deserialized = StateSerializer.deserialize(serialized, BaseState)
  print(f"Deserialized: {deserialized}")

  # Verify
  assert len(deserialized["messages"]) == 2
  assert deserialized["messages"][0].content == "Hello"
  print("✅ Serialization roundtrip successful")
  EOF
  ```

---

### PHASE 5: Testing & Validation
**Duration:** 8 hours
**Risk:** N/A (validation phase)
**Blocking:** Phases 1-4

#### Step 5.1: Unit Tests

- [ ] **Run full test suite:**
  ```bash
  poetry run pytest -v --tb=short
  ```

- [ ] **Test LLM module:**
  ```bash
  poetry run pytest chat_workflow/tests/test_llm.py -v
  ```

- [ ] **Test workflows:**
  ```bash
  poetry run pytest chat_workflow/tests/test_simple_chat.py -v
  ```

- [ ] **Check test coverage:**
  ```bash
  poetry run pytest --cov=chat_workflow --cov-report=html
  ```

#### Step 5.2: Integration Testing - Application Startup

- [ ] **Test 1: Start services:**
  ```bash
  docker compose up -d postgres minio
  poetry run chainlit run app.py --port 8000
  ```

**Expected output:**
```
Your app is available at http://localhost:8000
Chat profiles created: 4
```

- [ ] **Test 2: Check logs:**
  ```bash
  # No ERROR messages
  # Look for: "Logging level set to: INFO"
  # Look for: "Chat profiles created: 4"
  # Look for: "MinIOStorageClient initialized"
  ```

- [ ] **Test 3: Access UI:**
  ```
  Open http://localhost:8000
  - Page loads without errors
  - Login screen appears
  - No console errors in browser devtools
  ```

#### Step 5.3: Authentication Testing

- [ ] **Test 4: Password login:**
  ```
  Username: admin
  Password: admin
  Expected: ✅ Login successful, redirect to chat
  ```

- [ ] **Test 5: Check session:**
  ```
  - Refresh page → Still logged in
  - Check browser cookies → chainlit session cookie present
  - Check cookie attributes → httpOnly, secure (if HTTPS)
  ```

- [ ] **Test 6: Logout (if available):**
  ```
  - Logout → Redirect to login
  - Try to access chat → Redirect to login
  ```

- [ ] **Test 7: OAuth (if configured):**
  ```
  - Click OAuth provider
  - Complete OAuth flow
  - Return to app logged in
  ```

#### Step 5.4: Workflow Testing

- [ ] **Test 8: Workflow discovery:**
  ```
  - Click chat profile selector
  - See 4 workflows:
    1. Simple Chat
    2. Multimodal Chat
    3. Resume Optimizer
    4. Lean Canvas Chat
  ```

- [ ] **Test 9: Simple Chat workflow:**
  ```
  1. Select "Simple Chat"
  2. Check settings panel:
     - Model selector appears
     - Multiple models listed
  3. Send message: "What's 2+2?"
  4. Expected:
     - Message appears in chat
     - Streaming response (token by token)
     - AI responds with answer
     - No errors in logs
  ```

- [ ] **Test 10: Tool calling:**
  ```
  1. In Simple Chat, send: "What time is it?"
  2. Expected:
     - Tool call to datetime tool
     - Tool result appears
     - AI responds with current time
  3. Send: "Search web for latest AI news"
  4. Expected (if TAVILY_API_KEY set):
     - Tool call to search tool
     - Search results appear
     - AI summarizes results
  ```

- [ ] **Test 11: Settings update:**
  ```
  1. Change model in settings (e.g., GPT-4 → Claude)
  2. Send new message
  3. Expected:
     - New model used for response
     - Response style may differ
  4. Check logs:
     - "Updating state based on new settings"
     - "Setting chat_model to [new model]"
  ```

#### Step 5.5: State Persistence Testing

- [ ] **Test 12: Chat state persistence:**
  ```
  1. Start new chat
  2. Send 3-4 messages
  3. Refresh page
  4. Expected:
     - Chat history restored
     - All messages visible
     - Can continue conversation
  ```

- [ ] **Test 13: Resume from database:**
  ```
  1. Send messages in chat
  2. Close browser tab completely
  3. Open new tab → http://localhost:8000
  4. Navigate to previous thread (if UI allows)
  5. Expected:
     - Full chat history loaded
     - Correct workflow active
     - Settings restored
  ```

- [ ] **Test 14: Database query:**
  ```bash
  docker exec postgres psql -U postgres -d postgres -c "
  SELECT thread_id, workflow,
         jsonb_array_length(state->'messages') as msg_count
  FROM langgraphs
  ORDER BY thread_id DESC
  LIMIT 5;
  "
  ```
  Expected: Recent threads with message counts

#### Step 5.6: File Upload Testing

- [ ] **Test 15: Resume Optimizer workflow:**
  ```
  1. Select "Resume Optimizer" profile
  2. Expected: Prompt to upload PDF
  3. Upload sample PDF resume
  4. Expected:
     - File uploaded to MinIO
     - PDF extracted successfully
     - AI provides resume analysis
  ```

- [ ] **Test 16: MinIO storage:**
  ```bash
  # Check file in MinIO
  docker exec minio mc ls myminio/mybucket/
  ```

- [ ] **Test 17: Multimodal Chat with image:**
  ```
  1. Select "Multimodal Chat" profile
  2. Upload image file (PNG/JPG)
  3. Add text: "What's in this image?"
  4. Expected:
     - Image uploaded
     - Image displayed in chat
     - AI describes image content
  ```

#### Step 5.7: UI Testing

- [ ] **Test 18: Theme switching:**
  ```
  - Find theme toggle (if available)
  - Switch light ↔ dark
  - Expected: Colors change smoothly
  ```

- [ ] **Test 19: Responsive design:**
  ```
  - Resize browser window
  - Test on mobile screen size
  - Expected: Layout adapts
  ```

- [ ] **Test 20: All UI elements:**
  ```
  - Chat input field works
  - Send button works
  - File upload button works
  - Settings panel opens/closes
  - Profile selector works
  - No visual glitches
  ```

#### Step 5.8: Error Handling

- [ ] **Test 21: Invalid API key:**
  ```
  1. Remove API key from .env
  2. Try to send message with that provider
  3. Expected: Error message shown to user
  ```

- [ ] **Test 22: Network error:**
  ```
  1. Stop MinIO: docker compose stop minio
  2. Try to upload file
  3. Expected: Error handled gracefully
  4. Start MinIO: docker compose start minio
  ```

- [ ] **Test 23: Database connection loss:**
  ```
  1. Stop PostgreSQL briefly
  2. Try to start new chat
  3. Expected: Error message or retry logic
  ```

#### Step 5.9: Performance Testing

- [ ] **Test 24: Response time:**
  ```
  - Send message
  - Measure time to first token
  - Expected: < 2 seconds
  ```

- [ ] **Test 25: Streaming performance:**
  ```
  - Send message requesting long response
  - Observe streaming
  - Expected: Smooth, no delays between tokens
  ```

- [ ] **Test 26: Memory usage:**
  ```bash
  docker stats --no-stream
  # Check chainlit container memory
  # Expected: Reasonable (< 2GB for normal usage)
  ```

---

### PHASE 6: Docker & Deployment Updates
**Duration:** 3-4 hours
**Risk:** Low
**Blocking:** Phase 5

#### Step 6.1: Update Dockerfile (Optional)

- [ ] **Consider Python version upgrade:**
  ```dockerfile
  FROM python:3.11-slim  # Change from 3.10-slim
  ```

- [ ] **Verify system dependencies:**
  ```dockerfile
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      libsndfile1 \
      curl \  # For healthcheck
      && rm -rf /var/lib/apt/lists/*
  ```

- [ ] **Add healthcheck:**
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
  ```

#### Step 6.2: Update docker-compose.yml

- [ ] **Add healthchecks:**
  ```yaml
  services:
    chainlit:
      healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:8000"]
        interval: 30s
        timeout: 10s
        retries: 3
        start_period: 10s

    postgres:
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 10s
        timeout: 5s
        retries: 5

    minio:
      healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
        interval: 30s
        timeout: 10s
        retries: 3
  ```

- [ ] **Add depends_on with conditions:**
  ```yaml
  services:
    chainlit:
      depends_on:
        postgres:
          condition: service_healthy
        minio:
          condition: service_healthy
  ```

#### Step 6.3: Test Docker Build

- [ ] **Clean build:**
  ```bash
  docker compose down -v
  docker compose build --no-cache
  ```

- [ ] **Start all services:**
  ```bash
  docker compose up
  ```

- [ ] **Check healthchecks:**
  ```bash
  docker compose ps
  # All services should show (healthy)
  ```

- [ ] **Test application in Docker:**
  ```bash
  curl http://localhost:8000
  # Should return HTML
  ```

#### Step 6.4: Production Deployment Checklist

- [ ] **Environment variables:**
  ```bash
  # Verify all required vars in .env:
  grep -E "^[A-Z_]+=" .env | wc -l
  ```

- [ ] **Secrets management:**
  ```
  - CHAINLIT_AUTH_SECRET set to strong random value
  - API keys not hardcoded
  - Database passwords secure
  ```

- [ ] **Volume persistence:**
  ```bash
  # Verify volumes configured in docker-compose.yml
  docker volume ls
  ```

- [ ] **Backup strategy:**
  ```bash
  # Document backup procedure
  # Test restore procedure
  ```

- [ ] **Monitoring:**
  ```
  - Log aggregation configured
  - Error alerting set up
  - Performance metrics collected
  ```

---

### PHASE 7: Documentation Updates
**Duration:** 2-3 hours
**Risk:** Low
**Blocking:** Phase 6 (can parallelize after Phase 5)

#### Step 7.1: Update README.md

- [ ] **Update version badges:**
  ```markdown
  [![Version](https://img.shields.io/badge/Version-0.4.0-blue)](https://github.com/brucechou1983/chainlit-langgraph)
  [![Chainlit](https://img.shields.io/badge/Chainlit-2.8.3-brightgreen)](https://github.com/Chainlit/chainlit)
  [![LangGraph](https://img.shields.io/badge/LangGraph-1.0.1-brightgreen)](https://github.com/langchain-ai/langgraph)
  ```

- [ ] **Add migration notice:**
  ```markdown
  ## Migration Notes

  ### Version 0.4.0 (Breaking Changes)

  This version includes major upgrades:
  - Chainlit 1.3.1 → 2.8.3
  - LangGraph 0.2.45 → 1.0.1

  If upgrading from v0.3.x, please read [MIGRATION.md](MIGRATION.md) for detailed instructions.

  **Key Changes:**
  - Configuration file structure updated
  - Python 3.8 no longer supported (minimum 3.10)
  - Theme customization moved to separate file
  - New security features with cookie-based auth
  ```

- [ ] **Update Getting Started:**
  ```markdown
  ## Requirements
  - Python 3.10 or higher
  - Docker & Docker Compose
  - API keys for LLM providers (optional, can use Ollama)
  ```

#### Step 7.2: Create MIGRATION.md

- [ ] **Copy this plan document:**
  ```bash
  # This document serves as MIGRATION.md
  # No additional action needed
  ```

#### Step 7.3: Update CHANGELOG.md

- [ ] **Add new version entry:**
  ```markdown
  ## [0.4.0] - 2025-10-27

  ### Changed
  - **BREAKING:** Upgraded Chainlit from 1.3.1 to 2.8.3
  - **BREAKING:** Configuration file structure changed - theme and audio sections removed
  - **BREAKING:** Python 3.8 support dropped (minimum Python 3.10)
  - Upgraded LangGraph from 0.2.45 to 1.0.1
  - Updated LangChain packages to latest compatible versions
  - Authentication now uses secure cookie-based system

  ### Added
  - Optional theme.json for custom theme configuration
  - Improved security with updated FastAPI/Starlette
  - Better UI with Shadcn/Tailwind rewrite
  - Access to LangGraph 1.0 features (node caching, commands, etc.)

  ### Removed
  - Audio configuration from config.toml (use new API if needed)
  - Theme configuration from config.toml (moved to theme.json)
  - Support for Python 3.8

  ### Migration
  - See [MIGRATION.md](MIGRATION.md) for detailed upgrade instructions
  - Backup your database before upgrading
  - Update your .chainlit/config.toml (remove deprecated sections)
  - Test thoroughly after upgrade

  ### Security
  - Fixed CVE-2024-47874 via FastAPI/Starlette updates
  - Improved authentication security with httpOnly cookies
  ```

#### Step 7.4: Update Version Files

- [ ] **Update chat_workflow/version.py:**
  ```python
  __version__ = "0.4.0"
  ```

- [ ] **Update pyproject.toml:**
  ```toml
  [tool.commitizen]
  version = "0.4.0"
  ```

- [ ] **Commit version bump:**
  ```bash
  git add chat_workflow/version.py pyproject.toml
  git commit -m "bump: version 0.3.1 → 0.4.0"
  ```

#### Step 7.5: Update Configuration Documentation

- [ ] **Document new config structure:**
  Create `.chainlit/README.md`:
  ```markdown
  # Chainlit Configuration

  ## config.toml

  Main configuration file. After upgrade to Chainlit 2.8.3:

  - ❌ Removed: `follow_symlink`, `custom_font`, `audio`, `theme`
  - ✅ Kept: `project`, `features`, `UI` (basic settings)

  ## theme.json (Optional)

  Custom theme configuration. Create this file if you want to customize colors.

  Example:
  ```json
  {
    "default": "dark",
    "light": { ... },
    "dark": { ... }
  }
  ```

  See: https://docs.chainlit.io/customization/theming
  ```

---

### PHASE 8: Post-Upgrade Optimization (Optional)
**Duration:** Variable
**Risk:** Low
**Blocking:** Phases 1-7 complete

#### Future Enhancement Opportunities

- [ ] **Leverage LangGraph 1.0 Features:**

  **Node Caching:**
  ```python
  # Add caching to expensive nodes
  graph.add_node("expensive_computation", compute_fn, cache=True)
  ```

  **Deferred Nodes:**
  ```python
  # Wait for all upstream paths before summarizing
  graph.add_node("final_summary", summarize_fn, deferred=True)
  ```

  **Command API:**
  ```python
  from langgraph.types import Command
  # More flexible than traditional edges
  ```

- [ ] **Explore Chainlit 2.0 Features:**

  **Custom Elements:**
  ```python
  # Create custom UI elements with Shadcn components
  ```

  **New Theme System:**
  ```python
  # Advanced theme customization with theme.json
  ```

  **Audio Streaming (if needed):**
  ```python
  @cl.on_audio_start
  async def on_audio_start():
      # New audio API
  ```

- [ ] **Python 3.11+ Upgrade:**
  ```dockerfile
  FROM python:3.11-slim
  # Benefits: Better performance, improved error messages
  ```

- [ ] **Performance Optimization:**
  - Profile streaming performance
  - Optimize database queries
  - Add caching layers
  - Implement rate limiting

- [ ] **Security Hardening:**
  - Review cookie security settings
  - Implement CSP headers
  - Add rate limiting
  - Audit API key handling

---

## Rollback Procedures

### Quick Rollback (< 5 minutes)

```bash
# Run rollback script created in Phase 0
./rollback.sh
```

### Manual Rollback

#### Step 1: Restore Dependencies
```bash
cp pyproject.toml.backup pyproject.toml
cp poetry.lock.backup poetry.lock
poetry install
```

#### Step 2: Restore Configuration
```bash
cp .chainlit/config.toml.backup .chainlit/config.toml
rm .chainlit/theme.json  # If created
```

#### Step 3: Restore Database
```bash
docker exec -i postgres psql -U postgres postgres < backup-pre-upgrade-*.sql
```

#### Step 4: Restart Services
```bash
docker compose down
docker compose up -d
```

#### Step 5: Verify
```bash
curl http://localhost:8000
# Check version in logs
```

### Git Rollback

```bash
# If changes committed
git log --oneline
git revert <commit-hash>
git push origin claude/upgrade-chainlit-langraph-011CUXSzH8vJY23G3tyoznkW
```

---

## Testing Checklist Summary

### Critical Tests (Must Pass)
- [ ] Application starts without errors
- [ ] Authentication works (password + OAuth if configured)
- [ ] All 5 workflows discoverable
- [ ] Can send/receive messages with streaming
- [ ] State persists across sessions
- [ ] Database queries work
- [ ] File uploads work (MinIO)
- [ ] Settings updates apply

### Important Tests (Should Pass)
- [ ] All unit tests pass
- [ ] UI renders correctly
- [ ] Dark/light theme works
- [ ] Multimodal chat with images
- [ ] Tool calling works
- [ ] Resume PDF extraction works
- [ ] No console errors
- [ ] Reasonable performance

### Nice-to-Have Tests
- [ ] Test coverage maintained
- [ ] Documentation updated
- [ ] Docker build optimized
- [ ] Healthchecks working
- [ ] Monitoring configured

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Config file errors | High | High | Backup, test immediately |
| Database schema changes | Low | High | Full backup, test migrations |
| Auth flow breaks | Low | High | Test immediately after upgrade |
| State serialization fails | Low | High | Test with existing data |
| UI rendering issues | Medium | Medium | Visual QA, browser testing |
| Performance degradation | Low | Medium | Benchmark before/after |
| Docker build fails | Low | Medium | Test in stages |
| Loss of features | Low | Low | Full feature testing |

---

## Success Metrics

### Technical Metrics
- ✅ Zero critical errors in logs
- ✅ All tests passing (100%)
- ✅ Response time < 2s (first token)
- ✅ Memory usage < 2GB (normal load)
- ✅ All 5 workflows functional
- ✅ 100% feature parity with v0.3.1

### Business Metrics
- ✅ Zero user-reported issues
- ✅ No data loss
- ✅ Same or better UX
- ✅ Improved security posture

---

## Support Resources

### Official Documentation
- [Chainlit 2.0 Migration Guide](https://docs.chainlit.io/guides/migration/2.0.0)
- [Chainlit 2.8.3 Docs](https://docs.chainlit.io/)
- [LangGraph 1.0 Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain 0.3 Docs](https://python.langchain.com/docs/versions/v0_3/)

### Community Support
- [Chainlit GitHub Issues](https://github.com/Chainlit/chainlit/issues)
- [Chainlit Discord](https://discord.gg/chainlit)
- [LangChain Discord](https://discord.gg/langchain)
- [LangGraph Discussions](https://github.com/langchain-ai/langgraph/discussions)

### Troubleshooting Common Issues

**Issue:** "Unknown config field" error
- **Solution:** Remove deprecated fields from config.toml

**Issue:** Authentication not working
- **Solution:** Check CHAINLIT_AUTH_SECRET is set, cookies enabled

**Issue:** Workflows not loading
- **Solution:** Check module discovery logs, verify imports

**Issue:** Database connection errors
- **Solution:** Verify PostgreSQL running, check credentials

**Issue:** MinIO upload fails
- **Solution:** Check MinIO running, bucket exists, credentials correct

---

## Approval & Sign-off

**Before proceeding with upgrade:**

- [ ] All stakeholders informed
- [ ] Backup verified and tested
- [ ] Rollback plan understood
- [ ] Testing environment available
- [ ] Maintenance window scheduled
- [ ] Team members assigned roles
- [ ] Monitoring and alerting ready
- [ ] Communication plan in place

**Approved by:** _________________
**Date:** _________________
**Scheduled for:** _________________

---

## Execution Log

### Phase 0: Preparation
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 1: Dependencies
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 2: Configuration
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 3: Code Migration
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 4: Database
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 5: Testing
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 6: Docker
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

### Phase 7: Documentation
- Started: __________
- Completed: __________
- Issues: __________
- Notes: __________

---

## Post-Upgrade Review

**Completed:** __________
**Total Duration:** __________
**Issues Encountered:** __________
**Lessons Learned:** __________
**Recommendations:** __________

---

**Document Version:** 1.0
**Last Updated:** 2025-10-27
**Next Review:** After upgrade completion
