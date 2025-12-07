# ============================================================
#             ЭТАПЫ 1–4: ПОЛНЫЙ ПРОЕКТ УВМ
# ============================================================

# ============================================================
#                 ЭТАП 1 — ОПИСАНИЕ КОМАНД
#
# Команда 1: STORE
#  Формат: A(0–6), B(7–13), C(14–20), D(21–34)
#  Семантика: memory[ reg[B] + D ] = reg[C]
#
# Команда 2: SHIFT LEFT
#  Формат: A(0–6), B(7–13), C(14–20), D(21–27), E(28–41)
#  Семантика:
#      op1 = memory[ reg[B] + E ]
#      op2 = reg[D]
#      result = op1 << op2
#      memory[ reg[C] ] = result
# ============================================================


# ============================================================
#            ЭТАП 2 — СТРУКТУРЫ ДАННЫХ + ДЕКОДЕР
# ============================================================

memory = [0] * 5000       # память УВМ
reg = [0] * 256           # регистры УВМ

def get_bits(value, start, end):
    """Извлекает биты [start..end]."""
    mask = (1 << (end - start + 1)) - 1
    return (value >> start) & mask


def decode_A_B_C_D(cmd):
    x = int.from_bytes(cmd, "little")
    A = get_bits(x, 0, 6)
    B = get_bits(x, 7, 13)
    C = get_bits(x, 14, 20)
    D = get_bits(x, 21, 34)
    return A, B, C, D


def decode_A_B_C_D_E(cmd):
    x = int.from_bytes(cmd, "little")
    A = get_bits(x, 0, 6)
    B = get_bits(x, 7, 13)
    C = get_bits(x, 14, 20)
    D = get_bits(x, 21, 27)
    E = get_bits(x, 28, 41)
    return A, B, C, D, E


# ============================================================
#                    ЭТАП 3 — ИНТЕРПРЕТАТОР
# ============================================================

def exec_store(cmd):
    A, B, C, D = decode_A_B_C_D(cmd)
    value = reg[C]
    addr = reg[B] + D
    memory[addr] = value
    print(f"[STORE] R[{C}]={value} -> MEM[{addr}]")


def exec_shift_left(cmd):
    A, B, C, D, E = decode_A_B_C_D_E(cmd)
    addr = reg[B] + E
    op1 = memory[addr]
    op2 = reg[D]
    result = (op1 << op2) & 0xFFFFFFFF
    dest = reg[C]
    memory[dest] = result
    print(f"[SHL] MEM[{addr}]={op1} << R[{D}]={op2} = {result} -> MEM[{dest}]")


def execute(cmd):
    if len(cmd) == 5:
        exec_store(cmd)
    elif len(cmd) == 6:
        exec_shift_left(cmd)
    else:
        raise ValueError("Неизвестный формат команды")


# ============================================================
#                     ЭТАП 4 — АССЕМБЛЕР
# ============================================================

def set_bits(value, field, start, end):
    mask = (1 << (end - start + 1)) - 1
    return value | ((field & mask) << start)


def assemble_store(A, B, C, D):
    x = 0
    x = set_bits(x, A, 0, 6)
    x = set_bits(x, B, 7, 13)
    x = set_bits(x, C, 14, 20)
    x = set_bits(x, D, 21, 34)
    return x.to_bytes(5, "little")


def assemble_shift_left(A, B, C, D, E):
    x = 0
    x = set_bits(x, A, 0, 6)
    x = set_bits(x, B, 7, 13)
    x = set_bits(x, C, 14, 20)
    x = set_bits(x, D, 21, 27)
    x = set_bits(x, E, 28, 41)
    return x.to_bytes(6, "little")


# ============================================================
#                    ТЕСТИРОВАНИЕ ВСЕХ ЭТАПОВ
# ============================================================
if __name__ == "__main__":

    print("\n======= ТЕСТ 1: STORE (из задания) =======")
    cmd1 = assemble_store(126, 97, 112, 165)   # FE 30 BC 14 00
    reg[97] = 100
    reg[112] = 77
    execute(cmd1)
    print("Ожидаем 77 ->", memory[100 + 165])

    print("\n======= ТЕСТ 2: SHIFT LEFT (из задания) =======")
    cmd2 = assemble_shift_left(51, 38, 41, 57, 843)  # 33 53 2A B7 34 00
    reg[38] = 200
    reg[41] = 500
    reg[57] = 3
    memory[200 + 843] = 6
    execute(cmd2)
    print("Ожидаем 48 ->", memory[500])

# ============================================================
#                   ЭТАП 5 — ДИАЛОГОВЫЙ ИНТЕРФЕЙС
# ============================================================

def repl():
    print("\n===============================")
    print("  УВМ Вариант 32 — Интерфейс")
    print("===============================")
    print("Доступные команды:")
    print("  store A B C D")
    print("  shift A B C D E")
    print("  reg i value     — записать значение в регистр")
    print("  mem addr value  — записать значение в память")
    print("  print reg i     — показать регистр")
    print("  print mem addr  — показать память")
    print("  exit            — выход")
    print("-------------------------------")

    while True:
        cmd = input(">>> ").strip().lower()

        if cmd == "":
            continue

        # выход
        if cmd == "exit":
            print("Выход из УВМ...")
            break

        parts = cmd.split()

        # ----------------------------------------------------
        # STORE
        # ----------------------------------------------------
        if parts[0] == "store":
            if len(parts) != 5:
                print("Использование: store A B C D")
                continue

            A, B, C, D = map(int, parts[1:])
            ins = assemble_store(A, B, C, D)
            execute(ins)

        # ----------------------------------------------------
        # SHIFT LEFT
        # ----------------------------------------------------
        elif parts[0] == "shift":
            if len(parts) != 6:
                print("Использование: shift A B C D E")
                continue

            A, B, C, D, E = map(int, parts[1:])
            ins = assemble_shift_left(A, B, C, D, E)
            execute(ins)

        # ----------------------------------------------------
        # Установка регистра
        # ----------------------------------------------------
        elif parts[0] == "reg":
            if len(parts) != 3:
                print("Использование: reg индекс значение")
                continue

            i, val = int(parts[1]), int(parts[2])
            reg[i] = val
            print(f"R[{i}] = {val}")

        # ----------------------------------------------------
        # Установка памяти
        # ----------------------------------------------------
        elif parts[0] == "mem":
            if len(parts) != 3:
                print("Использование: mem адрес значение")
                continue

            addr, val = int(parts[1]), int(parts[2])
            memory[addr] = val
            print(f"MEM[{addr}] = {val}")

        # ----------------------------------------------------
        # PRINT
        # ----------------------------------------------------
        elif parts[0] == "print":
            if len(parts) != 3:
                print("Использование: print reg i  |  print mem addr")
                continue

            what = parts[1]
            arg = int(parts[2])

            if what == "reg":
                print(f"R[{arg}] = {reg[arg]}")
            elif what == "mem":
                print(f"MEM[{arg}] = {memory[arg]}")
            else:
                print("Неизвестный объект для печати.")

        # ----------------------------------------------------
        # НЕИЗВЕСТНАЯ КОМАНДА
        # ----------------------------------------------------
        else:
            print("Неизвестная команда. Введите 'help'.")


# ------------------------------------------------------------
#      Запуск интерфейса (после тестов)
# ------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== Запускаю REPL (Этап 5) ===")
    repl()
