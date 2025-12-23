# BFMoo

**Polski** | [English](README.md)

**BFMoo** to interpreter języka **Brainfuck** napisany w skryptowym języku silnika **Piklib / BlooMoo**.
Projekt jest równocześnie testem możliwości technicznych silnika oraz mojej implementacji/emulacji zachowania Piklib.

Główny cel demo: uruchomić **Snake’a napisanego w Brainfucku** (program kompatybilny z bf16),
renderując obraz jako **RGB332** na siatce **16×16**.

---

## Jak to działa

### Render (RGB332 → ekran, CLSSCREEN.CLASS)
- Ekran to **256 “pikseli”** (16×16).
- Każdy piksel to osobny **klon obiektu** z animacją-paleta:
  - 1 event, **256 klatek**,
  - numer klatki = numer koloru (0..255).
- W każdej klatce interpreter aktualizuje `videoMem[0..255]`,
  a renderer wywołuje `SETFRAME(0,colorIndex)` na odpowiednim klonie.

> Uwaga: w silniku występował klasyczny problem DirectDraw z **colorkey** (magenta / 0xF81F w RGB565).
> W demo zastosowano prosty workaround: drobna modyfikacja wartości (np. flip 0x0001) dla tej jednej barwy.

### Brainfuck (CLSBF.CLASS)
Interpreter BF jest realizowany jako osobna klasa `CLSBF.CLASS`, która trzyma:
- taśmę pamięci (30000 bajtów),
- wskaźnik danych (DP),
- licznik instrukcji (IP),
- mapowanie nawiasów `[`/`]` (preprocessing),
- wejście/wyjście dopasowane do runtime.

---

## Status
- ✅ Siatka 16×16 i paleta RGB332 działają i są szybkie
- 🧩 Trwa implementacja interpretera BF w `CLSBF.CLASS`
- ⏳ Następny krok: integracja z programem Snake (Brainfuck)
