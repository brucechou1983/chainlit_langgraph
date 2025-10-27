## v0.4.0 (2025-10-27)

### Changed

- **BREAKING:** Upgraded Chainlit from 1.3.1 to 2.8.3
- **BREAKING:** Configuration file structure changed (removed deprecated theme and audio sections)
- **BREAKING:** Python 3.8 support dropped (minimum Python 3.10)
- Upgraded LangGraph from 0.2.45 to 1.0.1 (backward compatible)
- Updated LangChain packages to latest compatible versions (langchain-openai 0.3.35, langchain-anthropic 0.3.0)
- Upgraded Docker base image from Python 3.10 to 3.11

### Added

- Implemented missing BaseStorageClient methods for Chainlit 2.x compatibility
  - `get_read_url()` for presigned URL generation
  - `delete_file()` for file deletion from MinIO
  - `close()` for cleanup operations
- Comprehensive migration documentation (MIGRATION_PLAN.md, UPGRADE_SUMMARY.md, UPGRADE_CHECKLIST.md)
- Better security with secure cookie-based authentication
- Improved UI with Shadcn/Tailwind rewrite from Chainlit 2.x
- Access to LangGraph 1.0 features (node caching, deferred nodes, commands)

### Fixed

- Updated import path for BaseStorageClient from `chainlit.data.base` to `chainlit.data.storage_clients.base`
- Removed deprecated `chainlit.telemetry.trace` decorator from auth.py
- Fixed CVE-2024-47874 via FastAPI/Starlette security updates

### Migration

- See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed upgrade instructions
- Configuration cleanup required: remove `[features.audio]` and `[UI.theme]` sections from `.chainlit/config.toml`
- Update `[meta] generated_by` to "2.8.3"
- Database backup recommended before upgrading

## v0.3.1 (2024-11-14)

### Feat

- Google model provider

## v0.3.0 (2024-11-05)

### Feat

- image capability
- model capability

### Fix

- wrong capability of haiku
- missing llm_factory

## v0.2.0 (2024-11-05)

### Feat

- groq support
- grok support

### Refactor

- model display naming
- llm factory pattern

## v0.1.1 (2024-10-25)

### Feat

- dynamic parameter parsing for Ollama
- parsing model specific params from ollama api response
- update claude 3.5 sonnet
- add starters for all workflows
- add password auth to simplify the setup
- simple resume chat
- docker compose support
- compose and dockerfile
- chat persistence
- google oauth support
- update claude model list
- get available model automatically
- auto module discovery
- extra header to enable the prompt caching
- new resume module
- Tavily search engine integration
- tool selection node
- search before answer
- llm module to support multiple llm api vendors
- simple chat demo

### Fix

- issues when parsing list of str
- minor issue
- remove the extra operation of creating session in the on_chat_start
- the messages serialize/deserialize issue
- final state is incorrectly updated
- wrong .chainlit folder issue
- error when OAuth provider is not given
- error when TAVILY_API_KEY is not given in .env
- remove redundant function def
- update .env example
- exclude .files created by chainlit app cache
- minio invalid bucket issue
- resume chat settings correctly
- error handling when openai key is not set
- temporary fix for randomly missing thread id in the data store.
- correctly resume chat_profile
- save/load graph states to db
- app not reloading when making changes
- duplicate import
- setting simple chat as default workflow
- host machine ollama api access
- remove the fixed cache request header
- setting menu not updating when switching to other workflows
- duplicate tool name issue
- llama tool calling issue
- langsmith setting in .env
- missing example in .env
- noisy console print
- conversation history issues

### Refactor

- llm module
- change ollama model naming rule to prioritize it
- workflow factory
-  move the tool routing logic to the base class
- better logging
- move get_chat_settings to BaseWorkflow
- move chat_settings to BaseWorkflow and add workflow-wise ChatProfile
- remove hard code output chat model name
- dynamic workflow loading and use langchain native tool calling
- separate name and value fields of the tool results
- move to search module
- setting module
- move graph and state to graphs module

### Perf

- better performance
- async tools binding
- change tool selection model options
- modify tool selection prompt
