"""Assignment 01 (modular arithmetic): answers each `modexp` and `modinv` line of a test input.

The checker runs `assignment_01_modular_arithmetic.py <input-file> <output-file>`. The arithmetic
is in src/pkiaudit/ecc/modmath.py.
"""

import sys

from pkiaudit.ecc.modmath import modexp, modinv


def main(input_path: str, output_path: str) -> None:
    """Writes one answer line per question line of the input."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "modexp":  # modexp <base> <exp> <mod>
                base, exp, mod = int(words[1]), int(words[2]), int(words[3])
                lines.append(f"modexp {modexp(base, exp, mod)}")
            elif words[0] == "modinv":  # modinv <a> <mod>
                inverse = modinv(int(words[1]), int(words[2]))
                lines.append("modinv none" if inverse is None else f"modinv {inverse}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
