<div align="center">

<img src="https://img.shields.io/badge/Python-3.7+-3776AB?style=flat-square&logo=python" />
<img src="https://img.shields.io/badge/Seed1.5--VL-ByteDance-E31937?style=flat-square" />
<img src="https://img.shields.io/badge/OpenCV-cv2-5C3EE8?style=flat-square&logo=opencv" />
<img src="https://img.shields.io/badge/Concurrency-16_workers-green?style=flat-square" />
<img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />

# Smart Short Video Ecosystem Analyzer

**Five-pass multimodal analysis and weighted ecosystem scoring for short-form video platforms**

[Quick Start](#quick-start) · [Methodology](#innovation--methodology) · [Results](#empirical-results) · [Report Bug](https://github.com/devinlovekoala/smart-video-ecosystem/issues)

</div>

---

## Overview

This system performs deep multi-dimensional analysis of short videos — covering content semantics, visual style, community governance signals, and distribution potential — and produces structured labels plus a quantitative ecosystem fitness score.

The core insight is that a single generic prompt cannot reliably capture all signals needed for platform-level decision making. Instead, the pipeline decomposes video understanding into **five specialized analytical passes**, runs them concurrently against ByteDance's open-source **Seed1.5-VL** multimodal model, and synthesizes results into a 12-dimension label set and a weighted [0, 1] fitness score — with **zero redundant inference calls** through result caching.

Designed to support content recommendation, platform governance, and creator guidance at scale on short-video platforms.

---

## Innovation & Methodology

### Five-Pass Multimodal Analysis

Rather than relying on a single generic prompt, video understanding is decomposed into five specialized passes, each backed by a purpose-designed prompt template and running concurrently via `ThreadPoolExecutor`:

| Pass | Prompt Template | What It Captures |
|------|----------------|-----------------|
| Content Understanding | `content_understanding.txt` | Theme, narrative, information density, audience profiling |
| Visual Style Recognition | `visual_style.txt` | Art style (realistic / cartoon / 3D / retro / cyberpunk / film-grain), color temperature, composition, production tier |
| Community Atmosphere | `community_atmosphere.txt` | Emotional valence, value orientation, health score, risk signals |
| Distribution Features | `distribution_features.txt` | Viral triggers, engagement drivers, timeliness, scene matching |
| Multimodal Feature Extraction | `multimodal_features.txt` | Cross-modal fusion: visual, motion, temporal, semantic, emotional |

All downstream modules reuse the cached inference results — no redundant API calls regardless of how many analysis steps follow.

### 12-Dimension Structured Label System

`ContentLabelingSystem` synthesizes the five passes into a normalized, deduplicated label set across 12 semantic dimensions that map directly to the slot structure of downstream recommendation, search, and moderation systems:

```
Content:      content_type · emotion · scene
Visual:       visual_style · color_tone · production_quality
User:         target_audience · interaction_type
Distribution: distribution · distribution_scene
Governance:   community_impact · content_safety
```

### Weighted Ecosystem Fitness Score

`DouyinEcosystemAnalyzer` computes a single [0, 1] fitness score via a five-factor weighted model:

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Viral Potential | 25% | Primary driver of platform growth |
| Engagement Potential | 20% | Retention and interaction signal |
| Content Quality | 20% | Production standard and watch-completion proxy |
| Platform Fit | 20% | Alignment with platform audience and norms |
| Audience Appeal | 15% | Target-demographic resonance |

Each factor is scored via three-tier keyword matching (high / medium / low signal) applied to VLM analysis text, then blended 50/50 with an AI-assessed quality score on a 0–10 scale. Final score drives a four-tier recommendation:

| Score | Tier |
|-------|------|
| ≥ 0.75 | Strongly Recommended |
| 0.65 – 0.74 | Recommended |
| 0.55 – 0.64 | Needs Optimization |
| < 0.55 | Not Recommended |

### Adaptive Keyframe Sampling

Frame extraction uses an EVEN_INTERVAL strategy that adapts to video duration, sampling up to **30 representative keyframes** per video. Images are resized and Base64-encoded before submission, balancing inference accuracy against API payload size.

### Content-Type-Aware Scoring Profiles

Scoring profiles are parameterized per content type. Comedy and drama content receives higher weight on viral potential triggers (humor, surprise, novelty); educational and craft content is weighted more heavily on engagement potential (knowledge, skill demonstration). This avoids a universal scoring bias across genres.

---

## Architecture

```
smart_videos/
├── smart_videos.ipynb              orchestration notebook (6-step pipeline)
├── video_analyzer.py               core VLM inference engine
│   ├── frame extraction            EVEN_INTERVAL, up to 30 frames
│   ├── concurrent batch analysis   ThreadPoolExecutor, 16 workers
│   └── 5-pass per-video analysis
├── content_labeling_system.py      12-dimension label synthesizer
├── douyin_ecosystem_analyzer.py    weighted ecosystem scorer
├── prompt/                         prompt templates (5 types + fallback)
├── download_videos/                input video directory
└── results/
    ├── video_analysis_results.json raw VLM outputs
    ├── video_labels.json           structured label data
    ├── ecosystem_scores.json       per-video fitness scores
    └── analysis_report.json        aggregated summary report
```

**Processing flow:**

```
Video files
    │
    ▼
Frame extraction (EVEN_INTERVAL, ≤30 frames, Base64)
    │
    ▼
Concurrent 5-pass VLM inference (ThreadPoolExecutor, 16 workers)
    │              └── results cached, reused downstream
    ├── Label synthesis     (ContentLabelingSystem)
    └── Ecosystem scoring   (DouyinEcosystemAnalyzer)
    │
    ▼
JSON report generation → results/
```

---

## Empirical Results

Evaluation on **10 real Douyin short videos** across 7 content categories.

### Pipeline Reliability

| Metric | Value |
|--------|-------|
| Analysis success rate | **100%** (10/10) |
| Label generation success rate | **100%** (10/10) |
| Ecosystem scoring success rate | **100%** (10/10) |

### Ecosystem Score Distribution

| Metric | Value |
|--------|-------|
| Average ecosystem score | **0.641** |
| Highest score | **0.81** — Comedy Drama |
| Lowest score | **0.51** — Game footage (no commentary) |
| Strongly Recommended (≥ 0.75) | **2 / 10** (20%) |
| Recommended or above (≥ 0.65) | **6 / 10** (60%) |

### Per-Video Scores

| Video | Content Type | Viral | Engage | Quality | Fit | Audience | **Score** | Tier |
|-------|-------------|-------|--------|---------|-----|----------|-----------|------|
| Recording 20-55-49 | Comedy Drama | 0.90 | 0.90 | 0.65 | 0.70 | 0.90 | **0.81** | Strongly Recommended |
| Recording 21-06-25 | Variety Show | 0.80 | 0.80 | 0.65 | 0.80 | 1.00 | **0.80** | Strongly Recommended |
| Recording 21-05-17 | Daily Vlog | 0.70 | 0.70 | 0.65 | 0.80 | 1.00 | **0.76** | Recommended |
| Recording 21-07-23 | Handcraft/DIY | 0.60 | 0.60 | 0.60 | 0.70 | 0.80 | **0.65** | Recommended |
| Recording 21-03-54 | Music | 0.80 | 0.30 | 0.60 | 0.60 | 0.90 | **0.64** | Recommended |
| Recording 21-00-30 | Sports | 0.60 | 0.60 | 0.65 | 0.60 | 0.80 | **0.64** | Recommended |
| Recording 20-54-10 | Game | 0.30 | 0.30 | 0.60 | 0.80 | 0.90 | **0.55** | Needs Optimization |
| Recording 20-53-33 | Game | 0.30 | 0.30 | 0.40 | 0.80 | 1.00 | **0.53** | Needs Optimization |
| Recording 20-52-43 | Game | 0.30 | 0.30 | 0.65 | 0.60 | 0.90 | **0.52** | Needs Optimization |
| Recording 20-57-58 | Game | 0.30 | 0.30 | 0.65 | 0.60 | 0.80 | **0.51** | Needs Optimization |

### Dimension Averages

| Dimension | Average | Note |
|-----------|---------|------|
| Audience Appeal | **0.90** | Strongest — VLM accurately identifies target demographics |
| Platform Fit | **0.71** | Most stable — range 0.60–0.80 |
| Content Quality | 0.62 | |
| Viral Potential | 0.61 | |
| Engagement Potential | 0.59 | |

### Key Finding: Content-Format Gap in Game Content

Game / esports footage scores uniformly low on viral potential (0.30) and engagement potential (0.30) despite high audience appeal (0.80–1.00). The audience exists, but raw footage without commentary or narration does not engage them. This pattern is consistent across all four game videos and suggests a systematic content-format gap, not a content-quality issue — a distinction that a single-pass generic scoring system would miss.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API access

Set your API key as an environment variable:

```bash
export VOLCENGINE_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here
```

### 3. Add videos

Place video files in `download_videos/`. Supported formats: `.webm` · `.mp4` · `.avi` · `.mov` · `.mkv`

### 4. Run the pipeline

Open `smart_videos.ipynb` and execute cells in order:

```
1. Import modules
2. Scan video directory
3. Run 5-pass VLM inference        ← main computation step
4. Generate structured labels
5. Compute ecosystem scores
6. Export analysis report
```

### 5. Review results

```
results/
├── video_analysis_results.json    raw VLM outputs per video per dimension
├── video_labels.json              12-dimension structured labels
├── ecosystem_scores.json          per-video fitness scores with dimension breakdown
└── analysis_report.json           summary statistics + top-video rankings
```

---

## Configuration

```python
# Concurrency
analyzer = VideoAnalyzer(max_workers=16)

# Frame sampling
analyzer = VideoAnalyzer(max_frames=30)

# Scoring weights (douyin_ecosystem_analyzer.py)
weights = {
    "viral_potential":    0.25,
    "engagement_potential": 0.20,
    "content_quality":    0.20,
    "platform_fit":       0.20,
    "audience_appeal":    0.15,
}
```

---

## Application Scenarios

**Content recommendation** — Feed ecosystem scores and structured labels directly into ranking and retrieval systems.

**Platform governance** — Use community atmosphere and content safety labels for automated moderation triage.

**Creator guidance** — Surface actionable optimization suggestions for low-scoring videos (e.g., "add commentary to increase engagement potential for game content").

**Trend analysis** — Aggregate label distributions over time to detect emerging content categories.

**Quality control** — Automate quality gating for user-generated content based on production quality scores.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Multimodal foundation model | Seed1.5-VL (ByteDance open-source VLM) |
| Inference API | Volcengine (OpenAI-compatible SDK) |
| Video processing | OpenCV (cv2) |
| Numerical processing | NumPy, scikit-learn |
| Concurrency | Python `ThreadPoolExecutor` (16 workers) |
| Runtime | Python 3.7+, Jupyter |
| Output | JSON (UTF-8, full CJK support) |

---

## License

MIT License
