#!/usr/bin/env python3
# 4Hats Shop — hat-only win path (2 intended vulns: hidden 'add', high discount bonus)
import os, secrets, sys, time, math
from decimal import Decimal, InvalidOperation

FLAG = "4hats{gre@t_hat_&cup_sh#p}"
TYPE_DELAY = 0.010
FAST_BANNER_DELAY = 0.002

# Intended vuln #2: large discount → credit bonus
HIGH_DISCOUNT_THRESHOLD = Decimal("10000000")  # discount >= this grants bonus
BONUS_CREDIT = 1_000_000

ITEMS = [
    ("mug", 60),
    ("tshirt", 80),
    ("poster", 40),
    ("sticker", 10),
    ("hat", 999_999),  # must be bought, then Checkout to reveal flag
]

BANNER = r"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      ✨   4 H A T S   S H O P   ✨                         ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Balance starts at $100.                                                   ║
║                                                                            ║
║  Buying the HAT and checking out reveals the reward.                       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

def slow_print(text: str, delay=TYPE_DELAY, end="\n"):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end); sys.stdout.flush()

def banner_print():
    for line in BANNER.strip("\n").splitlines():
        slow_print(line, delay=FAST_BANNER_DELAY)
    sys.stdout.write("\n"); sys.stdout.flush()

def hr():
    slow_print("─" * 74)

def chrome_header(title: str, balance: int, total: int, discount: Decimal):
    sys.stdout.write("\n")
    slow_print("╔" + "═" * 74 + "╗", delay=FAST_BANNER_DELAY)
    slow_print(f"║ {title:<72} ║", delay=FAST_BANNER_DELAY)
    slow_print("╠" + "═" * 74 + "╣", delay=FAST_BANNER_DELAY)
    info = f"Balance: ${balance} | Cart Total: ${total} | Discount: {discount if discount else 0}"
    slow_print(f"║ {info:<72} ║", delay=FAST_BANNER_DELAY)
    slow_print("╚" + "═" * 74 + "╝", delay=FAST_BANNER_DELAY)

def show_main_menu(balance, total, discount):
    chrome_header("MAIN MENU", balance, total, discount)
    slow_print("1) Shop")
    slow_print("2) Cart")
    slow_print("3) Discount")
    slow_print("4) Checkout")
    slow_print("5) Exit")
    hr()

def show_shop_list(balance, total, discount):
    chrome_header("BOUTIQUE", balance, total, discount)
    for i, (name, price) in enumerate(ITEMS, start=1):
        slow_print(f"{i}) {name:<10}  —  ${price}")
    slow_print("0) Back")
    hr()

class Session:
    def __init__(self):
        self.balance = 100
        self.sid = secrets.token_hex(4)
        self.cart = []
        self.last_discount_value = Decimal("0")

    def total(self):
        return sum(price for _, price in self.cart)

def parse_numeric(expr: str):
    expr = expr.strip().replace("_", "")
    if not expr:
        raise InvalidOperation("empty")
    if not all(c.isdigit() or c in "+-." for c in expr):
        raise InvalidOperation("non-numeric")
    val = Decimal(expr)
    if val.is_nan() or val.is_infinite():
        raise InvalidOperation("nan/inf")
    return val

def show_cart(s: Session):
    chrome_header("YOUR CART", s.balance, s.total(), s.last_discount_value)
    if not s.cart:
        slow_print("No items yet.")
    else:
        for i, (name, price) in enumerate(s.cart, start=1):
            slow_print(f"{i}) {name:<10}  —  ${price}")
        slow_print(f"\nSubtotal: ${s.total()}")
        if s.last_discount_value:
            payable = max(0, s.total() - int(s.last_discount_value))
            slow_print(f"After Discount: ${payable}")
    hr()

def add_by_number(s: Session, num: int):
    if num < 1 or num > len(ITEMS):
        slow_print("Invalid selection."); return
    idx = num - 1
    name, price = ITEMS[idx]
    if price > s.balance:
        slow_print(f"Insufficient balance. You have ${s.balance}."); return
    s.balance -= price
    s.cart.append((name, price))
    slow_print(f"Added {name}. Balance now ${s.balance}.")

def hidden_add_balance(s: Session, line: str):
    parts = line.strip().split(maxsplit=1)
    if len(parts) == 1:
        slow_print("Enter amount to add:")
        amt_in = input("amount> ").strip()
    else:
        amt_in = parts[1].strip()
    if not (amt_in.lstrip("+-").isdigit()):
        slow_print("Amount must be an integer."); return
    amt = int(amt_in)
    if amt <= 0:
        slow_print("Amount must be positive."); return
    if amt > 1_000_000_000:
        slow_print("Amount too large."); return
    s.balance += amt
    slow_print(f"Balance updated: +${amt} → ${s.balance}")

def main():
    if not os.path.exists("flag.txt"):
        with open("flag.txt", "w") as f:
            f.write(FLAG + "\n")

    s = Session()
    banner_print()
    slow_print(f"(session: {s.sid})\n")
    mode = "menu"
    show_main_menu(s.balance, s.total(), s.last_discount_value)

    while True:
        try:
            cmd = input("◈ ").strip()
        except (EOFError, KeyboardInterrupt):
            slow_print("\nGoodbye."); break
        if not cmd:
            continue

        # Hidden command (intended vuln #1): add <amount>
        if cmd.lower().startswith("add"):
            hidden_add_balance(s, cmd)
            if mode == "shop":
                show_shop_list(s.balance, s.total(), s.last_discount_value)
            else:
                show_main_menu(s.balance, s.total(), s.last_discount_value)
            continue

        # SHOP mode: pick item number, 0 to back
        if mode == "shop":
            if cmd.isdigit():
                n = int(cmd)
                if n == 0:
                    mode = "menu"
                    show_main_menu(s.balance, s.total(), s.last_discount_value)
                else:
                    add_by_number(s, n)
                    show_shop_list(s.balance, s.total(), s.last_discount_value)
            else:
                slow_print("Enter item number or 0 to go back.")
            continue

        # MENU mode only numbers
        if not cmd.isdigit():
            slow_print("Use numbers 1-5.")
            show_main_menu(s.balance, s.total(), s.last_discount_value)
            continue

        choice = int(cmd)

        if choice == 1:
            mode = "shop"
            show_shop_list(s.balance, s.total(), s.last_discount_value)

        elif choice == 2:
            show_cart(s)
            show_main_menu(s.balance, s.total(), s.last_discount_value)

        elif choice == 3:
            chrome_header("DISCOUNT CONSOLE", s.balance, s.total(), s.last_discount_value)
            slow_print("Enter a numeric discount")
            expr = input("expr> ")
            try:
                val = parse_numeric(expr)
            except InvalidOperation:
                slow_print("Discount must be a number. Set to 0.")
                s.last_discount_value = Decimal("0")
            else:
                if val < 0:
                    slow_print("Negative discount is not allowed. Set to 0.")
                    s.last_discount_value = Decimal("0")
                else:
                    s.last_discount_value = val
                    slow_print(f"=> saved discount: {s.last_discount_value}")
                    # Intended vuln #2: high numeric discount grants bonus credit
                    if val >= HIGH_DISCOUNT_THRESHOLD:
                        s.balance += BONUS_CREDIT
                        slow_print(f"Super discount detected! Bonus +${BONUS_CREDIT} credited.")
            hr()
            show_main_menu(s.balance, s.total(), s.last_discount_value)

        elif choice == 4:
            chrome_header("CHECKOUT", s.balance, s.total(), s.last_discount_value)
            if any(name == "hat" for name, _ in s.cart):
                slow_print(open("flag.txt").read().strip())
            else:
                slow_print("You don't have the required premium item.")
            hr()
            show_main_menu(s.balance, s.total(), s.last_discount_value)

        elif choice == 5:
            slow_print("Goodbye.")
            break

        else:
            slow_print("Invalid selection.")
            show_main_menu(s.balance, s.total(), s.last_discount_value)

if __name__ == "__main__":
    main()

