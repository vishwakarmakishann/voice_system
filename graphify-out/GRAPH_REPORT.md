# Graph Report - voice_system_v1.0  (2026-05-23)

## Corpus Check
- 43 files · ~7,270 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 320 nodes · 330 edges · 46 communities (36 shown, 10 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93ce6b73`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 16 edges
2. `5. Realtime Conversation Lifecycle` - 12 edges
3. `BaseEvent` - 9 edges
4. `2. Primary Technology Decisions` - 8 edges
5. `PlatformError` - 7 edges
6. `22. Reliability Strategy` - 7 edges
7. `ProviderError` - 6 edges
8. `STTProvider` - 6 edges
9. `3. Core Product Requirements` - 6 edges
10. `31. Suggested Database Domains` - 6 edges

## Surprising Connections (you probably didn't know these)
- `startup_event()` --calls--> `init_qdrant()`  [INFERRED]
  apps/api/src/main.py → apps/api/src/services/memory_service.py
- `extract_memories()` --calls--> `CoreMemory`  [INFERRED]
  apps/api/src/services/memory_service.py → apps/api/src/models/memory.py
- `search_memory()` --calls--> `search_archival_memory()`  [INFERRED]
  apps/api/src/api/memory.py → apps/api/src/services/memory_service.py
- `TranscriptRequest` --uses--> `CoreMemory`  [INFERRED]
  apps/api/src/api/memory.py → apps/api/src/models/memory.py
- `SearchRequest` --uses--> `CoreMemory`  [INFERRED]
  apps/api/src/api/memory.py → apps/api/src/models/memory.py

## Communities (46 total, 10 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (31): 11. Memory Architecture, 13. Memory Write Policy, 14. Memory Retrieval Strategy, 15. Background Memory Jobs, 16. Tool Calling System, 17. Tool Execution Rules, 18. Self-Healing Architecture, 19. Startup Recovery Requirements (+23 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (10): generate_token(), TokenResponse, BaseSettings, Settings, init_qdrant(), Ensure the Qdrant collection exists., Settings, startup_event() (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (24): dependencies, livekit-client, @livekit/components-react, @livekit/components-styles, next, react, react-dom, devDependencies (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (12): LLMProvider, Cancel the current generation., Generate a streaming response from the LLM.         Yields a dict containing tok, Receive partial and final transcripts from the provider.         Yields a dict w, Close the connection to the STT provider., Connect to the STT provider., Stream raw audio chunk to the STT provider., STTProvider (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.14
Nodes (14): search_memory(), SearchRequest, TranscriptRequest, Base, BaseModel, CoreMemory, LongTermMemory, Message (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.20
Nodes (14): CriticalError, InterruptionError, LLMProviderError, PlatformError, ProviderError, Raised when an operation is interrupted by the user speaking., Base exception for all platform errors., Errors that the system can automatically recover from. (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (14): 2. Primary Technology Decisions, Backend, Databases, Durable relational data, Ephemeral realtime coordination, Frontend, Infrastructure, Initial AI Providers (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.26
Nodes (9): login(), read_users_me(), register(), UserCreate, UserResponse, create_access_token(), get_password_hash(), verify_password() (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (12): 5. Realtime Conversation Lifecycle, Step 10 — Playback, Step 11 — Interruption, Step 1 — Authentication, Step 2 — Session Creation, Step 3 — Room Join, Step 4 — Worker Attachment, Step 5 — Audio Streaming (+4 more)

### Community 10 - "Community 10"
Cohesion: 0.42
Nodes (8): AssistantStartedSpeaking, AssistantStoppedSpeaking, BaseEvent, InterruptionOccurred, ToolExecutionCompleted, ToolExecutionRequested, UserStartedSpeaking, UserStoppedSpeaking

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (9): 4. High-Level Architecture, Layer 1 — Frontend, Layer 2 — Control Plane API, Layer 3 — Realtime Runtime, Layer 4 — Infrastructure Services, LiveKit, PostgreSQL, Qdrant (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.29
Nodes (7): 22. Reliability Strategy, LiveKit Failure, LLM Failure, PostgreSQL Failure, Redis Failure, STT Failure, TTS Failure

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (6): 31. Suggested Database Domains, Conversations, Identity, Memory, Operations, Sessions

### Community 14 - "Community 14"
Cohesion: 0.33
Nodes (6): 33. Performance Targets, Assistant response start, Initial Targets, Interruption reaction, STT partial latency, TTS startup

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (6): 3. Core Product Requirements, Memory system, Multi-user concurrency, Production reliability, Provider abstraction, Realtime speech-to-speech

### Community 16 - "Community 16"
Cohesion: 0.40
Nodes (3): geistMono, geistSans, metadata

### Community 18 - "Community 18"
Cohesion: 0.40
Nodes (4): code:bash (npm run dev), Deploy on Vercel, Getting Started, Learn More

### Community 19 - "Community 19"
Cohesion: 0.40
Nodes (5): 34. Testing Strategy, Integration Tests, Load Tests, Recovery Tests, Unit Tests

### Community 20 - "Community 20"
Cohesion: 0.40
Nodes (5): 6. Multi-User Architecture, Design Rules, Every session is isolated, Horizontal scalability, Workers must be stateless

### Community 21 - "Community 21"
Cohesion: 0.50
Nodes (4): 12. Memory Types, Long-Term Memory, Session Memory, Short-Term Memory

### Community 27 - "Community 27"
Cohesion: 0.67
Nodes (3): 32. Deployment Strategy, Local Development, Production Deployment

### Community 28 - "Community 28"
Cohesion: 0.67
Nodes (3): 30. Suggested Backend Modules, API, Worker

## Knowledge Gaps
- **147 isolated node(s):** `name`, `version`, `private`, `dev`, `build` (+142 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `2. Primary Technology Decisions` connect `Community 7` to `Community 0`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `5. Realtime Conversation Lifecycle` connect `Community 9` to `Community 0`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `4. High-Level Architecture` connect `Community 11` to `Community 0`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **What connects `Base exception for all platform errors.`, `Base exception for provider-related errors.`, `Raised when an operation is interrupted by the user speaking.` to the rest of the system?**
  _164 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08615384615384615 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._