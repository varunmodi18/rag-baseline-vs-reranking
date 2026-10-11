# RAG: Baseline vs. Re-Ranking

Varun Modi · Roll No. 2025202040 · 11 October 2026

## Setup and architectural comparison

The single corpus is NIST SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management (July 2025), 129 PDF pages and 389 unique chunks. The PDF and its normative clauses were inspected before selection. The exact source SHA-256 is recorded in data/source_manifest.json. Physical PDF page numbers are used below. Republished courtesy of the National Institute of Standards and Technology.

Page-aware PyMuPDF text is split at numbered sections, sentences, and a 230-wordpiece cap, with at most one-sentence overlap at token splits. Front matter is excluded. Chunks stay within a physical page; tables lose layout. Explicit assertions check the important rules and exceptions survive parsing and chunking. No model input is silently truncated.

The bi-encoder all-MiniLM-L6-v2 encodes query and passages independently. Attention-mask mean pooling and L2 normalization yield 384-dimensional vectors; passage embeddings are computed once and cached. An exact FAISS IndexFlatIP retrieves ten chunks by cosine-equivalent inner product; the first three feed Answer 1. This symmetric model needs no query prefix.

The cross-encoder ms-marco-MiniLM-L6-v2 jointly processes each query–passage pair, enabling self-attention across both token sequences. It scores precisely the same ten candidates in one batch, sorts raw relevance logits descending with dense-rank tie-breaking, and selects three for Answer 2. These logits are not calibrated probabilities. The same Qwen2.5-1.5B-Instruct model, prompt renderer, chat template, and greedy generation settings serve both answers; only ranked excerpts differ. Gold answers and evidence are kept out of inference.

The smaller Qwen2.5-0.5B pilot reversed explicit negations and produced contradictory answers. It was replaced by the 1.5B model; both pipelines were rerun with the same corpus, retrieval models, questions and prompt. Pilot records and the revision history are preserved separately from final statistics.

## Selected stress tests and ordinary controls

All 24 exploratory questions and outcomes are preserved. The final set was deliberately chosen after inspecting retrieval outcomes, including successes, unresolved cases, and controls. Evidence recovery means all indispensable evidence groups occur in the three excerpts; overlapping chunks with the same essential clause count as alternatives. This selected-case outcome is not an unbiased estimate of general performance.

| ID / category | Baseline → reranked evidence | Answer observation |
| --- | --- | --- |
| Q01 / exception | True → True | Answer 2 invents a 90-day rotation requirement. |
| Q02 / exception | False → True | Wrong six-character MFA minimum corrected to eight. |
| Q04 / negation | False → False | Correct no, but both rationales lack voice prohibition. |
| Q06 / keyword_trap | True → True | Answer 1 correct four; Answer 2 incorrectly says fifteen. |
| Q08 / negation | True → True | Answer 2 fixes AAL3 ban; equivalent evidence already present. |
| Q16 / control | False → True | Wrong 24-hour code timeout corrected to ten minutes. |
| Q19 / negation | False → False | Both say no without evidence; Answer 2 cites wrong clause. |
| Q24 / keyword_trap | True → True | Both say no; Answer 2 states whole-password rule, then truncates. |

<!-- pagebreak -->

## Verified failure case Q02

**Question:** Can an eight-character password be used when it is part of multi-factor authentication?

**Source-grounded reference:** Yes; single-factor requires 15 characters; MFA-only passwords can be at least eight.

| Indispensable evidence | PDF page | Dense rank | Cross rank |
| --- | --- | --- | --- |
| p025-ba87ffc2ee | 25 | 8 | 1 |

**Verified source excerpt:** Verifiers and CSPs SHALL require passwords that are used as a single-factor authentication mechanism to be a minimum of 15 characters in length. Verifiers and CSPs MAY allow passwords that are only used as part of multi-factor authentication processes to be shorter but SHALL require them to be a minimum of eight characters in length.

**Baseline context IDs:** p017-daf8ae22d3, p085-3d1b0d0bca, p049-5edd86be13

**Reranked context IDs:** p025-ba87ffc2ee, p049-5edd86be13, p085-3d1b0d0bca

**Actual Answer 1:** An eight-character password can be used when part of multi-factor authentication, but it must be part of a multi-factor authenticator. According to the NIST PDF excerpts, a multi-factor authenticator requires two factors to execute a single authentication event, and the password is one of the factors. The password must be at least six characters long to meet the requirement. Therefore, an eight-character password can be used if it is part of a multi-factor authenticator that meets the specified criteria.

**Actual Answer 2:** An eight-character password can be used when it is part of multi-factor authentication, as per the NIST guidelines. The key points are:

1. Verifiers and CSPs SHALL require passwords that are used as a single-factor authentication mechanism to be a minimum of 15 characters in length.
2. Verifiers and CSPs MAY allow passwords that are only used as part of multi-factor authentication processes to be shorter but SHALL require them to be a minimum of eight characters in length.
3. Verifiers and CSPs SHOULD permit a maximum password length of at least 64 characters.
4. Verifiers and CSPs SHOULD accept all printing ASCII characters and the space character in passwords.
5. Verifiers and CSPs SHOULD accept Unicode characters in passwords.
6. Verifiers and CSPs SHALL NOT impose other composition rules (e.g., requiring mixtures of different character types) for passwords.

The rule allows for shorter passwords in multi-factor authentication scenarios, provided they meet the minimum length requirement of eight characters.

**Assessment:** Answer 1 says yes but incorrectly makes six characters the required minimum and requires a multi-factor authenticator. It conflates the local activation-secret recommendation (SHOULD be six, SHALL be four) with the centrally verified MFA-password requirement. The actual central rule is absent from baseline top three. After the chunk moves 8 → 1, Answer 2 states the single-factor minimum of fifteen and the MFA-only minimum of eight, retaining MAY/SHALL distinctions. This corrects the mistaken rule and recovers the exception. Neither answer gives requested chunk/page citations, and Answer 2 exceeds the requested 130 words.

<!-- pagebreak -->

## Verified failure case Q16

**Question:** How long may an out-of-band authentication take, and can the same code be accepted twice?

**Source-grounded reference:** It is invalid unless completed within ten minutes; accept each secret once only during its validity period.

| Indispensable evidence | PDF page | Dense rank | Cross rank |
| --- | --- | --- | --- |
| p033-70431061f6 | 33 | 10 | 1 |

**Verified source excerpt:** In all cases, the authentication SHALL be considered invalid unless completed within 10 minutes. Verifiers SHALL accept a given authentication secret as valid only once during the validity period to provide replay resistance, as described in Sec. 3.2.7.

**Baseline context IDs:** p017-fee49e132c, p031-712d650583, p018-ab14635da6

**Reranked context IDs:** p033-70431061f6, p032-4fb0945ede, p029-c0b0976746

**Actual Answer 1:** The out-of-band authentication process described in the excerpts can take up to 24 hours at AAL2. The same code cannot be accepted twice; it must be unique for each authentication attempt.

**Actual Answer 2:** The out-of-band authentication process described in the excerpts can take up to 10 minutes, as indicated in the first excerpt. The same code cannot be accepted twice, as stated in the first excerpt: "Verifiers SHALL accept a given authentication secret as valid only once during the validity period to provide replay resistance."

**Assessment:** Baseline wrongly applies the AAL2 session-reauthentication timeout of twenty-four hours to a single out-of-band authentication transaction. Its one-use assertion is correct in the source document but unsupported by the three supplied excerpts. The indispensable verifier chunk contains both the ten-minute completion limit and acceptance only once during its validity period. It moves 10 → 1. Answer 2 explicitly recovers both conditions and fixes the timeout error. This is complete recovery of the required evidence and a substantive answer improvement. Neither answer provides the requested chunk/page IDs; referring to the first excerpt is less precise than the requested citation format.

<!-- pagebreak -->

## Measured retrieval latency

Intel Core i7-13620H, CPU only; four PyTorch threads and one FAISS thread. Warm models, one cross-encoder batch of ten. Seven fresh paired repetitions per final question, 56 samples total, using time.perf_counter. Query order is shuffled within repetitions. Dense time includes query tokenization/embedding/normalization, exact search, and selection. Reranking includes ten-pair tokenization/inference, sorting, and selection. Two-stage cost is the sum of the measured shared dense cost and measured reranker overhead in each repetition. Parsing, indexing, downloads, model loading, and LLM generation are excluded. CPU execution is synchronous.

| Query | Dense ms median | Reranker ms median | Two-stage ms median | Two-stage IQR |
| --- | --- | --- | --- | --- |
| Q01 | 4.00 | 167.15 | 170.93 | 168.58–176.48 |
| Q02 | 4.07 | 173.21 | 177.60 | 176.02–178.35 |
| Q04 | 3.81 | 160.70 | 164.50 | 162.23–168.89 |
| Q06 | 4.12 | 166.50 | 170.53 | 170.30–174.12 |
| Q08 | 4.18 | 175.07 | 178.71 | 176.87–179.92 |
| Q16 | 4.01 | 170.46 | 174.37 | 169.26–178.76 |
| Q19 | 3.91 | 154.12 | 158.01 | 156.10–163.90 |
| Q24 | 4.06 | 175.73 | 179.64 | 177.72–180.94 |

Actual LLM inference is measured separately: Answer 1 median 38.13 s, Answer 2 median 44.60 s, one uncached call per answer. Tokenization is outside these LLM timings. Prompt lengths and generated token counts differ with context; these generation times are descriptive, not a retrieval speed comparison. Raw timings and per-query p25/p75 values are saved.

## Why not cross-encode the entire corpus?

For N=389 chunks, a full cross-encoder scan requires N joint query–passage forward passes per question versus ten in this experiment (38.9× as many pairs, a workload comparison rather than a measured speedup). Passage-only cross-encoder relevance cannot be cached for arbitrary queries because token interactions depend on the query. Attention and padded sequence length add further costs. Batching helps utilization but does not eliminate the per-pair computation.

The dense method caches N document embeddings. IndexFlatIP is an exact scan, requiring O(Nd) dot-product work per query (d=384), plus top-k selection and the query encoder; it is not constant-time search. Approximate indexes can reduce search work at the cost of recall, but none was tested here. Restricting expensive joint scoring to ten candidates is useful only when initial retrieval includes the needed evidence. Evidence outside the top ten cannot be rescued, and queries needing multiple passages require recovery of every essential clause.

## Interpretation and limits

There were 0 queries with exact score ties in the 24-question exploration. Evidence recovery was unchanged for 22 questions; Q04 remained unresolved (the voice prohibition shifted 8 → 9), and Q19 needed evidence absent from the candidate set. Retrieval promotions and answer improvements are assessed separately. The compact CPU LLM can misstate or omit rules even with better evidence. It often fails the requested chunk/page citation format and sometimes exceeds the requested 130 words; actual outputs are preserved. Q01 and Q06 show answer regressions despite complete evidence in both contexts. Q19 Answer 1 and Q24 Answer 2 hit the 240-token generation cap and end incompletely. Q19 Answer 2 cites a real mistyping-allowance chunk that does not support its hint-ban claim. Exact score ties, retrieval ties, regressions, and unrecovered evidence are recorded in the exploratory artifacts. Conclusions apply to this frozen PDF, chunking, models, and selected questions. No training or baseline weakening was used. Integrity assertions passed in the executed notebook; report judgments were checked against the original PDF and saved answers.

## Sources

NIST source: https://doi.org/10.6028/NIST.SP.800-63B-4 . Model documentation: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 ; https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2 ; https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct . Exact revisions and tested packages are in the experiment manifest. GitHub: https://github.com/varunmodi18/rag-baseline-vs-reranking .
