import struct
from pathlib import Path


TAPE_SIZE = 30_000
INTEGER_TYPE = 1
PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = PROJECT_DIR / "common" / "bf_tape_30000.arr"


def generate_empty_tape(output_path: Path = OUTPUT_PATH, size: int = TAPE_SIZE) -> None:
    """Write an Aidem Media ARR containing `size` integer zeroes."""
    array_header = struct.pack("<i", size)
    zero_integer = struct.pack("<ii", INTEGER_TYPE, 0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output_file:
        output_file.write(array_header)
        output_file.write(zero_integer * size)


if __name__ == "__main__":
    generate_empty_tape()
    print(
        f"Generated {OUTPUT_PATH.relative_to(PROJECT_DIR)} "
        f"({TAPE_SIZE} integer zeroes)"
    )
