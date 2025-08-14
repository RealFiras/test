#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time, base64

# ===================== Settings =====================
SLOW_DELAY = 0.02   # per-char delay for "typewriter" effect
MAX_WRONG  = 3

RED   = "\033[31m"
RESET = "\033[0m"
BOLD  = "\033[1m"

def type_out(text, delay=SLOW_DELAY, end="\n"):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()

def ask(prompt):
    type_out(prompt, end="")
    sys.stdout.flush()
    return sys.stdin.readline().strip()

def show_attempts_left(wrongs):
    left = MAX_WRONG - wrongs
    msg = f"{left} attempts left." if left != 1 else "1 attempt left."
    sys.stdout.write(RED + msg + RESET + "\n")
    sys.stdout.flush()

# ===================== Banner & Art =====================
BANNER = r"""
  ____  _                                _                     
 / ___|| |__   __ _ _ __ ___  ___  _ __ | | ___   ___  _ __    
 \___ \| '_ \ / _` | '__/ __|/ _ \| '_ \| |/ _ \ / _ \| '_ \   
  ___) | | | | (_| | |  \__ \  __/| | | | | (_) | (_) | | | |  
 |____/|_| |_|\__,_|_|  |___/\___||_| |_|_|\___/ \___/|_| |_|  
"""

ASCII_ART = r"""
    .--.   .-.
   |o_o | (o o)   <- Squidward (tiny)
   |:_/ |  |-|
  //   \ \ / \
 (|     | )|_|_|
/'\_   _/`     \
\___)=(___/  \__\

  <- SpongeBob (small & cute!)
"""

TITLE = "Krabby Patty Secrets — SpongeBob Crypto CTF (Shamshoon Edition)"

# ===================== Flag Parts (Base64) =====================
# Decoded parts join to: HATS{SPONGE_BOB_LOVES_KRABBY_PATTIES}
FLAG_PARTS_PLAIN = ["HATS{", "SPONGE_", "BOB_LOVES_", "KRABBY_", "PATTIES}"]
FLAG_PARTS_B64   = [base64.b64encode(p.encode()).decode() for p in FLAG_PARTS_PLAIN]

# ===================== Stages (Hard + Tricky) =====================
# كل مرحلة فيها تلميح ضمني داخل النص، لكن ما في حلول تلقائية جاهزة.
stages = [
    # Stage 1 — Base64url مُشوَّه + Homoglyphs + Reverse + No padding in prompt
    {
        "intro": "Spatula edge note:\n  \u0406WYytEI5R3c1J\u0417S\n\nDoodle: “no dressing, flip the patty”\n",
        # Expected: "KRUSTY KRAB"
        "answer_variants": [
            "KRUSTY KRAB", "Krusty Krab", "krusty krab", "krustykrab", "KRUSTYKRAB"
        ],
        "hint": "Some letters aren’t what they look like. Normalize, flip, then decode safely."
    },

    # Stage 2 — Keyboard layout confusion (Dvorak <-> Qwerty) + spacing noise
    {
        "intro": "Squidward typed this with “his own layout”:\n  Cfrfcp   Cffycp\n\nFootnote: “mind the rests between notes”\n",
        # Expected: "BIKINI BOTTOM"
        "answer_variants": [
            "BIKINI BOTTOM", "Bikini Bottom", "bikini bottom", "bikinibottom", "BIKINIBOTTOM"
        ],
        "hint": "Try reading it as if it were typed on a different keyboard layout."
    },

    # Stage 3 — Morse inverted (dot<->dash) + per-letter reversal + zero-width spaces
    {
        "intro": "Jellyfish buzz:\n  • –– ••\u200b   – • –    ••– •–•   •• –––\n\nNote: “flip the poles, currents flow backward… (watch for invisible trails)”\n",
        # Expected: "GARY THE SNAIL"
        "answer_variants": [
            "GARY THE SNAIL", "Gary The Snail", "gary the snail", "GARYTHESNAIL", "garythesnail"
        ],
        "hint": "Normalize spacing, swap dot/dash, then reverse within letters."
    },

    # Stage 4 — Auto-key XOR (key from embedded arithmetic)
    {
        "intro": "Receipt hex (spilled soda on it):\n  11 5A 0F 1C 55 0E 11 5E 1E 12 12 59 5E 10\n\nCashier scribble:\n  “Total: 3 krabby patties @ 17 each + 2 drinks @ 4”\n",
        # Expected: "SECRET FORMULA"
        "answer_variants": [
            "SECRET FORMULA", "Secret Formula", "secret formula", "SECRETFORMULA", "secretformula"
        ],
        "hint": "Compute the total, start there, and let each recovered byte drive the next."
    },

    # Stage 5 — Base58 then simple letter swaps (A↔E, O↔U, T↔L)
    {
        "intro": "Tip jar note:\n  WXB3byRCTmnCp5n7ize\n\nChalkboard:\n  A↔E, O↔U, T↔L  (vowels sound funny today…)\n",
        # Expected: "PLANKTON RULES"
        "answer_variants": [
            "PLANKTON RULES", "Plankton Rules", "plankton rules", "PLANKTONRULES", "planktonrules"
        ],
        "hint": "It’s not Base64. After decoding, letters may have swapped partners."
    },
]

# ===================== Runner =====================
def main():
    # Greeting
    type_out(BANNER, delay=0.001)
    type_out(BOLD + TITLE + RESET)
    type_out(ASCII_ART)
    type_out("Welcome to Bikini Bottom! 🧽🍍\n")
    type_out("Rules:\n- 5 crypto stages.\n- You have only 3 wrong attempts total.\n- Each correct answer reveals one Base64 flag part.\n- Decode each part from Base64 and join in order for the final flag.\n")
    type_out("Good luck, sailor! 🦀\n\n")

    wrongs = 0
    obtained = []

    for i, stage in enumerate(stages, 1):
        type_out(f"--- Stage {i} ---\n")
        type_out(stage["intro"] + "\n")

        while True:
            ans = ask("> Your answer: ").strip()
            if ans in stage["answer_variants"]:
                type_out("✅ Correct! Here’s your Base64 flag part:")
                part_b64 = FLAG_PARTS_B64[i-1]
                type_out(f"  [Part {i}/5]  {part_b64}\n")
                obtained.append(part_b64)
                type_out("💡 Tip: keep it safe; decode all parts at the end and join in order.\n")
                break
            else:
                wrongs += 1
                type_out("❌ Incorrect.")
                if wrongs >= MAX_WRONG:
                    type_out(RED + "No attempts left! Reconnect to try again.\n" + RESET)
                    return
                show_attempts_left(wrongs)
                # Show hint after the second mistake on a given stage to keep it tough
                if wrongs % 2 == 0:
                    type_out(f"Hint: {stage['hint']}\n")

    # Success
    type_out(BOLD + "\n🎉 Nice! You collected all parts." + RESET)
    type_out("Here are the Base64 parts you earned:")
    for idx, p in enumerate(obtained, 1):
        type_out(f"  [Part {idx}/5] {p}")
    type_out("\nDecode each part from Base64 and join them in order for the final flag.")
    type_out("🚩 Format reminder: HATS{...}\n")
    type_out("See you at the Krusty Krab! 🍔")
    

if __name__ == "__main__":
    try:
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
        main()
    except Exception:
        sys.stdout.write("\nAn unexpected error occurred. Please try again later.\n")
        sys.stdout.flush()
