# Модуль для работы с pygame

import pygame  # Модуль для наложения текста на картинку (в данном случае)

pygame.init()  # Инициализация модуля pygame

pygame_fonts = pygame.font.get_fonts()


def create_mem(chat_id, text, text_style, text_position, text_rotation):
    """
    Наложение текста с заданным пользователем стилем на тестовую картинку.
    chat_id - id пользователя / чата
    text - текст, который будет отрисован
    font_style - список со стилем текста (название, размер, жирность, курсив,
        цвет текста в rgb)
    text_position - позиция текста в формате (format, x, y),
        format - рх / percent, x и y - координаты текста в int
    text_rotation - угол поворота текста
    """
    font = pygame.font.SysFont(*text_style[:-1])  # Создание шрифта
    text_object = font.render(text, 1, text_style[-1])  # Объект текста

    rotated_text = pygame.transform.rotate(text_object, -text_rotation)

    image = pygame.image.load(f"users/{chat_id}/img/source_picture.jpg")
    size = image.get_size()  # Размеры картинки
    screen = pygame.Surface(size)  # Рабочее поле с размерами картинки

    coords_format, x, y = text_position  # Распаковываем text_position
    if coords_format == "px":  # Если x и y заданы в px
        # i, j = x - text_object.get_width(), y - text_object.get_height()
        i, j = x, y  # Координаты верхнего левого угла текста
    elif coords_format == "percent":  # Если x и y заданы в %
        # Координаты центра текста
        i = (size[0] * x) // 100 - rotated_text.get_width() // 2
        j = (size[1] * y) // 100 - rotated_text.get_height() // 2
    else:  # Если произошла какая-то ошибка, format != "px" или "percent"
        raise ValueError("Ошибка в формате координат")

    image.blit(rotated_text, (i, j))  # Отрисовка текста на картинке
    screen.blit(image, (0, 0))  # Картинка на всё рабочее поле

    # Сохраняем всё рабочее поле в новый файл
    pygame.image.save(screen, f"users/{chat_id}/img/answer_picture.jpg")


def get_img_size(chat_id):
    """Получение размеров отправленной пользователем картинки"""
    image = pygame.image.load(f"users/{chat_id}/img/source_picture.jpg")
    return image.get_size()
