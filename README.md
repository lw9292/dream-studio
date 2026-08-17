# Dream Studio V1.23.1 — Asset Entity System + Canvas Stability

V1.23.1 keeps the V1.23 editable asset-entity system and adds a canvas stability hotfix: durable nodes cannot be deleted from local ReactFlow state, persisted layout is validated, and the canvas can rebuild non-destructively from project data.

## Project logic

Dream Studio now treats people and scenes as **editable project entities**, not as pictures:

```text
Project
├─ Characters (editable entities)
│  ├─ name / description / consistency lock
│  ├─ current reference
│  ├─ reference history
│  └─ entity versions
├─ Scenes (editable entities)
│  ├─ name / description / consistency lock
│  ├─ current reference
│  ├─ reference history
│  └─ entity versions
└─ Shots
   ├─ character entity IDs
   ├─ scene entity ID
   ├─ shot-specific references
   └─ generated outputs + history
```

A Shot references the **entity**, and generation resolves the entity's **current reference**. Older images remain available as history instead of all being injected into the model.

## Editing

- Click a character/scene in the left **Project Resources** list, or click **Edit** on its canvas card.
- Edit name and description directly.
- Switch the current reference image without deleting older references.
- Restore an older entity-setting version.
- The existing consistency lock affects generation consistency; it does not block explicit user edits.

## Non-destructive impacts

Changing a character/scene never deletes an existing video. Shots that already have generated visual output are marked as having changed inputs. The old result remains visible; the next manual generation uses the current entity/reference version and clears the stale marker when the new video succeeds.

---

# Previous V1.22 model/API notes

# Dream Studio V1.22 — Adaptive Model Desk

V1.22 applies Occam's razor to **模型与 API**.

Dream Studio no longer assumes any concrete provider or model name. A fresh installation starts with an empty API/model catalog. The system only understands four things:

```text
Connection   where/how to reach an API
Wire format  how requests are shaped
Capability   language / image / video behavior
Model ID     the exact id returned or entered by the user
```

Core rule:

> Configure a connection, inspect what it exposes, classify only what can be known, and let Auto use only real detected models.

## Fresh-install behavior

A fresh V1.22 database contains:

```text
API connections: 0
Models:          0
Auto bindings:   0
```

There are no built-in provider presets, model IDs, or vendor-specific Auto defaults. Existing databases keep previously saved connections/models for backward compatibility.

Mock mode still lets the workbench run without external services; mock generation does not require catalog entries.

## Settings flow

The visible taxonomy remains creator-oriented:

```text
语言模型
图像模型
视频模型
```

Under it, **API 连接** is infrastructure rather than the primary navigation.

Typical setup:

```text
添加 API
  ↓
Base URL + API Key
  ↓
自动识别 / 检测接口
  ↓
读取模型目录（如果存在）
读取 OpenAPI（如果存在）
探测可用端点
  ↓
自动归类能确定的模型
  ↓
无法确定的只补“类型 / 请求格式”
  ↓
加入工作台
```

## No model-name guessing

Dream Studio does **not** classify a model because its ID contains words such as `image`, `video`, a vendor name, or a product family name.

Automatic classification uses explicit API metadata when available, for example:

```text
type
category
modality / modalities
input_modalities / output_modalities
capabilities
```

If the model list does not carry useful metadata, Dream Studio leaves the model unclassified instead of guessing. The UI lets the user confirm only the missing model type and request format.

## Adaptive interface inspection

V1.22 can inspect two independent surfaces.

### 1. Model catalog

The configured model-list URL is tried first; otherwise the connection profile can use a conventional `/models` path.

Supported common response shapes include:

```json
{"data":[{"id":"model-a"}]}
```

```json
{"models":[{"id":"model-a"}]}
```

```json
["model-a","model-b"]
```

The exact returned model ID is stored; Dream Studio never invents a remote model ID.

### 2. OpenAPI / endpoint surface

An optional `OpenAPI URL` can point to a Swagger/OpenAPI JSON document. When present, Dream Studio reads:

```text
path
HTTP method
operation/summary
request-body fields
```

Those real interface fields can be used to infer a compatible wire format when the shape matches an adapter contract.

If OpenAPI is unavailable, Dream Studio falls back to non-generating endpoint probes and the connection's selected request-format family.

## Request formats, not model presets

The advanced model editor exposes request shapes rather than concrete products:

```text
Language
- Chat Completions JSON
- Responses JSON
- Responses JSON (compatible variant)

Image
- Image Generation JSON
- Image Generation JSON (compatible variant)

Video
- Async Video Job JSON
- Multimodal Video Job JSON
```

These are execution contracts. The visible model name/model ID comes only from the user's API connection or manual input.

## API connection modes

A connection may use:

```text
自动识别
Chat / Responses / Images 兼容
异步视频任务格式
Responses + Images 兼容变体
完全手动
```

Usually only `Base URL + API Key` are needed. Advanced endpoint overrides remain available for gateways with unusual routing:

```text
models
openapi
responses
chat
images
video_create
video_query
file_retrieve
```

Every override may be a relative path or a complete third-party URL.

## Auto is now adaptive

V1.22 removes the user-facing matrix of per-capability default-model selectors.

When a node has no explicit model, Auto deterministically chooses from saved models that satisfy:

```text
model enabled
+ connection enabled
+ API Key configured
+ connection inspected
+ capability matches
```

If the API exposes a model catalog, the exact model ID must also have been observed in that catalog.

A legacy saved capability binding is treated only as a preference. If it is unavailable, Auto may use another eligible real model. Explicit per-node selection still has priority and is never silently replaced.

## Manual-first creative workflow

The creative product boundary remains unchanged:

```text
optional AI 起稿
      ↓
user connects Character / Scene / references to Shot
      ↓
user chooses model/mode when desired
      ↓
Generate
      ↓
system handles validation, dimensions, jobs, retries and persistence
```

Language-model assistance exists only when the user explicitly invokes **AI 起稿** or **AI 帮我**.

## Canvas safety

The V1.19+ canvas safeguards remain:

- persistent per-project node positions;
- persistent viewport x/y/zoom;
- minimap;
- `显示全部节点` recovery action.

## Local development

Backend:

```bash
cd apps/api
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --port 8787
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:5173`.

## Verification

V1.22 release checks:

```text
Backend regression: 68 passed
Python compile: passed
TS / TSX syntax transpilation: passed
Git whitespace check: pending final release pass
```

A complete Vite production build depends on npm package availability in the execution environment.
