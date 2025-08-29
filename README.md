# Week 4 — Flight Debug Lab (Complete Solution)

This repo is a **ready-to-run solution** matching your assignment. It includes:
- Synthetic data generator
- Production-ready automation (`main.py` + `src/*`)
- Optimizations (vectorization, batching, retries, parallel I/O, session reuse, metrics)
- Pytest tests
- Documentation scaffold (troubleshooting report + slides outline)

> Default config is **DRY_RUN** (no real API calls). You can safely run everything offline.

---

## 1) Quick Start

```bash
# 1) Clone the repo (or unzip the archive you downloaded)
cd Week4-FlightDebugLab-Solution

# 2) Create & activate a virtual env
python -m venv .venv
# Windows
. .venv/Scripts/activate
# macOS/Linux
# source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Generate synthetic data (200 rows by default)
python generate_sample_data.py 200 --blank-rate 0.03 --dup-rate 0.02 --invalid-iata-rate 0.02

# 5) Run the script (DRY RUN; uses ./data/reservations.csv by default)
python main.py --input data/reservations.csv --output ./output --dry-run --workers 8 --batch-size 25

# 6) Run tests
pytest -q
```

Outputs:
- `./output/invalid_rows.csv` — invalid or malformed records
- `./output/processed.csv` — cleaned & enriched data
- `./output/notifications.log` — simulated confirmation sends (dry run)
- Console logs include timing & counts

---

## 2) What’s Optimized

- **Pandas vectorization** replaces slow per-row loops
- **Batching** confirmation “sends” in groups (default 25)
- **Parallel I/O** for notifications using `ThreadPoolExecutor`
- **Retry** on transient failures with `tenacity`
- **HTTP session reuse** (if you point to a real API)
- **Logging & metrics** (duration per stage, success/error counts)

See `docs/troubleshooting.md` → “Optimization Summary” for details and code snippets.

---

## 3) Repo Structure

```
Week4-FlightDebugLab-Solution/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── generate_sample_data.py
├── main.py
├── src/
│   ├── __init__.py
│   ├── batching.py
│   ├── config.py
│   ├── data_loader.py
│   ├── logging_setup.py
│   ├── metrics.py
│   ├── notifier.py
│   ├── processor.py
│   ├── validators.py
├── data/
│   └── reservations.csv        # created by the generator
├── docs/
│   ├── troubleshooting.md      # fill SHAs after you commit
│   └── slides-outline.md
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_processor.py
│   └── test_validators.py
└── output/                     # results land here
```

---

## 4) Common Tasks

**Inject more edge cases:**

```bash
python generate_sample_data.py 500   --blank-rate 0.05   --dup-rate 0.04   --invalid-iata-rate 0.03
```

**Profile a run:**

```bash
python -X perf -m cProfile -o output/profile.pstats main.py --input data/reservations.csv --output output --dry-run
# Visualize with snakeviz (optional) or print stats:
python - <<'PY'
import pstats
p = pstats.Stats('output/profile.pstats')
p.sort_stats('cumtime').print_stats(30)
PY
```

**Real API mode (optional):**
- Copy `.env.example` to `.env`
- Set `API_URL`, `API_KEY`, and `DRY_RUN=false`
- Ensure your `.gitignore` keeps `.env` out of git

---

## 5) Part Mapping to Assignment

- **Part 0**: `generate_sample_data.py` + Data Assumptions in `docs/troubleshooting.md`
- **Part 1**: Fixes are reflected in code; see Error Table section in `docs/troubleshooting.md`
- **Part 2**: Optimizations implemented in `src/*` (vectorization, batching, parallel, retry)
- **Docs**: `docs/troubleshooting.md` + `docs/slides-outline.md`

Good luck — and happy debugging! 🛫
