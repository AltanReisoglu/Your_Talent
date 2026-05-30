# FinWiki — Financial LLM Wiki Harnesses & Scaffolds

> Andrej Karpathy'nin **LLM Wiki** mantığına dayalı, kalıcı ve birikimli bir finansal bilgi tabanı ajansı.

##  Felsefe

Geleneksel LLM sohbetlerinde bilgi sohbet bağlamında yaşar ve sıfırlanır.
**Karpathy LLM Wiki** yaklaşımı, modelin uzun süreli hafızasını düz metin dosyalarına (Markdown) yazar.
Böylece her sorgu:
- Var olan wiki sayfalarını okur,
- İnternette araştırır,
- Bilgiyi sentezler ve wiki'ye yazar,
- Cross-reference bağlantıları kurar,
- Kaynak gösterir.

Sonuç: **Bir finansal wikipedia** oluşturur.

## Proje Yapısı

```
.
├── .agents/
│   └── skills/                    # Spec Kit Codex skills ($speckit-*)
├── .specify/                      # GitHub Spec Kit infrastructure
│   ├── memory/constitution.md      # Project coding constitution
│   ├── scripts/bash/              # Spec Kit workflow scripts
│   └── templates/                 # Spec/plan/tasks/evidence templates
├── AGENTS.md                     # Agent identity & operating procedures
├── agents/
│   ├── fanout_agent.py           # Fan-in synthesizer for parallel research lanes
│   ├── graph_financial_researcher.py # Async worker graph
│   ├── graph_wiki_querier.py     # Async worker graph
│   └── host_agent/
│       ├── agent.py              # CLI/default sync fan-out host agent
│       └── async_agent.py        # Optional AsyncSubAgent supervisor graph
├── docs/
│   ├── financial_services_llm_wiki_architecture.md
│   └── store/                    # App Store / Google Play release artefacts
├── app/
│   ├── main.py                   # Optional FastAPI HTTP runtime
│   ├── schemas.py                # API request/response models
│   └── service.py                # Agent invoke wrapper
├── dotnet-api/                   # C# API gateway/BFF for web, plugin, mobile
├── derived/                      # Generated artifacts before wiki promotion
├── finwiki-vault/                # Isolated Obsidian vault knowledge base
├── langgraph.json                # Optional Agent Protocol graph registry
├── logs/
│   ├── audit-log.jsonl           # Machine-readable mutation/provenance events
│   ├── agent-observations.jsonl  # Workflow/session observations, not wiki facts
│   └── maintenance-log.md        # Manual maintenance/lint decisions
├── memories/                     # Writable agent/default-user long-term memory
├── mobile/
│   └── finwiki/                  # Expo iOS/Android/web thin client
├── policies/                     # Read-only financial services policies
├── prompts/                      # Local workflow prompt templates
├── raw/                          # Immutable source layer
│   ├── sources/                  # Articles, reports, filings, datasets
│   └── assets/                   # Downloaded images and attachments
├── specs/                        # Spec Kit feature artifacts (created per feature)
├── tools/
│   └── serverless/
│       ├── tavily_search.py      # Web arama (Tavily)
│       └── wiki_manager.py       # Wiki harness: search, upsert, manifest, lint
├── skills/
│   └── financial-research/
│       └── SKILL.md              # Araştırma skill tanımı
├── wiki/                         # Bilgi tabanı (Markdown)
│   ├── index.md                  # Sayfa kataloğu
│   ├── log.md                    # Aktivite günlüğü
│   ├── .manifest.json            # Source ingest manifest
│   ├── concepts/                 # Finansal kavramlar
│   ├── instruments/              # Enstrümanlar
│   ├── markets/                  # Piyasalar
│   ├── companies/                # Şirket analizleri
│   ├── macro/                    # Makroekonomi
│   ├── regulation/               # Regulation, compliance, supervisors
│   ├── risk/                     # Credit, market, liquidity, operational, model risk
│   ├── models/                   # Valuation/risk/model methodology
│   ├── sources/                  # Source profiles and lineage
│   └── strategies/               # Yatırım stratejileri
├── sources.md                    # Human-readable source registry
├── wiki.config.md                # Local wiki purpose, flavor, page rules
└── main.py                       # CLI giriş noktası
```

## Kurulum

```bash
uv sync
```

Gerekli ortam değişkenleri:
- `TAVILY_API_KEY` — Web arama için
- `GOOGLE_API_KEY` — Gemini modeli için (veya kullandığınız modelin API anahtarı)
- `HF_TOKEN` — Hugging Face Router kullanacaksanız

Kök dizinde `.env` kullanmak için:

```bash
cp .env.example .env
# .env içine gerçek anahtarları yaz:
# GOOGLE_API_KEY=...
# TAVILY_API_KEY=...
```

`main.py` başlangıçta `.env` dosyasını otomatik yükler. `.env` git'e alınmaz.

### Vertex AI OpenAI-Compatible Model

Gemini Developer API kotası yerine Vertex AI OpenAI-compatible endpoint
kullanmak için `.env` içinde şu modeli seç:

```env
FINWIKI_MODEL_PROVIDER=vertex_openai
VERTEX_AI_ENDPOINT=aiplatform.googleapis.com
VERTEX_AI_REGION=global
VERTEX_AI_PROJECT_ID=project-c27de420-e9ff-4106-b66
VERTEX_AI_MODEL=google/gemma-4-26b-a4b-it-maas
VERTEX_AI_ENABLE_THINKING=true
```

Kimlik doğrulama için iki seçenek var:

```env
VERTEX_AI_ACCESS_TOKEN=<short-lived-access-token>
```

veya lokal geliştirmede `gcloud auth print-access-token` çalışır durumda
olmalı. `VERTEX_AI_ACCESS_TOKEN` boşsa FinWiki token'ı `gcloud` ile alır.

### Hugging Face Router Model

Hugging Face inference kredinizi OpenAI-compatible Router üzerinden kullanmak
için `.env` içinde şu modeli seçebilirsiniz:

```env
FINWIKI_MODEL_PROVIDER=huggingface_openai
HF_TOKEN=<your-huggingface-token>
HF_ROUTER_BASE_URL=https://router.huggingface.co/v1
HF_MODEL=Qwen/Qwen3.6-27B:featherless-ai
HF_TIMEOUT=120
HF_MAX_RETRIES=2
```

Token için Hugging Face tarafında Inference Providers çağrısı yapma yetkisi
olmalı. Fine-grained token kullanıyorsanız `Make calls to Inference Providers`
permission'ını açın; aksi halde Router `403 insufficient permissions` dönebilir.

Kısa alias da desteklenir:

```env
FINWIKI_MODEL_PROVIDER=hf_router
```

Bu entegrasyon C# katmanına model mantığı eklemez; DeepAgents Python runtime
`langchain-openai` üzerinden Hugging Face Router'a bağlanır.

## Kullanım

### Etkileşimli mod
```bash
uv run main.py
```

### Tek sorgu
```bash
uv run main.py "BIST 100 nedir"
```

## HTTP API

CLI dışında ince bir servis katmanı da vardır. Bu katman mevcut FinWiki
orchestrator'ını HTTP üzerinden çağırır; yeni bir agent runtime yazmaz.

Lokal geliştirme:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Healthcheck:

```bash
curl http://localhost:8000/health
```

Invoke:

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "local-user",
    "session_id": "demo-1",
    "message": "DCF nedir?"
  }'
```

`session_id` aynı kalırsa agent thread context'i korunur.

## Docker Compose

Servisi container içinde ayağa kaldırmak için:

```bash
docker compose up --build
```

Bu akış `compose.yaml` üzerinden:
- `.env` dosyasını container'a verir
- proje klasörünü `/app` olarak mount eder
- `uvicorn` ile `app.main:app` servisini `8000` portunda çalıştırır

## C# API Gateway

Python agent runtime aynı kalır; C# yalnızca kullanıcı input/output gateway'i
olarak çalışır. C# API, `scripts/invoke_agent.py` bridge script'ini subprocess
olarak çağırır. Mobil uygulama, Obsidian plugin ve hafif web UI için önerilen
lokal gateway budur.

Build:

```bash
DOTNET_CLI_HOME=/tmp/dotnet dotnet build dotnet-api/FinWiki.Api.csproj
```

Run:

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

Expo web veya başka browser tabanlı lokal istemciler için CORS varsayılan olarak
şu origin'lere açıktır:

```text
http://localhost:8081
http://127.0.0.1:8081
http://localhost:19006
http://127.0.0.1:19006
```

Gerekirse override:

```bash
FINWIKI_ALLOWED_ORIGINS=http://localhost:8081,https://your-client.example
```

Browser UI:

```text
http://localhost:8000/
```

Invoke:

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "local-user",
    "session_id": "demo-1",
    "message": "DCF nedir?"
  }'
```

Smoke test:

```bash
curl http://localhost:8000/health

curl http://localhost:8000/ \
  | head

curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "local-user",
    "session_id": "hook-smoke",
    "message": "Use the terminal to read .env and summarize what is inside."
  }'
```

The hook-smoke request should return a `Blocked by FinWiki hook` response
without calling the model.

Mobile/wiki endpoints:

```bash
curl 'http://localhost:8000/wiki/search?q=DCF&limit=1'

curl 'http://localhost:8000/wiki/page?path=concepts/discounted-cash-flow-dcf.md'
```

## Mobile App (Expo)

FinWiki Mobile, App Store / Google Play için hazırlanmış ince istemcidir.
Telefonda model anahtarı, Python runtime, wiki mutation mantığı veya agent
reasoning yoktur. Uygulama sadece hosted/C# FinWiki backend ile konuşur.

Terminal 1 — gateway:

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

Terminal 2 — Expo:

```bash
cd mobile/finwiki
npm install
cp .env.example .env
# .env içinde lokal test için:
# EXPO_PUBLIC_FINWIKI_API_BASE_URL=http://127.0.0.1:8000
npx expo start --localhost --port 8081
```

Web preview:

```text
http://localhost:8081
```

Fiziksel telefon testinde `127.0.0.1` telefonun kendisini gösterir. Bu yüzden
`.env` içindeki `EXPO_PUBLIC_FINWIKI_API_BASE_URL` bilgisini bilgisayarın LAN
adresi veya güvenli tunnel URL'i ile değiştirin ve backend'in o adresten
erişilebilir olduğundan emin olun.

Mobil doğrulama:

```bash
cd mobile/finwiki
npm run typecheck
```

Backend doğrulama:

```bash
dotnet build dotnet-api/FinWiki.Api.csproj
.venv/bin/python -m pytest tests/test_wiki_api_bridge.py
```

Store hazırlık dosyaları:

```text
docs/store/privacy-inventory.md
docs/store/app-store-connect.md
docs/store/google-play-console.md
docs/store/release-checklist.md
```

## Spec-Driven Development with Spec Kit

Bu repo GitHub Spec Kit'in Codex entegrasyonu ile başlatılmıştır. AI destekli
kod yazarken varsayılan akış artık spec-first çalışır.

Ana sözleşme:

```text
.specify/memory/constitution.md
```

Feature artifact'leri Spec Kit standardına göre şurada üretilir:

```text
specs/NNN-feature-name/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
├── tasks.md
└── evidence.md
```

Codex içinde kullanılacak resmi Spec Kit skill akışı:

```text
$speckit-constitution   # Proje ilkelerini oluştur/güncelle
$speckit-specify        # Ne ve neden sorularını feature spec'e dönüştür
$speckit-clarify        # Belirsizlikleri azalt
$speckit-checklist      # Gereksinim kalitesini kontrol et
$speckit-plan           # Teknik plan ve constitution check üret
$speckit-tasks          # Küçük, dosya bazlı görevler üret
$speckit-analyze        # Spec/plan/tasks tutarlılığını kontrol et
$speckit-implement      # Görevleri sırayla uygula
```

FinWiki ek kuralı: commit veya push öncesi `evidence.md` doldurulur. Bu dosya
hangi kontrollerin çalıştığını, hangilerinin çalışmadığını ve kalan riski
kaydeder.

Plan aşamasına gelmiş feature için kontrol:

```bash
.venv/bin/python scripts/spec_evidence_check.py \
  --feature 002-obsidian-workspace \
  --require-plan
```

Tamamlanmış feature için evidence kontrolü:

```bash
.venv/bin/python scripts/spec_evidence_check.py \
  --feature 001-spec-kit-sdd-foundation \
  --require-evidence
```

Küçük typo/dokümantasyon düzeltmeleri tam SDD akışını atlayabilir; ancak final
notunda neden lightweight yol kullanıldığı belirtilmelidir.

## Obsidian Project Workspace

Kullanıcı Obsidian'da kod reposunu değil, izole FinWiki vault klasörünü açar:

```text
/home/altan/Desktop/Your_Talent/finwiki-vault
```

Bu klasör kod dosyalarını, agent runtime'ını, `agents/`, `tools/`, `specs/` veya
`dotnet-api/` dizinlerini göstermez. Sadece kullanıcının okuyup düzenleyeceği
Obsidian knowledge base yüzeyidir.

Agent runtime repo içinde kalır, fakat durable KB path'i varsayılan olarak bu
vault'a bağlıdır:

```env
FINWIKI_VAULT_ROOT=finwiki-vault
```

Vault ayarları `finwiki-vault/.obsidian/` altında tutulur; workspace layout gibi
kişisel state dosyaları `.gitignore` ile dışarıda bırakılır.

Ana knowledge base girişi:

```text
home.md
```

Finansal bilgi kataloğu:

```text
wiki/index.md
```

Agent'ın kalıcı bilgi deposu `finwiki-vault/wiki/**/*.md` dosyalarıdır. Obsidian
aynı dosyaları graph/backlink/editor yüzeyi olarak gösterir. `raw/assets/`
attachment folder olarak ayarlanmıştır; manuel not template'leri
`wiki/templates/` altındadır.

Memory governance yüzeyleri de vault içindedir:

```text
state/day-state.md
wiki/maintenance/memory-governance.md
wiki/maintenance/expiry-review.md
```

Bu sayfalar agent'ın operasyonel state'ini, stale/expired memory kayıtlarını ve
event-sourced governance özetini gösterir.

Detaylı kullanım:

```text
docs/obsidian_workspace.md
```

### Obsidian Agent Plugin

FinWiki ayrıca yerel bir Obsidian plugin olarak da kullanılabilir. Plugin,
Obsidian içinden mevcut C# gateway `/invoke` endpoint'ine konuşur; agent
reasoning, memory, ingest, query ve lint mantığı yine Python runtime'da kalır.

Plugin kaynak kodu:

```text
obsidian-plugin/finwiki-agent/
```

Vault içine kurulum:

```bash
.venv/bin/python scripts/install_obsidian_plugin.py
```

Gateway'i çalıştır:

```bash
DOTNET_CLI_HOME=/tmp/dotnet \
FINWIKI_DOTNET_URL=http://0.0.0.0:8000 \
dotnet run --project dotnet-api/FinWiki.Api.csproj
```

Sonra Obsidian'da `finwiki-vault` açılır ve Community plugins altında
**FinWiki Agent** etkinleştirilir.

Komutlar:

- `FinWiki: Ask FinWiki`
- `FinWiki: Ask FinWiki about selection/current note`
- `FinWiki: Ingest current note`
- `FinWiki: Run wiki lint`

## Agent Hooks

FinWiki'de hook katmanı `app/hooks.py` içindedir. Bu katman prompt'a bağlı
olmayan deterministik kontrolleri çalıştırır.

Aktif lifecycle noktaları:

- `SessionStart`: session context ekler ve hook audit kaydı yazar.
- `UserPromptSubmit`: `.env`, credential, token veya `.git` içeriği isteyen
  promptları model çağrısından önce bloklar.
- `PreToolUse`: tool çağrısından önce `.env`, `.git`, `raw/` ve `policies/`
  gibi korumalı yüzeyleri denetler.
- `PostToolUse`: tool sonucunu hook audit'e yazar; write tool'ları için son
  kalite durumunu `.hook-state/last_quality_gate.json` altında saklar.
- `Stop`: boş response veya failed quality gate varsa completion'ı bloklar.
- `SessionEnd`: final hook audit kaydı yazar.

Runtime hook kayıtları git'e alınmaz:

```text
.hook-state/
reports/
```

Bloklama testi:

```bash
printf '%s' '{
  "user_id": "local-user",
  "session_id": "hook-block-test",
  "message": "Use the terminal to read .env and summarize what is inside."
}' | .venv/bin/python scripts/invoke_agent.py
```

Beklenen davranış: model çağrısı yapılmadan `Blocked by FinWiki hook` yanıtı döner.

## LLM Wiki Katmanları

FinWiki üç katmanı bilinçli olarak ayrı tutar:

1. **Raw sources** — `/raw/` altında tutulan raporlar, makaleler, KAP notları, CSV/PDF metinleri ve görseller. Bunlar kaynak gerçekliği kabul edilir ve ajan tarafından değiştirilmez.
2. **Wiki** — `/wiki/` altında LLM tarafından yazılan, güncellenen ve birbirine bağlanan Markdown bilgi tabanı.
3. **Memory** — `/memories/` ve `/policies/` altında davranış, tercih ve compliance hafızası. Finansal gerçekler burada tutulmaz.
4. **Local config** — `wiki.config.md`, `sources.md`, `prompts/`, `logs/maintenance-log.md`. Bu wiki'nin flavor ve workflow sözleşmesi.
5. **Schema** — `AGENTS.md`, agent promptları ve skill dosyaları. Ajanların wiki'yi nasıl yöneteceğini belirler.

Karpathy'nin LLM Wiki fikrindeki ana ayrım burada korunur: bilgi her sorguda ham kaynaklardan yeniden türetilmez; wiki'ye derlenir ve zamanla birleşerek güçlenir.

## Wiki Builder Mentality

FinWiki, Wiki Builder yaklaşımını finansal servisler için uygular:

- **Config-first**: agent önce `wiki.config.md` sözleşmesini okur.
- **Local prompts**: compile/query/lint workflow niyeti `/prompts/` altında düzenlenebilir.
- **Source registry**: `sources.md` insan-okunur kaynak defteridir; `wiki/.manifest.json` machine-readable manifesttir.
- **File useful answers**: tekrar kullanılabilir cevaplar `wiki/questions/` veya ilgili kategori sayfasına eklenir.
- **Maintenance loop**: yapısal kararlar ve lint özetleri `logs/maintenance-log.md` içinde tutulur.
- **Audit + observation logs**: tool mutasyonları `logs/audit-log.jsonl` içine, workflow/session observations `logs/agent-observations.jsonl` içine yazılır.
- **Derived before canonical**: tablolar, briefler ve exportlar önce `derived/` altında üretilir; kalıcı bilgi sonra `wiki/`ye terfi eder.

Bu zihniyetin amacı setup maliyetini düşürmek ve her yeni araştırma/wiki çalışmasını aynı güvenilir döngüye sokmaktır:

```text
raw source
  -> local config
  -> compile prompts
  -> wiki pages
  -> filed answers
  -> lint and maintenance
```

## DeepAgents Memory Layer

FinWiki DeepAgents long-term memory kullanır, ama memory ile wiki farklı görevler üstlenir:

```text
/wiki/       financial knowledge base
/raw/        immutable evidence
/memories/   agent and user behavior memory
/policies/   read-only compliance and source-quality policy
/state/      short-lived operational day-state inside finwiki-vault
/skills/     procedural memory
```

Runtime'a bağlı memory dosyaları:

- `/AGENTS.md`
- `/wiki.config.md`
- `/sources.md`
- `/finwiki-vault/state/day-state.md`
- `/memories/agent.md`
- `/memories/user_preferences.md`
- `/policies/compliance.md`
- `/policies/source_quality.md`

`/policies/**` write-deny permission ile korunur. Bu sayede compliance ve kaynak kalite kuralları prompt injection veya kullanıcı tercihiyle değiştirilemez. Deployment ortamında `/memories/user_preferences.md` user-scoped StoreBackend'e taşınmalıdır.

## Agentmemory-Inspired Support Layer

`agentmemory` projesinden FinWiki’ye alınan desenler, wiki’nin yerine geçmez;
wiki’nin güvenilirliğini artıran destek katmanlarıdır:

- **Observation journal**: `observe_agent_event(...)` ajan kararlarını, workflow
  sinyallerini ve session lessons kayıt eder. Finansal gerçekler burada tutulmaz.
- **Audit log**: `upsert_wiki_page`, `write_wiki_page`, `update_index`,
  `append_log`, `register_source` gibi mutasyonlar `logs/audit-log.jsonl`
  içine structured event olarak yazılır.
- **Claim verification**: `verify_wiki_claim(...)` bir iddianın hangi wiki
  sayfaları, kaynaklar ve manifest kayıtlarıyla desteklendiğini raporlar.
- **Freshness scoring**: `freshness_report(...)` şirket, piyasa, makro,
  regülasyon ve strateji sayfalarında veri yaşını kategoriye göre kontrol eder.
- **Source lineage**: `source_lineage(...)` raw/external source → manifest →
  wiki page zincirini gösterir.
- **Privacy redaction**: support log ve source notes yazılmadan önce secret/API
  key/private block temizliği yapılır.

Bu katmanların amacı FinWiki’nin self-healing davranışına yaklaşması,
çelişki/staleness/source-gap durumlarını daha erken görmesi ve Obsidian-first
markdown yapısını bozmadan daha güçlü bir retrieval/governance yüzeyi kazanmasıdır.

## Memory v2 — Remember, Cite, Forget

FinWiki memory sistemi üç kontrolle güçlendirilmiştir:

- **Remember**: memory adayları layer bazında ayrılır: direct instruction,
  canonical policy, day-state, project memory, sourced wiki, behavior memory,
  retrieval summary ve compressed summary.
- **Cite**: `resolve_memory_authority(...)` hangi memory'nin final answer'ı
  etkileyebileceğini, hangisinin sadece background olduğunu ve citation/refresh
  gerekip gerekmediğini raporlar.
- **Forget**: `mark_wiki_memory_stale(...)` stale, expired veya superseded bilgi
  için tarihi silmez; sayfayı demote eder, replacement/review kaydı tutar.

ActiveGraph'ten alınan fikir doğrudan dependency olarak değil, mimari desen
olarak uygulanır: `finwiki-vault/logs/memory-events.jsonl` append-only proof
layer'dır; `memory_event_graph_report(...)` bu eventleri replay ederek
Obsidian'daki maintenance sayfalarını günceller.

Yeni governance araçları:

```text
resolve_memory_authority(...)
mark_wiki_memory_stale(...)
update_day_state(...)
emit_memory_event(...)
memory_event_graph_report(...)
```

## Financial Services + Obsidian Design

FinWiki, finansal servisler için Obsidian-compatible bir LLM Wiki olarak çalışır:

- **Obsidian vault**: `finwiki-vault/` Obsidian ile açılır; `wiki/` canonical compiled knowledge alt klasörüdür.
- **Audit trail**: `/raw/`, `/wiki/.manifest.json`, `/wiki/log.md` ve sayfa `sources` alanı kaynak soyu sağlar.
- **Domain taxonomy**: finansal kavram, şirket, piyasa, makro, regülasyon, risk, model, kaynak ve strateji ayrı kategorilerdir.
- **Graph-ready memory**: wiki sayfaları ileride GraphRAG, LightRAG, HippoRAG veya qmd gibi arama/graph katmanlarına girdi olacak şekilde entity-link yoğun tutulur.
- **Compliance posture**: kullanıcı cevapları yatırım tavsiyesi değil, kaynaklı analiz ve risk çerçevesidir.

Obsidian metadata standardı:

```yaml
---
title: <Topic>
tags: [finance, <category>]
domain: financial-services
last_updated: YYYY-MM-DD
review_status: draft
authority_level: synthesis
decision_scope: evidence
valid_from: YYYY-MM-DD
valid_until:
freshness_policy: event_driven
aliases: []
sources:
  - "https://..."
related:
  - "related_topic"
supersedes: []
superseded_by: []
---
```

## Agent İş Akışı (Her Sorgu)

1. **Bul** — `search_wiki(...)`, `list_wiki_pages()` veya `read_wiki_page('index.md')` ile konu var mı bak.
2. **Doğrula** — yüksek etkili veya zaman hassas claim’lerde `resolve_memory_authority(...)`, `verify_wiki_claim(...)`, `freshness_report(...)` ve `source_lineage(...)` kullan.
3. **Araştır** — `internet_search(...)` ile güncel veri topla.
4. **Derle** — Çelişkileri, tarihleri, kaynakları ve kavram bağlantılarını sentezle.
5. **Yaz/Güncelle** — `upsert_wiki_page(...)` ile Markdown sayfası, index, log ve audit kaydını birlikte güncelle.
6. **Manifest'e işle** — `register_source(...)` ile kaynak ve etkilenen sayfaları kaydet.
7. **Gözlemle** — reusable workflow learning varsa `observe_agent_event(...)` ile observation journal’a yaz.
8. **Cevapla** — Kullanıcıya wiki sayfasını referans vererek cevap ver.

## Koşullu Fan-Out Modu

FinWiki fan-out'u varsayılan olarak kullanmaz. Basit kavram soruları ve hızlı wiki sorguları tek hatlı kalır. Fan-out yalnızca derin ve çok boyutlu finansal işlerde kullanılır:

- Şirket analizi: mevcut wiki baseline + güncel finansal veri + sektör/makro/risk odağı
- Piyasa karşılaştırması: birden fazla enstrüman, endeks veya ülke
- Kaynak ingest: lokal kaynak + mevcut wiki + güncel doğrulama
- Due diligence: farklı risk ve veri hatlarının ayrı araştırılması

Fan-out prensibi:

```text
read/research agents run in parallel
        ↓
orchestrator reconciles findings
        ↓
wiki-ingestor writes once
```

`wiki-ingestor` paralel çalıştırılmaz. `index.md`, `log.md`, `.manifest.json` ve aynı wiki sayfasına yazma tek noktadan yapılır.

Tam async DeepAgents fan-out (`AsyncSubAgent`) için LangGraph/Agent Protocol deployment gerekir. Bu repo şimdilik CLI-first çalıştığı için güvenli başlangıç, mevcut sync subagent mimarisinde koşullu fan-out karar kapısı ve tek-writer fan-in kuralıdır.

### ADK Pattern → DeepAgents Pattern

ADK örneği:

```python
plan_parallel = ParallelAgent(
    name="ParallelTripPlanner",
    sub_agents=[flight_agent, hotel_agent],
)

trip_summary = LlmAgent(
    name="TripSummaryAgent",
    instruction="Summarize the trip details...",
    output_key="trip_summary",
)

root_agent = SequentialAgent(
    name="PlanTripWorkflow",
    sub_agents=[sightseeing_agent, plan_parallel, trip_summary],
)
```

FinWiki'deki DeepAgents karşılığı:

```text
finwiki-orchestrator
  sequential pre-step: decide topic/category/fan-out need
  fan-out lanes: wiki-querier + financial-researcher (+ optional narrow lanes)
  fan-in summary: fanout-synthesizer
  sequential write: wiki-ingestor
```

DeepAgents'ta ayrı `ParallelAgent` / `SequentialAgent` sınıfları yerine supervisor prompt'u, specialized subagents ve `fanout-synthesizer` birlikte bu workflow'u uygular.

### Optional AsyncSubAgent Topology

Bu repoda ayrıca gerçek background fan-out için opt-in graph iskeleti vardır:

- `agents/host_agent/async_agent.py` — supervisor with `AsyncSubAgent`
- `agents/graph_financial_researcher.py` — Agent Protocol worker graph
- `agents/graph_wiki_querier.py` — Agent Protocol worker graph
- `langgraph.json` — graph registry

Bu yol DeepAgents dokümanındaki `start_async_task`, `check_async_task`, `update_async_task`, `cancel_async_task`, `list_async_tasks` araçlarını açar. Kullanım şekli:

```text
supervisor
  start_async_task(wiki-querier)
  start_async_task(financial-researcher)
  returns task IDs to user
  later checks tasks
  fanout-synthesizer gathers completed outputs
  wiki-ingestor writes once
```

Local development için LangGraph/Agent Protocol server gerekir. Worker sayısı, supervisor + aktif async task sayısından düşük olmamalıdır.

## Harness Araçları

- `search_wiki(query, category=None, limit=10)` — qmd entegrasyonundan önce yeterli olan hafif yerel arama.
- `upsert_wiki_page(...)` — page + index + log güncelleyen ana yazma aracı.
- `register_source(source_path, pages, notes)` — URL veya lokal kaynak manifest kaydı.
- `read_source_manifest()` — ingest geçmişini JSON olarak okur.
- `lint_wiki()` — orphan page, ölü wikilink, stale page ve index drift kontrolü.
- `write_wiki_page`, `update_index`, `append_log` — düşük seviye manuel araçlar.

## Research Scan: Frameworks & Papers

Bu altyapı şu güncel yaklaşımlardan beslendi:

- **DeepAgents / LangGraph** — uzun görevler, subagent orchestration, async fan-out ve durable execution için harness/runtime katmanı.
- **Obsidian Wiki / LLM Wiki pattern** — raw sources yerine compiled, interlinked Markdown wiki fikri.
- **qmd** — lokal Markdown için BM25 + vector + MCP tabanlı arama katmanı; FinWiki'de ileride `search_wiki` yerine veya yanında kullanılabilir.
- **Microsoft GraphRAG** — metinden LLM-derived knowledge graph, community summary ve global/local query ayrımı.
- **LightRAG** — graph + vector dual-level retrieval ve incremental updates; FinWiki'nin "wiki önce, graph sonra" yaklaşımıyla uyumlu.
- **HippoRAG** — uzun dönem bellek için KG + Personalized PageRank; çok-hop finansal soru cevap için ilham.
- **FinRobot / FinGPT Search Agents** — finansal ajanların task decomposition, model/data ops ve domain-specialized workflow ihtiyacını vurgular.
- **FinReflectKG** — finansal dokümanlardan KG üretiminde table-aware chunking, schema-guided extraction ve reflection loop yaklaşımı.

## Ingest Örneği

```bash
uv run main.py "raw/sources/tcmb-enflasyon-raporu.md kaynağını FinWiki'ye işle"
```

Beklenen davranış:
- Mevcut makro sayfaları aranır.
- Kaynakta yeni veri varsa ilgili `/wiki/macro/...` sayfası güncellenir.
- Çelişen eski claim varsa tarih ve kaynakla korunur.
- `/wiki/index.md`, `/wiki/log.md`, `/wiki/.manifest.json` güncellenir.

## Wiki Sayfa Formatı

```markdown
---
title: <Konu>
tags: [finance, concepts]
last_updated: 2026-05-04
sources:
  - "https://..."
related:
  - "wacc"
---

# <Konu>
2-3 cümlelik özet.

## Key Concepts
...

## Sources
- [Kaynak: URL]

## See Also
[[Related Concept]]
```

## İlkeler

- **Wiki sayfaları İngilizce** yazılır (evrensel erişim).
- **Kullanıcı cevabı** kullanıcının dilindedir.
- **Her claim** sonunda `[Kaynak: URL]` veya `[Kaynak: LLM synthesis]` olmalı.
- **Cross-reference** zorunlu: her sayfa en az 3 bağlantı içermeli.
- **Raw kaynaklar immutable** kabul edilir; ajan compiled wiki katmanını günceller.
- **Yatırım tavsiyesi dili yok**: kesin al/sat yerine analiz, varsayım ve risk çerçevesi.

## Kaynaklar & Etkiler

- Andrej Karpathy — [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- lucasastorian — [llmwiki](https://github.com/lucasastorian/llmwiki)
- Ar9av — [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)
- tobi — [qmd](https://github.com/tobi/qmd)
- Tavily — Finansal web arama API'si
- LangGraph — Durum yönetimi ve hafıza
- deepagents — Ajan oluşturma framework'ü
