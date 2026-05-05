# FinWiki — Financial LLM Wiki Harness

> Andrej Karpathy'nin **LLM Wiki** mantığına dayalı, kalıcı ve birikimli bir finansal bilgi tabanı ajansı.

## Felsefe

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
├── AGENTS.md                     # Agent identity & operating procedures
├── agents/
│   ├── fanout_agent.py           # Fan-in synthesizer for parallel research lanes
│   ├── graph_financial_researcher.py # Async worker graph
│   ├── graph_wiki_querier.py     # Async worker graph
│   └── host_agent/
│       ├── agent.py              # CLI/default sync fan-out host agent
│       └── async_agent.py        # Optional AsyncSubAgent supervisor graph
├── langgraph.json                # Optional Agent Protocol graph registry
├── raw/                          # Immutable source layer
│   ├── sources/                  # Articles, reports, filings, datasets
│   └── assets/                   # Downloaded images and attachments
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
│   └── strategies/               # Yatırım stratejileri
└── main.py                       # CLI giriş noktası
```

## Kurulum

```bash
uv sync
```

Gerekli ortam değişkenleri:
- `TAVILY_API_KEY` — Web arama için
- `GOOGLE_API_KEY` — Gemini modeli için (veya kullandığınız modelin API anahtarı)

## Kullanım

### Etkileşimli mod
```bash
uv run main.py
```

### Tek sorgu
```bash
uv run main.py "BIST 100 nedir"
```

## LLM Wiki Katmanları

FinWiki üç katmanı bilinçli olarak ayrı tutar:

1. **Raw sources** — `/raw/` altında tutulan raporlar, makaleler, KAP notları, CSV/PDF metinleri ve görseller. Bunlar kaynak gerçekliği kabul edilir ve ajan tarafından değiştirilmez.
2. **Wiki** — `/wiki/` altında LLM tarafından yazılan, güncellenen ve birbirine bağlanan Markdown bilgi tabanı.
3. **Schema** — `AGENTS.md`, agent promptları ve skill dosyaları. Ajanların wiki'yi nasıl yöneteceğini belirler.

Karpathy'nin LLM Wiki fikrindeki ana ayrım burada korunur: bilgi her sorguda ham kaynaklardan yeniden türetilmez; wiki'ye derlenir ve zamanla birleşerek güçlenir.

## Agent İş Akışı (Her Sorgu)

1. **Bul** — `search_wiki(...)`, `list_wiki_pages()` veya `read_wiki_page('index.md')` ile konu var mı bak.
2. **Araştır** — `internet_search(...)` ile güncel veri topla.
3. **Derle** — Çelişkileri, tarihleri, kaynakları ve kavram bağlantılarını sentezle.
4. **Yaz/Güncelle** — `upsert_wiki_page(...)` ile Markdown sayfası, index ve log'u birlikte güncelle.
5. **Manifest'e işle** — `register_source(...)` ile kaynak ve etkilenen sayfaları kaydet.
6. **Cevapla** — Kullanıcıya wiki sayfasını referans vererek cevap ver.

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
