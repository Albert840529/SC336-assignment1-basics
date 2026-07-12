# CS336 Assignment 1 Progress Tracker

This document records completed work, concepts learned, test checkpoints, and the next study step. A task is checked only after its deliverable has been completed or its relevant tests pass.

## Current status

- Repository setup is complete.
- `uv` is installed and the project environment has been synchronized.
- The initial test suite runs successfully and reports 46 expected `NotImplementedError` failures.
- No assignment implementation has started yet.
- Next study step: byte-level subword tokenization and BPE training.

## Assignment deliverables

The official submission consists of two main artifacts:

- `writeup.pdf`: typeset answers to the written and experimental questions.
- `code.zip`: the implementation produced by `make_submission.sh`.

For this self-study repository, the project should also preserve a clear implementation history, experiment records, learning notes, and reproducible test commands.

## Handout roadmap

### 1. Assignment Overview

- [x] Read the repository structure and assignment workflow
- [x] Install `uv` and synchronize the environment
- [x] Run the complete test suite to establish a baseline
- [x] Review the implementation, experiment, and submission expectations

Learning goal: understand how the handout, implementation package, test adapters, tests, written responses, and experiments fit together.

### 2. Byte-Pair Encoding Tokenizer

- [x] Understand Unicode characters and code points (`unicode1`)
- [x] Understand UTF-8 byte encoding and invalid byte sequences (`unicode2`)
- [ ] Understand byte-level subword tokenization
- [ ] Implement and test BPE training (`train_bpe`)
- [ ] Train and inspect TinyStories and OpenWebText tokenizers
- [ ] Implement and test tokenizer encoding and decoding (`tokenizer`)
- [ ] Measure compression ratio, throughput, and memory behavior
- [ ] Encode the training and validation datasets

Learning goal: understand how arbitrary text becomes a compact sequence of integer token IDs without an out-of-vocabulary problem.

### 3. Transformer Language Model Architecture

- [ ] Understand tensor shapes, batching, and `einsum`
- [ ] Implement Linear and Embedding modules
- [ ] Implement RMSNorm and the SwiGLU feed-forward network
- [ ] Implement Rotary Positional Embeddings
- [ ] Implement numerically stable softmax
- [ ] Implement scaled dot-product attention and causal multi-head self-attention
- [ ] Assemble and test a pre-norm Transformer block
- [ ] Assemble and test the complete Transformer language model
- [ ] Complete Transformer parameter, memory, and FLOP accounting

Learning goal: understand the data flow, tensor shapes, mathematical operations, and resource costs of a decoder-only Transformer.

### 4. Training a Transformer LM

- [ ] Implement numerically stable cross-entropy
- [ ] Study SGD behavior and learning-rate sensitivity
- [ ] Implement AdamW
- [ ] Complete AdamW memory and compute accounting
- [ ] Implement cosine learning-rate scheduling with warmup
- [ ] Implement gradient clipping

Learning goal: understand how loss, gradients, optimizer state, learning-rate schedules, and stability controls turn predictions into parameter updates.

### 5. Training Loop

- [ ] Implement batched next-token data loading
- [ ] Implement checkpoint saving and loading
- [ ] Build a configurable, memory-efficient training loop

Learning goal: connect tokenized data, the model, loss, optimizer, evaluation, and checkpointing into a reproducible training system.

### 6. Generating Text

- [ ] Implement autoregressive decoding
- [ ] Support temperature and top-p sampling
- [ ] Stop generation at the end-of-text token

Learning goal: understand how next-token probabilities become generated text and how sampling choices affect output quality.

### 7. Experiments

- [ ] Create experiment logging with step, time, training loss, and validation loss
- [ ] Train and tune a TinyStories model
- [ ] Study learning-rate and batch-size effects
- [ ] Generate and analyze model samples
- [ ] Compare RMSNorm, pre-norm/post-norm, RoPE/NoPE, and SwiGLU/SiLU variants
- [ ] Run the OpenWebText experiment when compute resources permit
- [ ] Consider the optional leaderboard modification

Learning goal: use controlled experiments and learning curves to explain why architectural and optimization choices matter.

## Test strategy

Run only the test associated with the current component during development. Run the complete suite at major milestones.

Examples:

```sh
uv run pytest -k test_linear
uv run pytest tests/test_train_bpe.py
uv run pytest tests/test_tokenizer.py
uv run pytest
```

## Learning log

### 2026-06-27 - Environment and baseline

Completed:

- Installed `uv` with Homebrew.
- Synchronized the project from `pyproject.toml` and `uv.lock`.
- Ran the full test suite from the repository root.
- Confirmed that the test infrastructure works and that the 46 failures are expected unimplemented adapters.

Learned:

- `uv sync` must be run inside `SC336-Assignment1`, where `pyproject.toml` is located.
- `uv run` executes commands in the project-managed Python environment rather than the base Anaconda environment.
- The initial failing suite is a baseline, not evidence of 46 separate bugs.

Next:

- Work through `unicode2` and compare Unicode encodings.

### 2026-07-03 - Unicode characters and code points

Completed:

- Investigated the NUL character with `chr(0)`, `repr()`, `print()`, and UTF-8 encoding.
- Completed the three written responses for `unicode1`.

Learned:

- Unicode code points can represent invisible control characters.
- `repr()` exposes an inspectable escape sequence even when printed output has no visible glyph.
- An invisible character can still occupy a position in a string and produce encoded bytes.

### 2026-07-12 - Unicode encodings and UTF-8 bytes

Completed:

- Compared UTF-8, UTF-16, and UTF-32 encodings on simple text and emoji examples.
- Traced how `"你"` maps from Unicode code point `U+4F60` to UTF-8 bytes `[228, 189, 160]`.
- Completed the three written responses for `unicode2`.

Learned:

- Unicode code points are abstract character numbers; encodings turn them into bytes.
- UTF-8 uses leading-bit patterns to distinguish one-byte characters, multi-byte starts, and continuation bytes.
- Not every byte sequence is valid UTF-8; for example, `0xff` is not a legal UTF-8 start byte.
