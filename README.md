# BFMoo

[Polski](README.pl.md) | **English**

**BFMoo** is a **Brainfuck** interpreter implemented in the **Piklib / BlooMoo** scripting environment.
It is both a stress test for the original engine and a practical testbed for my emulator/runtime.

Main demo goal: run a **Brainfuck Snake** program (bf16-compatible) and render output as **RGB332** on a **16×16** grid.

## How it works

### Rendering (RGB332 → screen, CLSSCREEN.CLASS)
- The screen is **256 “pixels”** (16×16).
- Each pixel is a **clone object** that plays a palette animation:
  - 1 event, **256 frames**,
  - frame index = color index (0..255).
- Each tick, the interpreter updates `videoMem[0..255]`,
  and the renderer calls `SETFRAME(0,colorIndex)` on each clone as needed.

> Note: the engine uses a classic DirectDraw **colorkey** (magenta / 0xF81F RGB565).
> A small workaround is used to avoid triggering transparency for that exact color.

### Brainfuck (CLSBF.CLASS)
The BF interpreter lives in `CLSBF.CLASS` and keeps:
- 30,000-byte tape,
- data pointer (DP),
- instruction pointer (IP),
- precomputed bracket map for `[`/`]`,
- runtime I/O hooks.

## Status
- ✅ 16×16 RGB332 palette grid works and is fast
- 🧩 BF interpreter work-in-progress (`CLSBF.CLASS`)
- ⏳ Next: integrate and run Brainfuck Snake
