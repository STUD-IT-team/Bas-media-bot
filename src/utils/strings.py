def NewlineJoin(*strings) -> str:
    return '\n'.join(strings)


def EnumerateStrings(*strings) -> list[str]:
    return [f'{i+1}. {s}' for i, s in enumerate(strings)]
