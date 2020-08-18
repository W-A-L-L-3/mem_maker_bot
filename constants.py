# Файл с константами для бота

# Константы цветов для текста в rgb
color_black = (0, 0, 0)
color_white = (255, 255, 255)
color_red = (255, 0, 0)
color_orange = (255, 145, 0)
color_yellow = (255, 255, 0)
color_green = (72, 255, 0)
color_blue = (0, 81, 255)
color_purple = (159, 0, 191)

standard_text_setting = ["arial", 40, False, False,
                         (0, 0, 0)]  # Стандартный набор настроек текста
standard_text_position = ["percent", 50,
                          50]  # Стандартное расположение текста (по центру)
# Пакеты настроек текста
text_setting_packs = [['cambria', 30, False, True, (0, 0, 0)],
                      ['comicsansms', 30, False, True, (0, 0, 0)],
                      ['franklingothicmedium', 30, False, True, (0, 0, 0)],
                      ['malgungothicsemilight', 30, True, True, (0, 0, 0)],
                      ['palatinolinotype', 30, True, True, (0, 0, 0)]]

max_mem_text_len = 200  # Макс. длина текста, который накладывается на картинку
max_font_size = 1000  # Макс. размер шрифта, который может быть использован

quantity_of_fonts = 20  # Кол-во доступных шрифтов в списке

rotation_degrees = (0, 45, 90, 180, 270)  # Стандартный набор углов наклона
