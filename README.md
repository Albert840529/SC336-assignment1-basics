# CS336 Spring 2025 Assignment 1: Basics

This repository is my personal learning workspace for Stanford CS336 Assignment 1. The goal is to build a small transformer-style implementation step by step, using the assignment handout and the provided tests as the main guide.

## Purpose
This project is intended to help me:
- understand the core building blocks of a simple language model
- implement the assignment incrementally rather than all at once
- keep a clear record of progress, learning points, and next steps

## Project structure
- [cs336_basics](./cs336_basics): implementation scaffold for the assignment
- [tests](./tests): test suite and adapter functions that define the expected behavior
- [PROGRESS.md](./PROGRESS.md): current study log and milestone tracker
- [cs336_assignment1_basics.pdf](./cs336_assignment1_basics.pdf): official assignment handout

## Setup
We manage the environment with `uv` to ensure reproducibility and ease of use.

### Environment
Install `uv` from the official guide or with `pip install uv` / `brew install uv`.

You can run code in the repository with:
```sh
uv run <python_file_path>
```

### Run unit tests
```sh
uv run pytest
```

Initially, the tests will fail with `NotImplementedError`s. The main implementation checkpoints are listed in [tests/adapters.py](./tests/adapters.py).

### Download data
If needed for later parts of the assignment, the repository instructions include downloading TinyStories and a sample of OpenWebText:

```sh
mkdir -p data
cd data

wget https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStoriesV2-GPT4-train.txt
wget https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStoriesV2-GPT4-valid.txt

wget https://huggingface.co/datasets/stanford-cs336/owt-sample/resolve/main/owt_train.txt.gz
gunzip owt_train.txt.gz
wget https://huggingface.co/datasets/stanford-cs336/owt-sample/resolve/main/owt_valid.txt.gz
gunzip owt_valid.txt.gz

cd ..
```

## Progress tracker
For the current milestone plan and status, see [PROGRESS.md](./PROGRESS.md).

