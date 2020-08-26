def count_symbols(photo, size):
    """
    Андрей Мишаков
    Возвращает кол-во символов в строке по картинке и размеру шрифта
    """
    return photo.get_size()[0] // (size * 0.785)


def fragmentation(user_text, max_length):
    """
    Варя Холевенкова
    Разбиение строки на список из строк,
    каждая из которых не длиннее заданного значения
    """
    separated = []
    user_text = user_text.strip()
    user_text += ' '
    while len(user_text) > max_length:
        j = user_text.find(' ')
        while (user_text.find(' ', j + 1) != -1 and
               user_text.find(' ', j + 1) <= max_length):
            j = user_text.find(' ', j + 1)
        separated.append(user_text[:j])
        user_text = user_text[j + 1:]
    if user_text[:len(user_text) - 1] != '':
        separated.append(user_text[:len(user_text) - 1])
    return separated


def fr(user_text, max_length):
    """
    Катя
    Разбиение строки на строки по max_length символов
    """
    if len(user_text) < max_length:
        return user_text

    lines = []
    for a in range(0, len(user_text), max_length):
        lines.append(user_text[a: a + max_length])

    return lines


if __name__ == "__main__":
    text = input()  # Строка, которая подаётся на ввод
    max_len = int(input())  # Каждая строка в выходном списке не длиннее
    print(fragmentation(text, max_len))
    print(fr(text, max_len))
