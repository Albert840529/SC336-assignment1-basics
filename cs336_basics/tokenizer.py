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

    Pipeline:
        initialize_vocab -> split_on_special_tokens -> count_pretokens
        -> [count_adjacent_pairs -> choose_pair_to_merge
            -> merge_pair_in_pretokens] repeated

    The bracketed part repeats until ``vocab_size`` is reached or no pair
    remains. ``vocab`` maps token IDs to bytes; ``merges`` records the BPE
    merge order as ``(left, right)`` pairs.
    """
    vocab = initialize_vocab(special_tokens)
    merges: list[tuple[bytes, bytes]] = []

    # TODO: Build ``pretoken_counts`` from the input file.

    # TODO: Repeatedly count pairs, choose a pair, merge it, and update vocab.

    return vocab, merges


def initialize_vocab(special_tokens: list[str]) -> dict[int, bytes]:
    """Create the starting vocabulary.

    Example:
        bytes([0])   -> b"\\x00"  -> vocab[0]
        bytes([65])  -> b"A"       -> vocab[65]
        bytes([255]) -> b"\\xff"  -> vocab[255]

        special_tokens = ["<|endoftext|>"]
        vocab[256] = b"<|endoftext|>"

    Every possible byte occupies IDs 0 through 255. Special tokens are
    appended afterwards and never participate in BPE pair counting.
    """
    vocab = {i: bytes([i]) for i in range(256)}

    for token in special_tokens:
        vocab[len(vocab)] = token.encode("utf-8")

    return vocab


def split_on_special_tokens(text: str, special_tokens: list[str]) -> list[str]:
    """Split text at special tokens so BPE cannot merge across them.

    Example:
        text = "Hello<|endoftext|>World"
        special_tokens = ["<|endoftext|>"]
        result = ["Hello", "World"]

    The special token is removed from the training text here, but it remains
    in the vocabulary from ``initialize_vocab``. Regex escaping makes the
    ``|`` characters literal rather than regex syntax.
    """
    if not special_tokens:
        return [text]

    escaped_tokens = [re.escape(token) for token in special_tokens]
    pattern = "|".join(escaped_tokens)

    segments = re.split(pattern, text)

    return [segment for segment in segments if segment]


def count_pretokens(
    text_segments: list[str],
) -> Counter[tuple[bytes, ...]]:
    """Pre-tokenize text and count identical sequences of UTF-8 byte tokens.

    Example:
        text_segments = ["low and low"]
        PAT matches      "low", " and", " low"
        "low"           -> b"low" -> (b"l", b"o", b"w")
        " and"          -> b" and" -> (b" ", b"a", b"n", b"d")

        Returned Counter:
        {
            (b"l", b"o", b"w"): 1,
            (b" ", b"a", b"n", b"d"): 1,
            (b" ", b"l", b"o", b"w"): 1,
        }

    A leading space is intentionally kept when PAT includes it: it belongs to
    that pre-token. Non-ASCII text is first encoded as UTF-8 bytes.
    """
    count = Counter()
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
    """Count adjacent token pairs, weighted by pre-token frequency.

    Example:
        pretoken_counts = {
            (b"l", b"o", b"w"): 5,
            (b"l", b"o", b"w", b"e", b"r"): 2,
        }

        zip((b"l", b"o", b"w"), (b"o", b"w"))
        -> (b"l", b"o"), (b"o", b"w")

        Returned pair counts:
        (b"l", b"o"): 7  # 5 from "low" + 2 from "lower"
        (b"o", b"w"): 7
        (b"w", b"e"): 2
        (b"e", b"r"): 2

    Pairs never cross from one pre-token into the next.
    """
    pair_counts = Counter()

    for pretoken, frequency in pretoken_counts.items():
        for left, right in zip(pretoken, pretoken[1:]):
            pair_counts[(left, right)] += frequency
    return pair_counts


def choose_pair_to_merge(
    pair_counts: Counter[tuple[bytes, bytes]],
) -> tuple[bytes, bytes] | None:
    """Choose the highest-frequency pair.

    Example:
        pair_counts = {(b"A", b"B"): 4, (b"B", b"A"): 4}
        chosen pair = (b"B", b"A")

    When frequencies tie, choose the lexicographically greatest pair, matching
    Python's ``max`` behavior on tuples. Return ``None`` if no pair exists.
    """
    pass


def merge_pair_in_pretokens(
    pretoken_counts: Counter[tuple[bytes, ...]],
    pair: tuple[bytes, bytes],
) -> Counter[tuple[bytes, ...]]:
    """Replace every non-overlapping occurrence of ``pair`` in each pre-token.

    Example:
        pair = (b"l", b"o")
        (b"l", b"o", b"w") -> (b"lo", b"w")
        (b"l", b"o", b"l", b"o") -> (b"lo", b"lo")

    The frequency of each pre-token stays unchanged; only its token sequence
    changes. A merged token is formed with ``left + right``.
    """
    pass
