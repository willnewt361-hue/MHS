#!/usr/bin/env python3
"""
password_generator.py

Generate memorable but strong passwords derived from a person's name(s).
- Uses the secrets module for cryptographic randomness.
- Ensures at least one uppercase, lowercase, digit, and symbol.
- Prints entropy estimate for each candidate.

Usage:
    python password_generator.py
"""

from typing import List, Tuple
import secrets
import string
import math


SYMBOLS = "!@#$%^&*()-_=+[]{}:;,.<>?/|"
LEET_MAP = str.maketrans({
    "a": "@",
    "A": "@",
    "e": "3",
    "E": "3",
    "i": "1",
    "I": "1",
    "o": "0",
    "O": "0",
    "s": "$",
    "S": "$",
    "t": "7",
    "T": "7",
})


def normalize_name(name: str) -> List[str]:
    """Split name into parts and remove non-letter characters."""
    parts = []
    for p in name.strip().split():
        filtered = "".join(ch for ch in p if ch.isalpha())
        if filtered:
            parts.append(filtered)
    return parts


def take_chunks(parts: List[str], max_chunks: int = 3) -> List[str]:
    """Take 1-3 chunks (prefixes/syllable-like) from name parts to build a base mnemonic."""
    chunks = []
    for p in parts[:max_chunks]:
        # Heuristic: first 3 letters or first 2 + last 1 if short, else first 3
        if len(p) <= 3:
            chunks.append(p.lower())
        else:
            chunks.append(p[:3].lower())
    # If only one chunk, split it into two pieces for memorability
    if len(chunks) == 1 and len(chunks[0]) >= 4:
        c = chunks[0]
        chunks = [c[:2], c[2:]]
    return chunks


def leet_transform(s: str, strength: float = 0.5) -> str:
    """Apply leet substitutions probabilistically. strength between 0 and 1."""
    if strength <= 0:
        return s
    out = []
    for ch in s:
        if ch.lower() in "aeiost" and secrets.randbelow(100) < int(100 * strength):
            out.append(ch.translate(LEET_MAP))
        else:
            out.append(ch)
    return "".join(out)


def ensure_classes(pw_chars: List[str]) -> List[str]:
    """Ensure at least one of each class exists by replacing random positions if needed."""
    s = "".join(pw_chars)
    classes = {
        "lower": any(c.islower() for c in s),
        "upper": any(c.isupper() for c in s),
        "digit": any(c.isdigit() for c in s),
        "symbol": any(c in SYMBOLS for c in s),
    }
    # positions we may replace
    positions = list(range(len(pw_chars)))
    secrets.SystemRandom().shuffle(positions)

    if not classes["upper"]:
        pos = positions.pop()
        pw_chars[pos] = secrets.choice(string.ascii_uppercase)
    if not classes["lower"]:
        pos = positions.pop()
        pw_chars[pos] = secrets.choice(string.ascii_lowercase)
    if not classes["digit"]:
        pos = positions.pop()
        pw_chars[pos] = secrets.choice(string.digits)
    if not classes["symbol"]:
        pos = positions.pop()
        pw_chars[pos] = secrets.choice(SYMBOLS)
    return pw_chars


def estimate_entropy(password: str) -> float:
    """Estimate entropy in bits based on character class coverage and length."""
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in SYMBOLS for c in password):
        pool += len(SYMBOLS)
    if pool == 0:
        return 0.0
    return len(password) * math.log2(pool)


def generate_from_name(name: str, length: int = 14, candidates: int = 5, leet_strength: float = 0.5) -> List[Tuple[str, float]]:
    """
    Generate `candidates` password suggestions from `name`, aiming for `length`.
    Returns list of (password, entropy_bits).
    """
    parts = normalize_name(name)
    if not parts:
        raise ValueError("Please provide a name containing alphabetic characters.")
    base_chunks = take_chunks(parts, max_chunks=3)
    suggestions = []

    for _ in range(candidates):
        # Start with a mnemonic base: join chunks with a memorable separator
        sep = secrets.choice(["-", "_", ".", "~"])
        base = sep.join(base_chunks)

        # Randomly choose to append/prepend year or small number
        if secrets.randbelow(100) < 60:
            # choose a small memorable number or year-like (2-4 digits)
            num_choice = secrets.choice([str(secrets.randbelow(90)+10), str(19 + secrets.randbelow(30)) + str(secrets.randbelow(10)), str(secrets.randbelow(900)+100)])
            if secrets.randbelow(2):
                base = num_choice + sep + base
            else:
                base = base + sep + num_choice

        # Apply leet substitutions (partially) and random capitalization
        transformed = leet_transform(base, strength=leet_strength)
        # Capitalize a random chunk or letter
        if secrets.randbelow(2):
            i = secrets.randbelow(len(transformed))
            transformed = transformed[:i] + transformed[i].upper() + transformed[i+1:]

        # Now make a list of chars and inject random characters to reach desired length
        pw_chars = list(transformed)
        while len(pw_chars) < length:
            # add a random class based on probabilities favoring digits/symbols moderately
            r = secrets.randbelow(100)
            if r < 40:
                pw_chars.append(secrets.choice(string.digits))
            elif r < 75:
                pw_chars.append(secrets.choice(SYMBOLS))
            else:
                # random letter (mix case)
                ch = secrets.choice(string.ascii_letters)
                pw_chars.append(ch)

        # If too long, randomly remove some chars while keeping structure
        while len(pw_chars) > length:
            del pw_chars[secrets.randbelow(len(pw_chars))]

        # Ensure all classes present
        pw_chars = ensure_classes(pw_chars)

        # Shuffle a little to avoid entirely name-prefixed structure, but keep some order for memorability
        # We'll do a mild shuffle: perform a few pairwise swaps
        for _ in range(max(1, len(pw_chars)//6)):
            i = secrets.randbelow(len(pw_chars))
            j = secrets.randbelow(len(pw_chars))
            pw_chars[i], pw_chars[j] = pw_chars[j], pw_chars[i]

        candidate = "".join(pw_chars)
        entropy = estimate_entropy(candidate)
        suggestions.append((candidate, entropy))

    # Sort by entropy descending
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions


def main():
    print("Memorable+Strong Password Generator (derived from name)")
    name = input("Enter the person's full name (first last ...): ").strip()
    if not name:
        print("No name entered. Exiting.")
        return
    try:
        desired_len_raw = input("Desired password length (recommended 12-20) [14]: ").strip()
        desired_len = int(desired_len_raw) if desired_len_raw else 14
    except ValueError:
        print("Invalid length; using 14.")
        desired_len = 14

    try:
        count_raw = input("How many candidates to generate [5]: ").strip()
        count = int(count_raw) if count_raw else 5
    except ValueError:
        count = 5

    print("\nGenerating...\n")
    results = generate_from_name(name, length=desired_len, candidates=count)

    for i, (pw, ent) in enumerate(results, start=1):
        print(f"{i:>2}. {pw}    (est. entropy: {ent:.1f} bits)")

    print("\nNotes:")
    print("- Entropy estimate is a rough calculation; aim for >= 60 bits for general accounts, >= 80 bits for high-value accounts.")
    print("- If the password will be reused across sites, use a password manager and a unique random password instead.")
    print("- Avoid putting the full real name or other public info in the password if the account may be targeted.")


if __name__ == "__main__":
    main()