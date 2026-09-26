"""
Generates ../plan.js from the weekly spec below.

How it works:
- Each block (week) has a date range and a list of study tasks with estimated hours.
- Tasks are placed day by day in order, filling each day's study capacity
  (WEEKDAY_HOURS / WEEKEND_HOURS). Kalamna (2h) and one short video are added
  on top of that every day.
- Days that end up with no study task get a "Catch-up / review" task.

Edit the spec, bump PLAN_VERSION, then run:  python tools/generate_plan.py
Everyone who opens the page will be offered the new version (their checkmarks
and notes are kept for tasks whose id did not change).
"""
import datetime as dt
import json
from pathlib import Path

PLAN_VERSION = "2026-09-26.1"
START, END = dt.date(2026, 10, 1), dt.date(2026, 12, 31)
WEEKEND = {4, 5}          # Python weekday(): Mon=0 ... Fri=4, Sat=5, Sun=6
WEEKDAY_HOURS, WEEKEND_HOURS = 2.5, 3.0
KALAMNA_HOURS = 2

L = {
    "btb": "https://www.youtube.com/playlist?list=PL9ExMy1CBZjnsv2WXFKxXNf41iT1pdT2Q",
    "sd": "https://www.youtube.com/playlist?list=PLMCXHnjXnTnvo6alSjVkgxV-VH6EPyvoX",
    "sd_course": "https://youtu.be/oYxTTirKY8M",
    "rps": "https://youtu.be/W4EwfEU8CGA",
    "cosmic": "https://www.cosmicpython.com/book/preface.html",
    "agent_book": "https://www.manning.com/books/build-an-ai-agent-from-scratch",
    "lc_sql": "https://leetcode.com/studyplan/top-sql-50/",
    "3b1b": "https://www.youtube.com/@3blue1brown",
    "illustrated": "https://jalammar.github.io/illustrated-transformer/",
    "hf_course": "https://huggingface.co/learn/llm-course",
    "karpathy": "https://www.youtube.com/@AndrejKarpathy",
}

def T(title, hours, kind="study", details="", link=""):
    return {"title": title, "hours": hours, "type": kind, "details": details, "link": link}

BLOCKS = [
    dict(n=1, title="Python revision", start="2026-10-01", end="2026-10-07", btb=4, sd=3, tasks=[
        T("Python core: data types, collections, mutability, == vs is, copy", 1.5, details="Shallow vs deep copy, hashable keys, what happens when you pass a list to a function."),
        T("Task: User/Task Data Processor", 2, "project", "Unique skills with a set, deep copy for nested settings, modify a copy safely."),
        T("Functions, *args/**kwargs, lambda, map/filter, comprehensions", 1.5),
        T("Task: Employee Data Processor", 2, "project", "calculate_salary(*salaries, bonus=0), group_by_department, map/filter/lambda."),
        T("Iterators, generators, decorators, context managers, exceptions", 1.5, details="The most important day for understanding how Python works."),
        T("Project: Log Processing System", 2, "project", "LogIterator, error_logs() generator, @measure_time, @handle_errors, log_file() context manager, custom exceptions."),
        T("Modules, packages, venv, type hints, dataclasses, Pydantic", 1.5),
        T("Project: API Request Validation Package", 2, "project", "user_service package, dataclass User, Pydantic CreateUserRequest, absolute vs relative imports."),
        T("Async/await, threads, processes, CPU vs I/O bound", 1.5),
        T("Project: Concurrent Fetcher → Mini Async Job Processing System", 2, "project", "Sequential vs asyncio.gather, then combine everything with @measure_time. Review the interview questions list."),
    ]),
    dict(n=2, title="OOP (Days 1–4) + Cosmic Python 1–2", start="2026-10-08", end="2026-10-14", btb=4, sd=3, tasks=[
        T("OOP from zero: classes, objects, attributes, instance/class/static methods", 1.5),
        T("Project: Bank Account System", 1.5, "project"),
        T("Four pillars: encapsulation, inheritance, polymorphism, abstraction + composition", 2, details="@property, super(), ABC, IS-A vs HAS-A."),
        T("Project: E-commerce Domain (PaymentProvider → Stripe/Paymob)", 2, "project"),
        T("Cosmic Python ch. 1: Domain Modeling", 1.25, "book", link=L["cosmic"]),
        T("Advanced Python OOP: dunders, __eq__/__hash__, dataclasses, Protocol, DI", 1.5),
        T("Project: Notification System (Email/SMS/Push)", 2, "project"),
        T("Cosmic Python ch. 2: Repository Pattern", 1.25, "book", link=L["cosmic"]),
        T("SOLID + key design patterns", 1.5, details="Factory, Builder, Adapter, Decorator, Facade, Strategy, Observer, Repository, Service Layer."),
        T("Project: AI Model Provider System", 2, "project", "Swap OpenAIProvider for GeminiProvider without changing AIService."),
    ]),
    dict(n=3, title="OOP Day 5 + Backend (Days 1–3) + Cosmic 3", start="2026-10-15", end="2026-10-21", btb=4, sd=3, tasks=[
        T("Production OOP: layers, OOP in Django/DRF/FastAPI, testing with fakes", 1.5),
        T("Project: Mini RAG architecture with fake components", 2, "project", "FakeRetriever, FakeLLM, FakeVectorStore behind interfaces."),
        T("Clean code (naming, functions, DRY/KISS/YAGNI) + Git", 1.25),
        T("Task: Refactor a messy API + Git branch/conflict/rebase practice", 1.25, "project"),
        T("Cosmic Python ch. 3: Coupling and Abstractions", 1.5, "book", link=L["cosmic"]),
        T("HTTP, JSON, REST (methods, status codes, resource URLs)", 1.25),
        T("Project: Task Management REST API (FastAPI)", 2, "project", "CRUD, filtering, pagination."),
        T("Authentication vs authorization: hashing, JWT, refresh tokens, RBAC", 1.25),
        T("Project: Add JWT auth + roles/permissions to the Task API", 2, "project"),
    ]),
    dict(n=4, title="Backend (Days 4–7) + Cosmic 4", start="2026-10-22", end="2026-10-28", btb=4, sd=3,
         kalamna_note=(3, "Build the production-style AI Support API capstone (Week 3 Day 7) inside Kalamna"), tasks=[
        T("Testing: pyramid, pytest, fixtures, parametrize, mocking", 1.5),
        T("Project: Test the Task API (auth, permissions, CRUD, failure paths)", 2, "project"),
        T("Logging (structured, request IDs) + env vars + Pydantic Settings", 1),
        T("Project: Add .env config, logging, request IDs to the Task API", 1.5, "project"),
        T("Cosmic Python ch. 4: Service Layer", 1.5, "book", link=L["cosmic"]),
        T("Design patterns: problem → pattern → trade-off", 2, details="Factory, Strategy, Adapter, Decorator, Facade, Observer, Repository, DI."),
        T("Project: AI Provider Architecture (providers + retrievers)", 2.5, "project"),
        T("Review Weeks 1–4 checklists, fix weak spots", 2, "review"),
    ]),
    dict(n=5, title="Databases + SQL (Days 1–4) + Cosmic 5", start="2026-10-29", end="2026-11-04", btb=4, sd=3, tasks=[
        T("SQL foundations: tables, keys, types, CRUD, filtering, sorting", 1.5),
        T("LeetCode SQL: 5 problems (SELECT / filtering)", 1, "leetcode", link=L["lc_sql"]),
        T("DB design: relationships, constraints, normalization; build e-commerce schema", 2),
        T("LeetCode SQL: 5 problems", 1, "leetcode", link=L["lc_sql"]),
        T("System Design Course, part 1 (first hour)", 1, "video", link=L["sd_course"]),
        T("Aggregation, GROUP BY, HAVING, all JOIN types", 1.5),
        T("LeetCode SQL: 5 problems (JOIN / GROUP BY)", 1.25, "leetcode", link=L["lc_sql"]),
        T("Cosmic Python ch. 5: TDD in High and Low Gear", 1.5, "book", link=L["cosmic"]),
        T("Subqueries, EXISTS, CTEs, window functions", 2),
        T("LeetCode SQL: 5 problems (window functions)", 1.25, "leetcode", link=L["lc_sql"]),
        T("System Design Course, part 2 (second hour)", 1, "video", link=L["sd_course"]),
    ]),
    dict(n=6, title="PostgreSQL + Indexes + Month review", start="2026-11-05", end="2026-11-11", btb=4, sd=3, tasks=[
        T("PostgreSQL: UUID, JSONB, arrays, RETURNING, ON CONFLICT, transactions, ACID", 2),
        T("LeetCode SQL: 5 problems", 1, "leetcode", link=L["lc_sql"]),
        T("Indexes: B-tree, composite, EXPLAIN / EXPLAIN ANALYZE", 2),
        T("LeetCode SQL: 5 problems", 1, "leetcode", link=L["lc_sql"]),
        T("1 Million Requests per Second video, part 1", 1.25, "video", link=L["rps"]),
        T("Django ORM bridge: select_related, prefetch_related, annotate, N+1", 1.5),
        T("LeetCode SQL: 5 problems (35 total)", 1, "leetcode", link=L["lc_sql"]),
        T("1 Million Requests per Second video, part 2", 1.25, "video", link=L["rps"]),
        T("Month review: Python, OOP, backend, SQL checklists", 2, "review"),
    ]),
    dict(n=7, title="Text, Embeddings & Transformers + Cosmic 6–7", start="2026-11-12", end="2026-11-24", btb=4, sd=5, tasks=[
        T("NLP basics + text preprocessing (keep it short)", 1.5, details="Normalization, sentence/word splitting, n-grams, vocabulary, OOV."),
        T("Tokenization: BPE, WordPiece, special tokens, context window", 2),
        T("Practice: tokenizer on English, Arabic, Egyptian Arabic, code", 1.5, "project", "Compare token counts; note anything useful for Kalamna.", L["hf_course"]),
        T("Embeddings: vectors, cosine / dot / euclidean, top-k", 2),
        T("Practice: documents → embeddings → top-k retrieval", 2, "project"),
        T("Cosmic Python ch. 6: Unit of Work", 2.5, "book", link=L["cosmic"]),
        T("Neural networks → attention (conceptual, 3Blue1Brown)", 3, details="Forward pass, loss, backprop, RNN/LSTM limits, Q/K/V.", link=L["3b1b"]),
        T("Transformers: self-attention, multi-head, positional info, encoder/decoder", 3, details="BERT vs GPT vs T5.", link=L["illustrated"]),
        T("Hugging Face: pipeline, tokenizers, generation params", 1.5, link=L["hf_course"]),
        T("Practice: sentiment, generation, embeddings, QA with transformers", 2, "project"),
        T("Cosmic Python ch. 7: Aggregates and Consistency Boundaries", 2.5, "book", link=L["cosmic"]),
        T("Project: Semantic Search Engine", 4, "project", "embed_documents, embed_query, similarity, retrieve(query, k)."),
    ]),
    dict(n=8, title="LLMs", start="2026-11-25", end="2026-12-03", btb=3, sd=3, tasks=[
        T("What is an LLM: next-token prediction, autoregressive generation, context window", 2.5, details="Optional: Karpathy's 'Deep Dive into LLMs like ChatGPT'.", link=L["karpathy"]),
        T("How LLMs are trained: cross-entropy, gradient descent, batch/lr, overfitting", 3.5),
        T("Decoder-only architecture review: causal mask, logits, softmax", 2.5),
        T("Decoding: greedy, sampling, temperature, top-k, top-p, stop sequences", 2.5),
        T("Base → chat model: instruction tuning, RLHF, DPO, chat templates", 2.5),
        T("LLM APIs: streaming, retries, timeouts, rate limits, token cost", 3.5, "project", "Reuse your Week 2–3 provider code for the LLM service layer."),
        T("LLM evaluation basics: factuality, hallucination, latency, cost", 1.5),
        T("Project: LLM Q&A API with token/latency/cost logging", 3, "project"),
    ]),
    dict(n=9, title="Prompt engineering + Agent book 1–2", start="2026-12-04", end="2026-12-10", tasks=[
        T("Prompt fundamentals: instruction vs context vs input, delimiters, few-shot", 3, details="Write a bad → improved → structured → few-shot prompt for one task."),
        T("Advanced prompting + templates (classification, extraction, summarization, JSON)", 3.5),
        T("Agent book ch. 1: What is an AI agent?", 2, "book", link=L["agent_book"]),
        T("Structured output: JSON Schema, Pydantic validation, retry on invalid output", 4, "project"),
        T("Agent book ch. 2: The brain of AI agents: LLMs", 2, "book", link=L["agent_book"]),
        T("Failure modes + prompt injection, untrusted retrieved content", 3, details="Relevant to Kalamna: customer documents are untrusted data."),
    ]),
    dict(n=10, title="Advanced RAG + Vector DBs + RAG research guide", start="2026-12-11", end="2026-12-23",
         kalamna_note=(4, "Build the Production-style RAG project inside Kalamna (hybrid + RRF + reranker + citations + metrics)"), tasks=[
        T("RAG architecture deep dive: offline indexing vs online query, IDs, citations", 3),
        T("Types of RAG: naive, advanced, modular, hybrid, multi-query, parent-child, hierarchical, GraphRAG", 4),
        T("Vector databases: dedicated, pgvector, search engines, FAISS", 3),
        T("Vector search + ANN: HNSW, IVF, PQ, speed vs recall vs memory", 3),
        T("Retrieval: dense, BM25, hybrid, RRF, reranking", 4),
        T("RAG evaluation: Recall/Precision@K, MRR, NDCG, faithfulness, abstention", 3.5),
        T("Research case: RAG evaluation (write-up)", 1.5, "research", "Fill the case in Research cases."),
        T("Production RAG: P50/P95/P99, TTFT, cost, multi-tenancy, failure handling", 2.5),
        T("Capacity & scaling: Little's Law, prefill vs decode, KV-cache, GPU sizing", 3, details="Work through the 4,000 users / 100 concurrent / P95 < 8s assignment."),
        T("Research case: From demo to production (write-up)", 1, "research"),
        T("Research case: Multi-user, multi-channel conversations (write-up)", 1.5, "research"),
    ]),
    dict(n=11, title="AI Agents: fundamentals + Agent book 3–4", start="2026-12-24", end="2026-12-31", tasks=[
        T("Agent fundamentals: goal, state, actions, observations, loop (quick review after ch. 1)", 1),
        T("Agent book ch. 3: Enabling actions: tool use", 3, "book", link=L["agent_book"]),
        T("Agent loop + ReAct, termination, max iterations", 1.5),
        T("Tools: schemas, validation, errors, retries, timeouts", 2),
        T("Agent book ch. 4: Implementing a basic ReAct agent", 3, "book", link=L["agent_book"]),
        T("Architectures: ReAct, planner–executor, reflection; workflow vs agent", 3, "research", "Together with Agent guide 1A."),
        T("Agent state vs memory basics", 1),
        T("Reliability: loops, fallbacks, escalation, autonomy slider", 2),
        T("Research case: Tool design, selection & execution (write-up)", 1.5, "research"),
        T("Project: Single-agent Research Assistant (extend the book's ReAct agent)", 3.5, "project", "Tool schemas, loop, state, max iterations, error handling, logging."),
    ]),
]

CASES = [
    dict(id="rag-eval", source="RAG guide", title="RAG evaluation: how do we know it actually works?", week=10,
         question="If we built a RAG system tomorrow, what exact metrics and evaluation process would we put in place?"),
    dict(id="rag-capacity", source="RAG guide", title="From demo to production: capacity, scaling & infrastructure", week=10,
         question="4,000 users, 100 concurrent, 20K input / 500 output tokens, P95 < 8s: are 1, 2, 4, 8 or 16 GPUs enough?"),
    dict(id="rag-multiuser", source="RAG guide", title="Multi-user, multi-channel conversations", week=10,
         question="How would you design identity + sessions + history + memory for a multi-channel enterprise RAG app?"),
    dict(id="agent-1a", source="Agent guide", title="Agent techniques & architectures (1A)", week=11,
         question="Pick one default agent technique for an enterprise internal assistant. Which, and why?"),
    dict(id="agent-1b", source="Agent guide", title="Tool design, selection & execution (1B)", week=11,
         question="Design a minimal but production-ready tool layer for an agent that searches documents, calls internal APIs, and writes to a database."),
    dict(id="agent-2a", source="Agent guide", title="Multi-agent architectures & coordination (2A)", week=None,
         question="Research, write a report, fact-check it: one agent with tools, manager + specialists, or another pattern?"),
    dict(id="agent-2b", source="Agent guide", title="Knowledge, memory & state management (2B)", week=None,
         question="Design a memory architecture for a multi-agent customer-support system without leaking data across customers or agents."),
    dict(id="agent-3a", source="Agent guide", title="Evaluation, measurement & monitoring (3A)", week=None,
         question="If we launch an agent system next month, what evaluation + monitoring stack would you put in place on day 1?"),
    dict(id="agent-3b", source="Agent guide", title="Security, reliability & human collaboration (3B)", week=None,
         question="Design the safety + human oversight layer for an agent that reads company data and sends emails for users."),
]

GUIDE = [
    dict(week=1, goal="Write clean, modern Python and understand how it works underneath.", sections=[
        ("Fundamentals", ["Data types and collections: list, tuple, set, dict", "Mutable vs immutable", "Why dict keys must be hashable", "== vs is", "Shallow vs deep copy", "What happens when you pass a list to a function"]),
        ("Functions", ["Functions and scope", "*args and **kwargs", "Lambda", "map and filter", "List and dict comprehensions (and when they're better)"]),
        ("Python internals", ["Iterable vs iterator", "Generators and yield", "Decorators", "Context managers: __enter__ / __exit__", "Exceptions: try / except / else / finally, custom exceptions"]),
        ("Code organization", ["Modules vs packages, __init__.py", "Absolute vs relative imports", "Virtual environments", "Type hints", "Dataclasses", "Pydantic, and dataclass vs Pydantic"]),
        ("Concurrency", ["async / await and the event loop", "asyncio.gather", "Threads vs processes", "CPU-bound vs I/O-bound", "Why async doesn't speed up CPU-heavy code"]),
    ]),
    dict(week=2, goal="Go from OOP syntax to designing maintainable components.", sections=[
        ("OOP fundamentals", ["Class, object, instance, self, __init__", "Instance vs class attributes", "Instance, class and static methods", "Constructor vs factory method"]),
        ("Four pillars", ["Encapsulation: public, _protected, __private, properties", "Inheritance: super(), multiple inheritance, MRO", "Polymorphism", "Abstraction with ABC"]),
        ("Relationships", ["IS-A vs HAS-A", "Composition, aggregation, association", "Why composition often beats deep inheritance"]),
        ("Advanced Python OOP", ["Dunder methods: __str__, __repr__, __eq__, __hash__, __len__, __getitem__, __iter__", "__eq__, __hash__ and immutability", "Properties: getter, setter, deleter", "Dataclasses: frozen, defaults, field()", "Protocol vs ABC", "Dependency injection"]),
        ("SOLID", ["Single responsibility", "Open/closed", "Liskov substitution", "Interface segregation", "Dependency inversion"]),
        ("Design patterns (first pass)", ["Factory, Factory Method, Builder", "Adapter, Decorator, Facade", "Strategy, Observer", "Repository and service layer"]),
        ("Book", ["Cosmic Python ch. 1: Domain modeling", "Cosmic Python ch. 2: Repository pattern"]),
    ]),
    dict(week=3, goal="Production architecture, clean code, and the core of backend engineering.", sections=[
        ("Production OOP", ["Layers: API, service, domain, infrastructure", "OOP in Django: Model, Manager, QuerySet, Serializer, View, Permission, Middleware", "OOP in FastAPI: Depends, services, repositories", "OOP in AI: LLMProvider, Retriever, VectorStore, Memory abstractions", "Testing with fakes (FakeLLM, FakeRetriever)"]),
        ("Clean code", ["Naming", "Small, single-purpose functions; side effects", "Cohesion and coupling, avoiding god classes", "Guard clauses instead of nested ifs", "DRY (and not abstracting too early), KISS, YAGNI"]),
        ("Git", ["Working tree → staging → commit → remote", "Branch, merge, rebase, conflicts", "stash, reset vs revert, cherry-pick", "fetch vs pull, HEAD, origin", "Pull request workflow, .gitignore, commit messages"]),
        ("HTTP, JSON, REST", ["Methods, headers, path and query params, body", "Status codes (2xx, 4xx, 5xx)", "Statelessness, idempotency, caching, cookies", "Resource URLs, pagination, filtering, sorting, versioning", "Error responses", "JSON serialization and deserialization"]),
        ("Authentication & authorization", ["AuthN vs AuthZ", "Password hashing: salt, bcrypt, Argon2", "Sessions vs JWT; access and refresh tokens", "Expiration, rotation, revocation limits", "RBAC, permissions, object-level authorization", "401 vs 403"]),
        ("Book", ["Cosmic Python ch. 3: Coupling and abstractions"]),
    ]),
    dict(week=4, goal="Make the backend testable, observable and configurable.", sections=[
        ("Testing", ["Testing pyramid: unit, integration, E2E", "pytest, fixtures, parametrize, markers", "Mocking (and mocking LLMs)", "API tests for success and failure paths (401, 403, 404, 409, 422)"]),
        ("Logging & configuration", ["Log levels", "Structured logs, request and correlation IDs", "What never to log: passwords, tokens, keys", "Environment variables, .env, secrets", "Pydantic Settings; dev / test / staging / prod"]),
        ("Design patterns (problem → pattern → trade-off)", ["Factory", "Strategy", "Adapter", "Decorator", "Facade", "Observer", "Repository", "Dependency injection"]),
        ("Capstone (in Kalamna hours)", ["Production-style AI support API: auth, validation, providers, retrieval, logging, tests"]),
        ("Book", ["Cosmic Python ch. 4: Service layer"]),
    ]),
    dict(week=5, goal="Write intermediate SQL confidently without an ORM.", sections=[
        ("SQL foundations", ["Tables, rows, primary / foreign / candidate keys, NULL", "PostgreSQL data types", "SELECT, WHERE, IN, BETWEEN, LIKE / ILIKE, IS NULL", "ORDER BY, LIMIT, OFFSET, DISTINCT", "CASE"]),
        ("Database design", ["1:1, 1:N, N:M relationships", "Foreign keys and ON DELETE: cascade, restrict, set null", "Constraints: NOT NULL, UNIQUE, CHECK, DEFAULT", "Normalization 1NF–3NF and denormalization"]),
        ("Aggregation & joins", ["COUNT, SUM, AVG, MIN, MAX", "GROUP BY, HAVING vs WHERE", "INNER, LEFT, RIGHT, FULL, CROSS, SELF JOIN", "Why LEFT JOIN keeps users with zero orders"]),
        ("Advanced queries", ["Scalar and correlated subqueries", "IN vs EXISTS", "CTEs", "Window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, SUM OVER", "GROUP BY vs window functions", "Dates: DATE_TRUNC, INTERVAL"]),
        ("Practice & extras", ["~20 LeetCode SQL problems", "Cosmic Python ch. 5: TDD in high and low gear", "System Design Course (2h)"]),
    ]),
    dict(week=6, goal="Use PostgreSQL well and connect SQL to the ORM.", sections=[
        ("PostgreSQL", ["Schemas, roles, permissions, extensions", "UUID, JSONB, arrays, TIMESTAMP vs TIMESTAMPTZ", "SERIAL / identity columns", "RETURNING, ON CONFLICT (upsert)", "Transactions and ACID", "Isolation levels (Read Committed, Serializable)"]),
        ("Indexes & performance", ["B-tree indexes", "Composite indexes and column order", "When indexes hurt", "EXPLAIN and EXPLAIN ANALYZE", "Seq scan vs index scan vs bitmap scan"]),
        ("ORM bridge", ["filter, exclude, get, values", "annotate, aggregate, F, Q", "Exists, Subquery, OuterRef", "select_related vs prefetch_related", "N+1 problem; ORM vs raw SQL"]),
        ("Practice & extras", ["35 LeetCode SQL problems total, all 8 patterns", "1 Million Requests per Second video", "Month 1 review"]),
    ]),
    dict(week=7, goal="Understand the components under LLMs: tokens, embeddings, attention.", sections=[
        ("Text processing", ["What NLP is", "Unicode normalization, cleaning", "Sentence and word splitting", "Stop words, stemming vs lemmatization", "N-grams, vocabulary, OOV"]),
        ("Tokenization", ["Token vs word vs character", "Token IDs, special tokens (BOS, EOS, PAD, UNK)", "BPE, WordPiece, Unigram", "Context window and token counting", "Why Arabic uses more tokens"]),
        ("Embeddings", ["What an embedding represents", "Dense vectors and dimensions", "Cosine similarity, dot product, Euclidean distance", "Normalization; similarity vs distance", "Top-k retrieval"]),
        ("Neural networks → attention", ["Layers, weights, activations", "Forward pass, loss, gradient, backpropagation", "Training vs inference", "RNN, LSTM and their limits", "Attention: query, key, value"]),
        ("Transformers", ["Self-attention, multi-head attention", "Feed-forward, residuals, layer norm", "Positional encoding", "Encoder, decoder, causal and cross-attention", "BERT vs GPT vs T5"]),
        ("Hugging Face & project", ["Models, tokenizers, pipeline()", "Generation: max_new_tokens, temperature, top_k, top_p", "Architecture vs weights vs tokenizer vs inference", "Semantic search engine project"]),
        ("Book", ["Cosmic Python ch. 6: Unit of work", "Cosmic Python ch. 7: Aggregates"]),
    ]),
    dict(week=8, goal="Know how LLMs are trained, how they generate, and how to call them in production.", sections=[
        ("LLM fundamentals", ["Language model vs LLM vs chatbot", "Next-token prediction, autoregressive generation", "Parameters, weights, model size", "Context window; training vs inference vs serving"]),
        ("Training", ["Dataset, tokenization, input/target shifting", "Cross-entropy loss, gradient descent", "Batch size, learning rate, epochs, steps", "Training vs validation loss, overfitting", "Why next-token prediction leads to useful capabilities"]),
        ("Architecture", ["Decoder-only transformer", "Causal mask", "Token embeddings + positional information", "Logits and softmax"]),
        ("Generation", ["Greedy vs sampling", "Temperature, top-k, top-p", "Stop sequences, max tokens, repetition penalty", "Top-k retrieval vs top-k generation"]),
        ("Base → chat model", ["Pretraining", "Instruction tuning", "RLHF, reward models, DPO", "Chat templates; system / user / assistant messages"]),
        ("Engineering", ["LLM APIs, auth, model selection", "Streaming, structured responses", "Retries, timeouts, rate limits", "Token counting and cost", "Provider abstraction layer", "Basic evaluation: factuality, hallucination, latency, cost"]),
    ]),
    dict(week=9, goal="Communicate tasks to models reliably and safely.", sections=[
        ("Prompt fundamentals", ["Instruction vs context vs input vs output constraint", "System, user, assistant messages", "Delimiters, role prompting", "Zero-, one-, few-shot"]),
        ("Advanced prompting", ["Task decomposition", "Chain-of-thought and self-consistency (concepts)", "ReAct (concept)", "Prompt templates and dynamic prompts", "Prompt engineering vs RAG"]),
        ("Structured output", ["JSON and JSON Schema", "Pydantic validation, required vs optional, enums", "Parsing failures and retry / re-prompt"]),
        ("Reliability & security", ["Hallucination, ignored context, unsupported answers", "Prompt injection and indirect injection", "Retrieved content is untrusted data", "Instruction / data separation"]),
        ("Book", ["Agent book ch. 1: What is an AI agent?", "Agent book ch. 2: LLMs as the agent's brain"]),
    ]),
    dict(week=10, goal="Design, evaluate and run RAG as a production system.", sections=[
        ("RAG architectures", ["Offline indexing vs online query pipeline", "Naive, advanced, modular RAG", "Hybrid, multi-query, query rewriting", "Parent-child, hierarchical RAG", "GraphRAG; agentic RAG (concept)", "Document IDs, chunk IDs, citations"]),
        ("Vector databases", ["What a vector DB stores (vectors + metadata)", "Dedicated DBs: Pinecone, Milvus, Qdrant, Weaviate", "PostgreSQL + pgvector", "Search engines with vector support", "FAISS / local indexes", "Exact search vs ANN: HNSW, IVF, product quantization"]),
        ("Retrieval", ["Chunking strategies and overlap", "Dense vs sparse (TF-IDF, BM25)", "Hybrid retrieval and RRF", "Reranking", "Metadata filtering, top-k"]),
        ("Evaluation", ["Recall@K, Precision@K, hit rate, MRR, NDCG", "Correctness, faithfulness, citation quality", "Hallucination rate, abstention", "Retrieval quality vs answer quality"]),
        ("Production", ["P50 / P95 / P99, TTFT, throughput", "Cost per request", "Capacity: Little's Law, prefill vs decode, KV-cache", "Multi-tenancy and data isolation", "Empty retrieval and failure handling"]),
        ("Research cases (RAG guide)", ["RAG evaluation", "From demo to production", "Multi-user, multi-channel conversations"]),
    ]),
    dict(week=11, goal="Build a reliable single-agent system.", sections=[
        ("Agent fundamentals", ["LLM app vs agent", "Goal, state, environment, actions, observations", "The agent loop, autonomy"]),
        ("Techniques", ["ReAct", "Planner–executor", "Reflection / Reflexion", "Query decomposition", "Reactive vs goal-directed agents", "When a fixed workflow beats an agent"]),
        ("Tools", ["Tool schemas, inputs, outputs, descriptions", "Tool selection and validation", "Errors, retries, timeouts", "Tool design and permissions"]),
        ("State & reliability", ["Agent state vs memory", "Max iterations, infinite loops", "Fallbacks and graceful failure", "Human escalation, autonomy slider"]),
        ("Practice", ["Agent book ch. 3: Tool use", "Agent book ch. 4: Basic ReAct agent", "Single-agent research assistant project", "Research cases: Agent guide 1A and 1B"]),
    ]),
]

NEXT = dict(
    title="Next 3 months (Jan – Mar 2027)",
    intro="The next plan continues the same flow: fundamentals → LLMs → RAG → agents → production AI systems. It picks up exactly where Week 11 ends. Details will be planned later.",
    sections=[
        ("Multi-agent systems", ["Single vs multi-agent, avoiding agent sprawl", "Manager/worker, hierarchical, democratic, swarm, actor-critic", "Communication: shared state, message brokers, event buses, A2A", "Orchestration engines and frameworks (LangGraph, AutoGen, CrewAI)"]),
        ("Agent memory", ["Context vs state vs memory", "Short-term and long-term memory", "Semantic, episodic, procedural memory", "Memory lifecycle: capture, store, retrieve, consolidate, expire", "Privacy and tenant isolation"]),
        ("Production agents", ["Evaluation of agent trajectories", "Monitoring and observability (traces, OpenTelemetry, Langfuse)", "Security: tool misuse, injection, threat modeling", "Reliability and human oversight"]),
        ("Books & research", ["Agent book Part 2: RAG knowledge bases, memory, planning, code execution, multi-agent, evaluation", "Agent guide cases 2A, 2B, 3A, 3B"]),
        ("Also on the list", ["Side project", "Remaining backend stack from the roadmap: Django/DRF, FastAPI, Redis, Docker"]),
    ],
)

def M(id, title, kind, url, weeks, note="", source="plan"):
    return dict(id=id, title=title, kind=kind, url=url, weeks=weeks, note=note, source=source)

MATERIALS = [
    # Your chosen materials
    M("m-btb", "Beyond the Basics (ما بعد الأساسيات), pragma", "Playlist", L["btb"], [1,2,3,4,5,6,7,8], "31 videos, about 4 per week through Week 8."),
    M("m-sd", "System Design playlist", "Playlist", L["sd"], [1,2,3,4,5,6,7,8], "26 videos of 15–25 min. Check this link: it may point to the wrong playlist."),
    M("m-sdc", "System Design Course: APIs, Databases, Caching, CDNs, Load Balancing", "Video", L["sd_course"], [5], "2h, split into two sessions."),
    M("m-rps", "Let's Handle 1 Million Requests per Second", "Video", L["rps"], [6], "2h 30m, Month 1 finale."),
    M("m-cosmic", "Architecture Patterns with Python (Cosmic Python)", "Book", L["cosmic"], [2,3,4,5,7], "Free online. Part 1 (ch. 1–7) in this plan."),
    M("m-agentbook", "Build an AI Agent (From Scratch), Hur & Song", "Book", L["agent_book"], [9,11], "Part 1 (ch. 1–4) in this plan; Part 2 next plan."),
    M("m-lc", "LeetCode: Top SQL 50", "Practice", L["lc_sql"], [5,6], "35 problems across the 8 SQL patterns."),
    M("m-ragguide", "BARQ RAG research guide (PDF)", "Guide", "", [10], "Your internship PDF. Answer the cases in Research cases."),
    M("m-agentguide", "BARQ Agent research guide (PDF)", "Guide", "", [11], "Your internship PDF. 1A and 1B in this plan; the rest next plan."),
    # Suggested references
    M("s-pytut", "Python tutorial (official docs)", "Docs", "https://docs.python.org/3/tutorial/", [1], source="suggested"),
    M("s-asyncio", "asyncio documentation", "Docs", "https://docs.python.org/3/library/asyncio.html", [1], source="suggested"),
    M("s-pydantic", "Pydantic documentation", "Docs", "https://docs.pydantic.dev/latest/", [1,9], source="suggested"),
    M("s-datamodel", "Python data model (dunder methods)", "Docs", "https://docs.python.org/3/reference/datamodel.html", [2], source="suggested"),
    M("s-guru", "Refactoring.Guru: design patterns (with Python examples)", "Website", "https://refactoring.guru/design-patterns", [2,4], source="suggested"),
    M("s-progit", "Pro Git book", "Book", "https://git-scm.com/book/en/v2", [3], "Free online.", source="suggested"),
    M("s-mdnhttp", "MDN: HTTP", "Docs", "https://developer.mozilla.org/en-US/docs/Web/HTTP", [3], source="suggested"),
    M("s-fastapi", "FastAPI tutorial (incl. security / JWT)", "Docs", "https://fastapi.tiangolo.com/tutorial/", [3,4], source="suggested"),
    M("s-owasp-pw", "OWASP Password Storage Cheat Sheet", "Docs", "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html", [3], source="suggested"),
    M("s-pytest", "pytest documentation", "Docs", "https://docs.pytest.org/", [4], source="suggested"),
    M("s-logging", "Python logging HOWTO", "Docs", "https://docs.python.org/3/howto/logging.html", [4], source="suggested"),
    M("s-settings", "Pydantic Settings", "Docs", "https://docs.pydantic.dev/latest/concepts/pydantic_settings/", [4], source="suggested"),
    M("s-pgtut", "PostgreSQL tutorial (official docs)", "Docs", "https://www.postgresql.org/docs/current/tutorial.html", [5], source="suggested"),
    M("s-pgwin", "PostgreSQL: window functions", "Docs", "https://www.postgresql.org/docs/current/tutorial-window.html", [5], source="suggested"),
    M("s-luke", "Use The Index, Luke (SQL indexing)", "Website", "https://use-the-index-luke.com/", [6], source="suggested"),
    M("s-explain", "PostgreSQL: using EXPLAIN", "Docs", "https://www.postgresql.org/docs/current/using-explain.html", [6], source="suggested"),
    M("s-djorm", "Django: making queries", "Docs", "https://docs.djangoproject.com/en/stable/topics/db/queries/", [6], source="suggested"),
    M("s-3b1b", "3Blue1Brown: neural networks & transformers", "Playlist", L["3b1b"], [7], source="suggested"),
    M("s-illustrated", "The Illustrated Transformer, Jay Alammar", "Article", L["illustrated"], [7], source="suggested"),
    M("s-hf", "Hugging Face LLM course", "Course", L["hf_course"], [7,8], "Chapters 1–2 fit Week 7.", source="suggested"),
    M("s-tiktok", "Tiktokenizer (see tokens live)", "Tool", "https://tiktokenizer.vercel.app/", [7], "Try Arabic vs English.", source="suggested"),
    M("s-karpathy", "Andrej Karpathy: Deep Dive into LLMs like ChatGPT", "Video", L["karpathy"], [8], "On his channel.", source="suggested"),
    M("s-prompt", "Anthropic prompt engineering guide", "Docs", "https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview", [9], source="suggested"),
    M("s-owasp-llm", "OWASP Top 10 for LLM applications", "Docs", "https://genai.owasp.org/llm-top-10/", [9,10], "Prompt injection and related risks.", source="suggested"),
    M("s-pgvector", "pgvector", "Docs", "https://github.com/pgvector/pgvector", [10], source="suggested"),
    M("s-react", "ReAct paper (Yao et al.)", "Paper", "https://arxiv.org/abs/2210.03629", [11], source="suggested"),
    M("s-effective", "Building effective agents (Anthropic)", "Article", "https://www.anthropic.com/engineering/building-effective-agents", [11], "When to use workflows vs agents.", source="suggested"),
    M("s-mcp", "Model Context Protocol docs", "Docs", "https://modelcontextprotocol.io/", [11], source="suggested"),
]

def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(days=1)

def build():
    days, uid = [], 0
    def nid():
        nonlocal uid
        uid += 1
        return f"t{uid:04d}"

    blocks_out = []
    btb_i = sd_i = 0
    for b in BLOCKS:
        start, end = dt.date.fromisoformat(b["start"]), dt.date.fromisoformat(b["end"])
        bdays = [dict(date=d.isoformat(), week=b["n"], tasks=[]) for d in daterange(start, end)]
        cap = [WEEKEND_HOURS if dt.date.fromisoformat(x["date"]).weekday() in WEEKEND else WEEKDAY_HOURS for x in bdays]
        # Place each task on the day where its midpoint falls on the cumulative
        # capacity line (squeezed proportionally if the week is over capacity).
        total_h, total_cap = sum(t["hours"] for t in b["tasks"]), sum(cap)
        scale = min(1.0, total_cap / total_h) if total_h else 1.0
        bounds, acc = [], 0.0
        for c in cap:
            acc += c
            bounds.append(acc)
        pos = 0.0
        for t in b["tasks"]:
            mid = (pos + t["hours"] / 2) * scale
            i = next((k for k, bd in enumerate(bounds) if mid < bd), len(bdays) - 1)
            bdays[i]["tasks"].append(dict(id=nid(), **t))
            pos += t["hours"]
        if total_h > total_cap:
            print(f"  ! Week {b['n']} is over capacity by {total_h - total_cap:.1f}h (days squeezed)")
        for k, day in enumerate(bdays):
            if not day["tasks"]:
                day["tasks"].append(dict(id=nid(), **T("Catch-up / review day", cap[k], "review",
                    "Finish anything unchecked from this week, or revise the checklist.")))
        # Kalamna every day (first task of the day)
        note = b.get("kalamna_note")
        for k, day in enumerate(bdays):
            title, details = "Kalamna work block", ""
            if note and k >= len(bdays) - note[0]:
                title, details = "Kalamna work block (project week)", note[1]
            day["tasks"].insert(0, dict(id=nid(), **T(title, KALAMNA_HOURS, "kalamna", details)))
        # One short video per day, alternating playlists
        vids = []
        nb, ns = b.get("btb", 0), b.get("sd", 0)
        while nb or ns:
            if nb:
                btb_i += 1; nb -= 1
                vids.append(T(f"Beyond the Basics, video {btb_i} of 31", 0.33, "video", "One ~20 min video; 1.25x speed works well.", L["btb"]))
            if ns:
                sd_i += 1; ns -= 1
                vids.append(T(f"System Design playlist, video {sd_i} of 26", 0.33, "video", "One ~20 min video.", L["sd"]))
        step = max(1, len(bdays) // max(1, len(vids))) if vids else 1
        for j, v in enumerate(vids):
            bdays[min(j * step if len(vids) < len(bdays) else j, len(bdays) - 1)]["tasks"].append(dict(id=nid(), **v))
        days.extend(bdays)
        blocks_out.append(dict(n=b["n"], title=b["title"], start=b["start"], end=b["end"]))
        print(f"Week {b['n']:>2}: {sum(t['hours'] for t in b['tasks']):5.1f}h study / {sum(cap):5.1f}h capacity")

    assert days[0]["date"] == START.isoformat() and days[-1]["date"] == END.isoformat()
    return dict(version=PLAN_VERSION, start=START.isoformat(), end=END.isoformat(),
                weekend=sorted(WEEKEND), profiles=[dict(id="ahmed", name="Ahmed"), dict(id="bassant", name="Bassant")],
                weeks=blocks_out, days=days, cases=CASES, guide=GUIDE, next_plan=NEXT, materials=MATERIALS)

if __name__ == "__main__":
    plan = build()
    out = Path(__file__).resolve().parent.parent / "plan.js"
    out.write_text("// Generated by tools/generate_plan.py. Edit the generator (or this file) and bump version.\n"
                   "window.PLAN = " + json.dumps(plan, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"Wrote {out} ({len(plan['days'])} days, btb/sd totals checked in output)")
