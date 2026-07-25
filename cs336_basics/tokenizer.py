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
    text = Path(input_path).read_text(encoding="utf-8")
    text_segments = split_on_special_tokens(text, special_tokens)
    pretoken_counts = count_pretokens(text_segments)
    # 這行optimize要放外面
    pair_counts = count_adjacent_pairs(pretoken_counts)
    # TODO: Repeatedly count pairs, choose a pair, merge it, and update vocab.
    while len(vocab) < vocab_size:
        # 這行naive才在裡面，optimize要放外面
        # pair_counts = count_adjacent_pairs(pretoken_counts)
        pair = choose_pair_to_merge(pair_counts)

        if pair is None:
            break

        vocab[len(vocab)] = pair[0] + pair[1]
        merges.append(pair)
        # Old naive use this function
        # pretoken_counts = merge_pair_in_pretokens(pretoken_counts, pair)
        pretoken_counts, pair_counts = merge_pair_and_update_counts(
            pretoken_counts,
            pair_counts,
            pair,
        )
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
    if not pair_counts:
        return None

    return max(pair_counts, key=lambda pair: (pair_counts[pair], pair))
    # return max(pair_counts, key=lambda pair: pair_counts[pair])


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
    merged_counts = Counter()

    for pretoken, frequency in pretoken_counts.items():
        merged_tokens = []
        index = 0

        while index < len(pretoken):
            is_target_pair = index + 1 < len(pretoken) and (pretoken[index], pretoken[index + 1]) == pair

            if is_target_pair:
                merged_tokens.append(pair[0] + pair[1])
                #'lo'
                index += 2
            else:
                merged_tokens.append(pretoken[index])
                index += 1

        merged_counts[tuple(merged_tokens)] += frequency

    return merged_counts


def merge_pair_and_update_counts(
    pretoken_counts: Counter[tuple[bytes, ...]],
    pair_counts: Counter[tuple[bytes, bytes]],
    pair: tuple[bytes, bytes],
) -> tuple[Counter[tuple[bytes, ...]], Counter[tuple[bytes, bytes]]]:
    """Merge one pair and incrementally update the cached pair counts.

    Example:
        pretoken = (b"x", b"A", b"B", b"y")
        pair = (b"A", b"B")
        merged pretoken = (b"x", b"AB", b"y")

        Removed pair contributions: (b"x", b"A"), (b"A", b"B"), (b"B", b"y")
        Added pair contributions:   (b"x", b"AB"), (b"AB", b"y")

    Each count change must be weighted by the pre-token frequency. This helper
    will eventually replace the full ``count_adjacent_pairs`` rescan inside the
    training loop. It should return both updated Counters.
    """
    updated_pretoken_counts = Counter()
    updated_pair_counts = pair_counts.copy()

    for pretoken, frequency in pretoken_counts.items():
        has_target_pair = any(adjacent_pair == pair for adjacent_pair in zip(pretoken, pretoken[1:]))

        if not has_target_pair:
            updated_pretoken_counts[pretoken] += frequency
            continue

        # Remove this affected pre-token's old contribution from the cache.
        for old_pair in zip(pretoken, pretoken[1:]):
            updated_pair_counts[old_pair] -= frequency

            if updated_pair_counts[old_pair] == 0:
                del updated_pair_counts[old_pair]

        # Build this pre-token's merged replacement.
        merged_tokens = []
        index = 0

        while index < len(pretoken):
            is_target_pair = index + 1 < len(pretoken) and (pretoken[index], pretoken[index + 1]) == pair

            if is_target_pair:
                merged_tokens.append(pair[0] + pair[1])
                index += 2
            else:
                merged_tokens.append(pretoken[index])
                index += 1

        merged_pretoken = tuple(merged_tokens)
        updated_pretoken_counts[merged_pretoken] += frequency

        # Add this affected pre-token's new contribution to the cache.
        for new_pair in zip(merged_pretoken, merged_pretoken[1:]):
            updated_pair_counts[new_pair] += frequency

    return updated_pretoken_counts, updated_pair_counts
