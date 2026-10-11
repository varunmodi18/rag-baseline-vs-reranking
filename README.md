# RAG Assignment: Baseline vs. Re-Ranking

Varun Modi — Roll No. 2025202040. Submission deadline: 19 October 2026.

A reproducible paired experiment over one PDF: **NIST SP 800-63B-4, July 2025**. The primary implementation is `RAG_Baseline_vs_Reranking.ipynb`. Both pipelines share the same ten dense candidates, the same corpus, and the same LLM prompt contract. Only the order of the three selected contexts changes.

The verified cases are Q02 (MFA password minimum: essential evidence **8 → 1**, correcting a mistaken six-character minimum to eight) and Q16 (out-of-band code validity: **10 → 1**, correcting a mistaken 24-hour limit to ten minutes and recovering one-use acceptance). The final set has eight questions and 56 fresh timing samples. The four-page report includes the complete actual answer comparisons.

Observed limits include answer regressions on password rotation and local PIN length despite adequate evidence, an unrecovered voice-biometric prohibition, and a password-hint rule outside the initial ten candidates. Only two of sixteen answers supplied chunk IDs; one cited an irrelevant clause. Two outputs reached the 240-token cap. These failures are preserved and assessed against the PDF; the successful selected cases do not establish universal superiority.

## Setup and execution

Use Linux x86_64, Python **3.11**, and a CPU with about 5 GB of additional available RAM. No GPU, API key, or paid model account is needed. Allow about 6 GB of disk for the environment/model downloads; allow additional disk for package-manager caches. The first run requires internet access to PyPI, the PyTorch CPU wheel server, and Hugging Face. Download/model-loading time is excluded from retrieval measurements.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python run_notebook.py
```

Run from the repository root. The execution helper registers a project-local kernel under `.cache/jupyter` and executes all notebook cells from a clean kernel. For interactive use, install JupyterLab separately, register this virtual environment as a kernel, restart it, and run all cells. The submitted notebook contains a clean-kernel execution. The helper uses localhost kernel sockets; restricted sandboxes must permit loopback connections. Running it again performs genuine model inference and overwrites final artifacts; preserve a copy if comparing runs. Latency varies with hardware/load. Greedy CPU inference reduces randomness but bitwise reproducibility across package versions/hardware is not promised.

The notebook resolves exact model revisions from `data/model_revisions.json`. It downloads them using Transformers when the optional `.cache/models/` snapshots are absent. No credentials are required for these public models. If your institution requires an authenticated Hugging Face connection, configure its credentials externally; do not put tokens into notebook cells or tracked files.

## Source and chunking

The PDF is redistributed with attribution in `data/ATTRIBUTION.md`. Its official acquisition URL, release date, SHA-256, and redistribution conditions are in `data/source_manifest.json`. If missing, the notebook downloads it and verifies its exact hash. Changing source content triggers an assertion requiring review and a complete rerun. Physical PDF page numbers are used for citations; they differ from printed body-page numbers.

Page-aware PyMuPDF extraction removes exact running headers/footer and repairs line-wrap hyphens. Front matter is saved but excluded from retrieval. Chunks preserve numbered sections and sentence boundaries, cap at 230 dense-tokenizer wordpieces, and use at most one sentence of overlap at token splits. Pages form hard boundaries. Important normative clauses are asserted to survive extraction and chunking. Tables/figures can lose visual layout, and page/long-list splits can separate related clauses; these are limitations.

## Models and paired comparison

- Dense bi-encoder: `sentence-transformers/all-MiniLM-L6-v2`, attention-mask mean pooling and L2-normalized 384-dimensional vectors; symmetric encoding without query prefixes.
- Dense index: FAISS `IndexFlatIP`, exact inner product of normalized vectors (cosine similarity), ten unique candidates.
- Cross-encoder: `cross-encoder/ms-marco-MiniLM-L6-v2`, raw relevance logits over exactly those ten pairs, one batch of ten; deterministic ties by dense rank. Scores are not calibrated probabilities.
- LLM: `Qwen/Qwen2.5-1.5B-Instruct`, CPU bfloat16, greedy decoding, one shared chat/prompt template. The compact model has limited reasoning/citation reliability; observed answer defects are reported rather than corrected manually.

The smaller Qwen2.5-0.5B pilot produced contradictory rule statements; its complete records are retained in `results/pilot_qwen_0_5b/` and the change is documented in `results/revision_history.md`. Final statistics use only the larger model.

Gold answers and evidence labels are stored separately and enter only post-generation evaluation. The final questions were intentionally selected after exploring retrieval failures; this is a stress test, not an unbiased performance estimate. The reranker cannot recover evidence outside the initial top ten.

## Artifacts

- `data/`: the one source PDF, source manifest, extracted pages, stable chunks, normalized vectors/index, model revisions, and attribution.
- `results/query_pool.json` and `exploratory_results.jsonl`: all 24 questions, source-grounded gold records, and exploration outcomes.
- `results/final_queries.json`: configuration frozen before the complete final run.
- `results/final_results.jsonl`: all ten ranks/scores in both orders, complete prompts, actual answers, context IDs, and individual generation timings.
- `results/query_evidence.json`: gold passages/pages, evidence recovery, and rank shifts, evaluated separately from inference.
- `results/experiment_manifest.json`, `prompt_contract.json`, `validation.json`: exact configuration, model revisions, environment, and integrity checks.
- `results/latency_samples.csv`, `latency_summary.csv`, `timing_methodology.json`: seven actual warm repetitions per final question, raw measurements, medians/IQR, and explicit timing boundaries. Two-stage time is shared measured retrieval plus measured reranking.
- `report.md` and `report.pdf`: concise findings with source/answer comparisons, measured latency, architectures, and scaling.

Model caches, virtual environments, credentials, and weights are excluded by `.gitignore`. The original assignment instructions and implementation plan remain in the parent workspace; they are not part of the retrieval corpus.

## Regenerate report

The notebook contains the report-generation cells. They use saved final results and a checked qualitative assessment file to produce Markdown and PDF. Review answers against the PDF if model/configuration changes; the original human assessments must not be treated as valid for changed outputs.
