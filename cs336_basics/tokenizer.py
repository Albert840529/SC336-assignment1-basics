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

from collections import Counter
from pathlib import Path

import regex as re


PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""


def train_bpe(
    input_path: str | Path,
    vocab_size: int,
    special_tokens: list[str],
) -> tuple[dict[int, bytes], list[tuple[bytes, bytes]]]:
    """Train a byte-level BPE tokenizer.

    Milestone order:

    1. Initialize the vocabulary with all 256 single-byte tokens.
    2. Add special tokens to the vocabulary.
    3. Read the corpus and split it on special tokens.
    4. Pre-tokenize each non-special segment with the GPT-2 regex.
    5. Convert each pre-token into a tuple of byte tokens and count frequency.
    6. Repeatedly:
       - count adjacent pairs,
       - choose the most frequent pair with the required tie-break,
       - merge that pair everywhere,
       - append the merge and extend the vocabulary.
    7. Stop when ``len(vocab) == vocab_size`` or no pair remains.

    Returns:
        vocab:
            Mapping from token ID to token bytes.
        merges:
            Ordered list of merge operations. Each item is ``(left, right)``.
    """
    vocab = initialize_vocab(special_tokens)
    merges: list[tuple[bytes, bytes]] = []

    # TODO: Build ``pretoken_counts`` from the input file.

    # TODO: Repeatedly count pairs, choose a pair, merge it, and update vocab.

    return vocab, merges


def initialize_vocab(special_tokens: list[str]) -> dict[int, bytes]:
    """Create the starting vocabulary.

    Byte-level BPE starts with one token for each possible byte value:
    ``0`` through ``255``. Special tokens are appended after those byte tokens.
    """
    # Example trace:
    # range(256) gives integer byte values:
    # 0, 1, 2, ..., 65, ..., 255
    #
    # bytes([0])  -> b"\x00"
    # bytes([65]) -> b"A"
    # bytes([255]) -> b"\xff"
    #
    # After this comprehension:
    # vocab[0]   = b"\x00"
    # vocab[65]  = b"A"
    # vocab[255] = b"\xff"
    vocab = {i: bytes([i]) for i in range(256)}

    # Example with special_tokens = ["<|endoftext|>"]:
    # token                     = "<|endoftext|>"
    # token.encode("utf-8")     = b"<|endoftext|>"
    # len(vocab) before insert  = 256
    # vocab[256]                = b"<|endoftext|>"
    #
    # Special tokens get fixed IDs, but they are not used when counting BPE
    # merge statistics.
    for token in special_tokens:
        vocab[len(vocab)] = token.encode("utf-8")

    return vocab


def split_on_special_tokens(text: str, special_tokens: list[str]) -> list[str]:
    """Split text at special tokens so BPE cannot merge across them.

    Special tokens act as hard boundaries during training. They should not
    contribute to pair counts.
    """
    if not special_tokens:
        return [text]

    # Example trace:
    # text           = "Hello<|endoftext|>World again"
    # special_tokens = ["<|endoftext|>"]
    # pattern        = "<\\|endoftext\\|>"
    # segments       = ["Hello", "World again"]
    #
    # The special token is removed from training text here. It is still added
    # to the vocabulary by ``initialize_vocab``.

    # Escape special tokens so regex treats characters like "|" literally.
    escaped_tokens = [re.escape(token) for token in special_tokens]
    pattern = "|".join(escaped_tokens)

    segments = re.split(pattern, text)

    return [segment for segment in segments if segment]  # remove empty strings


def count_pretokens(
    text_segments: list[str],
) -> Counter[tuple[bytes, ...]]:
    """Pre-tokenize text segments and count each UTF-8 byte-token sequence.

    Each key should be a tuple of bytes objects, for example:
    ``"low" -> (b"l", b"o", b"w")``.
    """
    count = Counter()

    # Example trace 1:
    # text_segments = ["low and lower"]
    # segment       = "low and lower"
    # match.group() = "low"
    # pretoken      = "low"
    # token_bytes   = b"low"
    # byte_tuple    = (b"l", b"o", b"w")
    # count[(b"l", b"o", b"w")] += 1
    #
    # Later in the same segment:
    # match.group() = " and"
    # pretoken      = " and"
    # token_bytes   = b" and"
    # byte_tuple    = (b" ", b"a", b"n", b"d")
    #
    # Example trace 2:
    # text_segments = ["some text that i'll pre-tokenize"]
    # match.group() values from PAT:
    # "some", " text", " that", " i", "'ll", " pre", "-", "tokenize"
    #
    # Example trace 3:
    # pretoken      = "你好"
    # token_bytes   = b"\xe4\xbd\xa0\xe5\xa5\xbd"
    # byte_tuple    = (b"\xe4", b"\xbd", b"\xa0", b"\xe5", b"\xa5", b"\xbd")
    for segment in text_segments:
        for match in re.finditer(PAT, segment):
            pretoken = match.group()
            token_bytes = pretoken.encode("utf-8")
            byte_tuple = tuple(bytes([b]) for b in token_bytes)
            count[byte_tuple] += 1
    return count


def count_adjacent_pairs(
    pretoken_counts: Counter[tuple[bytes, ...]],
) -> Counter[tuple[bytes, bytes]]:
    """Count adjacent token pairs, weighted by pre-token frequency."""
    pass


def choose_pair_to_merge(
    pair_counts: Counter[tuple[bytes, bytes]],
) -> tuple[bytes, bytes] | None:
    """Choose the highest-frequency pair.

    If multiple pairs have the same frequency, choose the lexicographically
    greatest pair, matching Python's ``max`` behavior on tuples.
    """
    pass


def merge_pair_in_pretokens(
    pretoken_counts: Counter[tuple[bytes, ...]],
    pair: tuple[bytes, bytes],
) -> Counter[tuple[bytes, ...]]:
    """Replace every non-overlapping occurrence of ``pair`` in each pre-token."""
    pass
