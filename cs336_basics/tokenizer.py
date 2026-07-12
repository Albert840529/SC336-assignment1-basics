"""Byte-level BPE tokenizer implementation for CS336 Assignment 1.

Implementation milestones for ``train_bpe``:

1. Define the function interface from the handout and its return types.
2. Initialize the vocabulary with all 256 single-byte tokens, then account for
   user-provided special tokens.
3. Read the corpus and pre-tokenize it without allowing merges across special
   token boundaries.
4. Represent each pre-token as UTF-8 bytes and retain its corpus frequency.
5. Count adjacent byte-token pairs across the pre-token representation.
6. Repeatedly choose the required pair, merge every valid occurrence, append
   the merge, and extend the vocabulary until ``vocab_size`` is reached.
7. Return the vocabulary and ordered merge list in the formats required by the
   adapter contract.
8. Connect the implementation through ``tests/adapters.py`` and pass the
   correctness tests before working on performance.
9. Profile the naïve version, then consider incremental pair-count updates and
   parallel pre-tokenization for larger corpora.

Start with correctness on a tiny corpus. Do not optimize multiple stages at
once; each optimization should preserve the same vocabulary and merge order.
"""

import regex as re
