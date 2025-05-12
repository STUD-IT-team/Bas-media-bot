def NewlineJoin(*strings) -> str:
    return '\n'.join(strings)


def EnumerateStrings(*strings) -> list[str]:
    return [f'{i+1}. {s}' for i, s in enumerate(strings)]

# Функция нужна для объединения вывода Traceback
# Функция предполагает что в строках уже стоят '\n'
def JoinStringsAddBorder(strings: list[str]) -> str:
    BorderChar = '-'
    BorderLen = 85 # min(len(max(strings, key=len)), 85)

    BorderLine = (BorderChar * BorderLen) + '\n'

    return BorderLine + ''.join(strings) + BorderLine
