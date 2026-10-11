## Pilot and final configuration

The first fully executed pilot used Qwen2.5-0.5B-Instruct for all eight paired questions. It reversed the no-periodic-password-change rule despite available evidence; its Q02 reranked answer contradicted itself about eight versus fifteen characters. All raw pilot answers, prompts, timings and its original manifest are preserved in pilot_qwen_0_5b/. These are excluded from final statistics.

The final configuration changes only the generator to Qwen2.5-1.5B-Instruct, chosen to improve instruction/negation handling within CPU memory limits. The source PDF, 389 chunks, dense/cross models, retrieval procedure, question set, prompt template and greedy generation settings remain unchanged. Both pipelines are rerun consistently; final timings are new actual operations. The complete final configuration is frozen before the final paired run, and the final notebook is executed top to bottom from a clean kernel.
