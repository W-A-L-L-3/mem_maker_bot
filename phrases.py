# Файл с фразами для общения с пользователем

first_msg = "Привет! Я MemMakerBot."

yes = "да"
no = "нет"

# Настройка шрифта
font_setting_on = "Включен режим настройки шрифта"
font_setting_off = "Настройка шрифта завершена"

ask_font_name = "Введите название шрифта"
ask_font_name_or_num = "Введите название шрифта, или нажмите ниже, чтобы посмотреть список доступных шрифтов"
available_fonts_list = "Список доступных шрифтов"

ask_font_size = "Введите размер шрифта (в px, без указания единиц измерения)"
ask_font_bold = "Сделать текст жирным?"
ask_font_italic = "Сделать текст курсивом?"
ask_text_color = "Выберите цвет текста"

successful_changes = "✅ Изменение успешно применено"
invalid_input = "❌ Некорректный ввод"
invalid_font_name = "❌ Этот шрифт недоступен"
previous_file_error = "❌ Предыдущего изображения не существует"

# Главное меню бота
main_menu_title = "Главное меню бота:"
main_menu_list = ["🏞 Создать мем",
                  "🔍 Найти пикчу по названию"]

# Меню выбора источника изображения для мема
picture_source_title = "Какое изображение использовать:"
picture_source_list = ["🔙 Предыдущее",
                       "🗂 Выбрать шаблон",
                       "🆕 Загрузить новое"]

# Меню выбора способа настройки стиля текста, который будет использован
set_text_settings_title = "Выбор стиля текста"
set_text_settings_list = ["📂 Выбрать пакет",
                          "⚙ Задать вручную",
                          "✅ Использовать текущий"]

# Меню настройки стиля текста вручную
change_text_settings_title = "Настройки стиля текста"
change_text_settings_list = ["✏ Полностью задать стиль текста",
                             "🔤️ Изменить название шрифта",
                             "🔢️ Изменить размер шрифта",
                             "🔲️ Изменить жирность шрифта",
                             "🔳️ Изменить курсив шрифта",
                             "🟢 Изменить цвет текста"]

# Меню выбора цвета
text_colors_title = "Доступные цвета:"
text_colors_list = ["⚫ Черный",
                    "⚪ Белый",
                    "🔴 Красный",
                    "🟠 Оранжевый",
                    "🟡 Желтый",
                    "🟢 Зелёный",
                    "🔵 Синий",
                    "🟣 Фиолетовый",
                    "Ещё ➡"]
users_color = "Заданный пользователем"
arbitrary_color_instruction = "Чтобы задать произвольный цвет, перейдите на сайт: https://colorscheme.ru/color-converter.html. При помощи палитры выберите нужный цвет и скопируйте его кодировку в rgb формате. Например: (0, 0, 0)"

# Меню настройки расположения текста
text_pos_menu_title = "Расположение текста"
text_pos_menu_list = ["↔ По центру картинки",
                      "➡ Задать вручную"]

text_rotation_menu_title = "Угол поворота текста"
set_text_rotation_manually = "➡ Задать вручную"
ask_text_rotation = "Введите угол поворота текста в градусах"

cts_finish_menu_continue = "➡ Продолжить настройку"
use_this_template = "✅ Использовать этот шаблон"
choose_another_template = "🔄 Выбрать другой"
sp_finish_continue = "🔄 Получить ещё пикчу"
back_to_main = "↩ Вернуться в главное меню"
back = "⬅ Назад"
next_step = "Что делать дальше:"

available_packs = "Доступные пакеты:"

send_picture_to_me = "Отправьте картинку и текст, который необходимо на неё наложить"
send_mem_text_to_me = "Введите текст, который будет наложен на картинку"
send_mem_text_to_me_2 = send_mem_text_to_me + " ещё раз"

send_text_pos_in_px = "Введите координаты по горизонтали и по вертикали для верхнего левого угла текста через пробел, в px"
send_text_pos_in_per = "Введите координаты по горизонтали и по вертикали для середины текста через пробел, в %"

# Меню выбора пакета настроек
pack_choice_title = "Выберите пакет настроек:"
pack_choice_success = "Пакет настроек успешно применён"

# Задания позиции текста в px / в %
set_text_pos_title = "Формат ввода координат текста"
# Кнопки
set_text_pos_in_px = "Абсолютно, в px"
set_text_pos_in_percents = "Относительно, в %"

# Ответы на ввод
successful_input = "✅ ОК"
pos_out_of_range = "Выход за границу изображения"


def ask_picture_number(quantity_of_pictures):
    return f"Введите число от 1 до {quantity_of_pictures} - номер пикчи"


def ask_template_number(quantity_of_templates):
    return f"Введите число от 1 до {quantity_of_templates} - номер шаблона"


def max_text_len_info(text_len):
    return f"Макс. длина текста {text_len} симв."


def user_pict_size(size):
    return f"Размеры Вашей картинки {size}, в px"


not_understand = "Напишите /menu, чтобы активировать главное меню"

database_error = "Бот был перезапущен. Ваши настройки не сохранены"
