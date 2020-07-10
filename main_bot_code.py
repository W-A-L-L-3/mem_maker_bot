# Главный код бота
import os  # Модуль для создания и удаления папок (в данном случае)
from shutil import copy  # Ф-ция для копирования файлов
import telebot  # Модуль для работы с telegram ботами
import pygame  # Модуль для работы наложения текста на картинку (в данном случае)
import pickle  # Модуль для работы с файлами
from bottoken import TOKEN  # Мой токен из файла
import phrases  # Фразы для диалога
import constants  # Константные величины
import names  # Файл с названиями пикч и шаблонов

pygame.init()  # Инициализация модуля pygame

bot = telebot.TeleBot(TOKEN)  # Создаём бота

# Клавиатура да / нет
yesno_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
yesno_keyboard.add(telebot.types.KeyboardButton(text="да"), telebot.types.KeyboardButton(text="нет"))


# =====================РАБОТА С ФАЙЛАМИ=======================
def read_data_file(chat_id):
    """Открытие файла с пользовательскими данными и выгрузка их из файла в переменные"""
    with open(f"users/{chat_id}/data", 'rb') as data_file:
        user_data = pickle.load(data_file)
    # print('read', chat_id, user_data)  # Вывод для тестов
    return user_data


def rewrite_data_file(chat_id, user_data):
    """Открытие файла с пользовательскими данными и загрузка их из переменных в файл"""
    with open(f"users/{chat_id}/data", 'wb') as data_file:
        pickle.dump(user_data, data_file)
    # print('rewrite', chat_id, user_data)  # Вывод для тестов


def del_user_file(chat_id, name):
    """
    Удаление файла пользователя (исходника или готового мема, в зависимости от name)
    name - answer / source
    """
    os.remove(f"users/{chat_id}/img/{name}_picture.jpg")


# =====================ФУНКЦИИ=======================
def is_2_digit(string):
    """Проверка на корректность ввода. Должны быть введены 2 целых числа"""
    lst = string.strip().split()
    return len(lst) == 2 and lst[0].isdigit() and lst[1].isdigit()


def final_send_picture(chat_id):
    """
    1) Создание мема с пользовательскими настройками
    2) Отправка этого мема
    3) Удаление отправленного файла из папки пользователя
    4) Вызов главного меню
    """
    create_mem_with_user_settings(chat_id)
    send_mem(chat_id)
    del_user_file(chat_id, "answer")
    mode = "None"
    step = 0
    active_menu = 0
    main_menu(chat_id)

    return mode, step, active_menu


# ======================PYGAME========================
def create_mem(chat_id, text, text_style, text_position):
    """
    Наложение текста с заданным пользователем стилем на тестовую картинку.
    chat_id - id пользователя / чата
    text - текст, который будет отрисован
    font_style - список со стилем текста (название, размер, жирность, курсив)
    text_color - цвет текста в rgb
    text_position - позиция текста в формате (format, x, y),  format - рх / percent, x и y - координаты текста в int
    """
    font = pygame.font.SysFont(*text_style[:-1])  # Создание шрифта
    text_object = font.render(text, 1, text_style[-1])  # Создание объекта текста
    image = pygame.image.load(f"users/{chat_id}/img/source_picture.jpg")  # Загружаем картинку
    size = image.get_size()  # Размеры картинки
    screen = pygame.Surface(size)  # Создаём рабочее поле с размерами картинки

    coords_format, x, y = text_position  # Распаковываем text_position
    if coords_format == "px":  # Если x и y заданы в px
        # i, j = x - text_object.get_size()[0], y - text_object.get_size()[1]
        i, j = x, y  # Координаты верхнего левого угла текста
    elif coords_format == "percent":  # Если x и y заданы в %
        # Координаты центра текста
        i = (size[0] * x) // 100 - text_object.get_width() // 2
        j = (size[1] * y) // 100 - text_object.get_height() // 2
    else:  # Если произошла какая-то ошибка, и format не px и не percent
        raise ValueError("Ошибка в формате координат")

    image.blit(text_object, (i, j))  # Отрисовка текста на картинке
    screen.blit(image, (0, 0))  # Отрисовка картинки на рабочем поле, верхний левый угол в (0, 0)
    pygame.image.save(screen, f"users/{chat_id}/img/answer_picture.jpg")  # Сохраняем всё рабочее поле в новый файл


def create_mem_with_user_settings(chat_id):
    """Создание мема с пользовательскими настройками стиля текста и его координат"""
    user_data = read_data_file(chat_id)
    create_mem(chat_id, user_data[5], user_data[3], user_data[4])


def send_mem(chat_id):
    """Отправка файла с мемом пользователю"""
    with open(f"users/{chat_id}/img/answer_picture.jpg", 'rb') as photo:
        bot.send_photo(chat_id, photo)


def send_picture(chat_id, folder_name, name):
    """
    Отправка файла с пикчей или шаблоном, в зависимости от folder_name, пользователю
    folder_name - имя папки (pictures / templates)
    name - имя файла (без порядкового номера и расширения)
    """
    with open(f"img/{folder_name}/{name}.jpg", 'rb') as photo:
        bot.send_photo(chat_id, photo)


def get_user_img_size(chat_id):
    """Получение размеров отправленной пользователем картинки"""
    image = pygame.image.load(f"users/{chat_id}/img/source_picture.jpg")  # Загружаем картинку
    return image.get_size()


# ======================ЗАПРОСЫ ПАРАМЕТРОВ ТЕКСТА========================
def get_font_name(message, user_message, step):
    """Запрос названия шрифта"""
    if user_message in pygame.font.get_fonts():  # Если введённый шрифт есть в наборе шрифтов pygame
        if step == 1:  # Если находимся в режиме полной настройки, переходим к след. вопросу
            bot.send_message(message.chat.id, phrases.ask_font_size)
        else:  # Если находимся в режиме индивидуальной настройки, сообщ., что изменения применены
            bot.send_message(message.chat.id, phrases.successful_changes)
        return user_message, (2 if step == 1 else 0)
    else:
        bot.send_message(message.chat.id, phrases.invalid_font_name)
        return -1, step


def get_font_size(message, user_message, step):
    """Запрос размера шрифта"""
    global yesno_keyboard
    if user_message.isdigit() \
            and 0 < int(user_message) < constants.max_font_size:  # Если ввели корректно, запоминаем и идём дальше
        if step == 2:  # Если находимся в режиме полной настройки, переходим к след. вопросу и вкл. yesno клаву
            bot.send_message(message.chat.id, text=phrases.ask_font_bold, reply_markup=yesno_keyboard)
        else:  # Если находимся в режиме индивидуальной настройки, сообщ., что изменения применены
            bot.send_message(message.chat.id, phrases.successful_changes)
        return int(user_message), (3 if step == 2 else 0)
    else:
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step


def get_font_bold(message, user_message, step):
    """Запрос жирности шрифта"""
    # Если ввели корректно, запоминаем и идём дальше
    if user_message in ('да', 'нет'):
        if step == 3:  # Если находимся в режиме полной настройки, переходим к след. вопросу
            bot.send_message(message.chat.id, phrases.ask_font_italic)
        else:  # Если находимся в режиме индивидуальной настройки, сообщ., что изменения применены и выкл. yesno клаву
            bot.send_message(message.chat.id, phrases.successful_changes,
                             reply_markup=telebot.types.ReplyKeyboardRemove())
        return True if user_message == 'да' else False, (4 if step == 3 else 0)
    else:
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step


def get_font_italic(message, user_message, step):
    """Запрос курсивности (если есть такое слово) шрифта"""
    # Если ввели корректно, запоминаем и идём дальше
    if user_message in ('да', 'нет'):
        if step == 4:  # Если находимся в режиме полной настройки, переходим к след. вопросу
            bot.send_message(message.chat.id, phrases.successful_changes,
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            text_color_menu(message.chat.id)
        else:  # Если находимся в режиме индивидуальной настройки, сообщ., что изменения применены и выкл. yesno клаву
            bot.send_message(message.chat.id, phrases.successful_changes,
                             reply_markup=telebot.types.ReplyKeyboardRemove())
        return (True if user_message == 'да' else False), (5 if step == 4 else 0), (9 if step == 4 else 10)
    else:
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step, -1


def color_to_rgb(color):
    """Проверка строки с цветом на корректность и перевод цвета в 3 переменные."""
    correct = (color[0] == '(' and color[-1] == ')' and len(color[1:-1].split(', ')) == 3 and
               color[1:-1].split(', ')[0].isdigit() and 0 <= int(color[1:-1].split(', ')[0]) <= 255 and
               color[1:-1].split(', ')[1].isdigit() and 0 <= int(color[1:-1].split(', ')[1]) <= 255 and
               color[1:-1].split(', ')[2].isdigit() and 0 <= int(color[1:-1].split(', ')[2]) <= 255)
    if correct:
        r, g, b = map(int, color[1:-1].split(', '))
    else:
        r, g, b = 0, 0, 0
    return correct, r, g, b


def get_text_color(message, user_message, step):
    """Запрос цвета текста"""
    # Если ввели корректно, запоминаем и идём дальше
    correct, r, g, b = color_to_rgb(user_message)
    if correct:
        if step == 4:  # Если находимся в режиме полной настройки, сообщ., что настройка завершена
            bot.send_message(message.chat.id, phrases.font_setting_off)
        else:  # Если находимся в режиме индивидуальной настройки, сообщ., что изменения применены
            bot.send_message(message.chat.id, phrases.successful_changes)
        return tuple((r, g, b)), 0
    else:
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step


def rgb_to_name(rgb):
    """Возвращает название цвета по его rgb кодировке"""
    convert_dict = {(0, 0, 0): phrases.text_colors_list[0][2:],
                    (255, 255, 255): phrases.text_colors_list[1][2:],
                    (255, 0, 0): phrases.text_colors_list[2][2:],
                    (255, 145, 0): phrases.text_colors_list[3][2:],
                    (255, 255, 0): phrases.text_colors_list[4][2:],
                    (72, 255, 0): phrases.text_colors_list[5][2:],
                    (0, 81, 255): phrases.text_colors_list[6][2:],
                    (159, 0, 191): phrases.text_colors_list[7][2:]}

    return convert_dict.get(rgb, 'Заданный пользователем')


def get_current_text_style(chat_id):
    """Получение текущего стиля текста из файла с настройками"""
    user_data = read_data_file(chat_id)
    text_style = user_data[3]
    ans = "Текущий стиль текста: \n"
    ans += f"Нaзвание шрифта: {text_style[0]} \n"
    ans += f"Размер шрифта: {text_style[1]} \n"
    ans += f"Жирный шрифт: {'да' if text_style[2] else 'нет'} \n"
    ans += f"Курсив шрифта: {'да' if text_style[3] else 'нет'} \n"
    ans += f"Цвет текста: {rgb_to_name(text_style[4])}"
    return ans


# ======================МЕНЮ========================
def cts_finish_menu(chat_id):
    """Меню после настройки текста вручную"""
    ctsf_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру

    # Добавляем все ф-ции в меню
    ctsf_menu.add(
        telebot.types.InlineKeyboardButton(text=phrases.cts_finish_menu_continue, callback_data='cts_finish_menu_1'))
    ctsf_menu.add(
        telebot.types.InlineKeyboardButton(text=phrases.back_to_main, callback_data='cts_finish_menu_2'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.next_step, reply_markup=ctsf_menu)


def text_color_menu(chat_id):
    """Меню настройки цвета текста"""
    tc_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.text_colors_list)):
        tc_menu.add(
            telebot.types.InlineKeyboardButton(text=phrases.text_colors_list[i],
                                               callback_data=f'text_color_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.text_colors_title, reply_markup=tc_menu)


def change_text_settings_menu(chat_id):
    """Меню настройки стиля текста вручную"""
    cts_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.change_text_settings_list)):
        cts_menu.add(
            telebot.types.InlineKeyboardButton(text=phrases.change_text_settings_list[i],
                                               callback_data=f'change_text_settings_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.change_text_settings_title, reply_markup=cts_menu)


def pack_choice_menu(chat_id):
    """Меню выбора пакета настроек стиля текста"""
    bot.send_message(chat_id, text=phrases.available_packs)
    # Отправляем все варианты пакетов
    with open("img/five_packs.jpg", 'rb') as photo:
        bot.send_photo(chat_id, photo)

    pc_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    n = 5
    for i in range(1, n + 1):
        pc_menu.add(
            telebot.types.InlineKeyboardButton(text=f"Пакет настроек № {i}", callback_data=f'pack_choice_menu_{i}'))
    pc_menu.add(telebot.types.InlineKeyboardButton(text=phrases.back, callback_data=f'pack_choice_menu_{n + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.pack_choice_title, reply_markup=pc_menu)


def set_text_settings_menu(chat_id):
    """Меню выбора способа настройки стиля текста, который будет использован"""
    sts_menu = telebot.types.InlineKeyboardMarkup()
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.set_text_settings_list)):
        sts_menu.add(telebot.types.InlineKeyboardButton(text=phrases.set_text_settings_list[i],
                                                        callback_data=f'set_text_settings_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.set_text_settings_title, reply_markup=sts_menu)


def text_style_choice_menu(chat_id):
    """Меню выбора стиля текста, который будет использован"""
    tsc_menu = telebot.types.InlineKeyboardMarkup()
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.text_style_choice_list)):
        tsc_menu.add(telebot.types.InlineKeyboardButton(text=phrases.text_style_choice_list[i],
                                                        callback_data=f'text_style_choice_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.text_style_choice_title, reply_markup=tsc_menu)


def text_pos_menu(chat_id):
    """Меню настройки расположения текста"""
    tp_menu = telebot.types.InlineKeyboardMarkup()
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.text_pos_menu_list)):
        tp_menu.add(telebot.types.InlineKeyboardButton(text=phrases.text_pos_menu_list[i],
                                                       callback_data=f'text_pos_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.text_pos_menu_title, reply_markup=tp_menu)


def picture_source_menu(chat_id):
    """Меню выбора источника изображения для мема"""
    create_mem_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.picture_source_list)):
        create_mem_menu.add(
            telebot.types.InlineKeyboardButton(text=phrases.picture_source_list[i],
                                               callback_data=f'picture_source_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.picture_source_title, reply_markup=create_mem_menu)


def picture_search_message(chat_id):
    """Режим поиска пикчи по названию"""
    bot.send_message(chat_id,
                     text=phrases.ask_picture_number)  # Сообщение с просьбой ввести номер пикчи
    msg = ''
    for name in names.pictures:
        msg += name
    bot.send_message(chat_id, text=msg)  # Вывод списка названий


def template_search_message(chat_id):
    """Режим выбора шаблона по названию"""
    bot.send_message(chat_id,
                     text=phrases.ask_template_number)  # Сообщение с просьбой ввести номер шаблона
    msg = ''
    for name in names.templates:
        msg += name
    bot.send_message(chat_id, text=msg)  # Вывод списка названий


def send_picture_finish_menu(chat_id):
    """Меню после настройки текста вручную"""
    sp_f_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    sp_f_menu.add(
        telebot.types.InlineKeyboardButton(text=phrases.sp_finish_continue, callback_data='send_picture_finish_menu_1'))
    sp_f_menu.add(
        telebot.types.InlineKeyboardButton(text=phrases.back_to_main, callback_data='send_picture_finish_menu_2'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.next_step, reply_markup=sp_f_menu)


def send_template_finish_menu(chat_id):
    """Меню после настройки текста вручную"""
    st_f_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    st_f_menu.add(
        telebot.types.InlineKeyboardButton(text=phrases.use_this_template, callback_data='send_template_finish_menu_1'))
    st_f_menu.add(
        telebot.types.InlineKeyboardButton(text=phrases.choose_another_template,
                                           callback_data='send_template_finish_menu_2'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.next_step, reply_markup=st_f_menu)


def main_menu(chat_id):
    """Главное меню бота"""
    m_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клавиатуру
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.main_menu_list)):
        m_menu.add(
            telebot.types.InlineKeyboardButton(text=phrases.main_menu_list[i], callback_data=f'main_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.main_menu_title, reply_markup=m_menu)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    """Обработчик нажатий на кнопки"""
    global yesno_keyboard
    user_data = read_data_file(call.message.chat.id)
    bot.answer_callback_query(callback_query_id=call.id, text='')  # Всплывающее сообщение

    if user_data[2] == 0:  # Если активно главное меню
        if call.data == 'main_menu_1':  # Если выбран пункт "Наложить текст на картинку"
            user_data[2] = 1  # Активируем меню выбора источника изображения
            picture_source_menu(call.message.chat.id)  # Выводим меню выбора источника изображения
        elif call.data == 'main_menu_2':  # Если выбран пункт "Найти пикчу по названию"
            picture_search_message(call.message.chat.id)  # Отправляем список названий пикч
            user_data[0] = "send_picture"  # Активируем режим выбора пикч
            user_data[2] = -1  # Блокируем все меню

    elif user_data[2] == 1:  # Если активно меню выбора источника изображения для мема
        if call.data == 'picture_source_menu_1':  # Если выбран пункт "Предыдущее"
            if os.path.exists(f"users/{call.message.chat.id}/img/source_picture.jpg"):  # Если предыдущее существует
                user_data[0] = "get_source"  # Активируем режим получения исходников для мема
                user_data[1] = 1  # Переходим к вводу текста пользователем
                user_data[2] = -1  # Блокируем все меню
                bot.send_message(call.message.chat.id, phrases.send_mem_text_to_me)  # Просьба отправить текст для мема
            else:  # Если предыдущего не существует, выводим соотв. предупреждение
                bot.send_message(call.message.chat.id, phrases.previous_file_error)
                picture_source_menu(call.message.chat.id)
        elif call.data == 'picture_source_menu_2':  # Если выбран пункт "Выбрать шаблон"
            template_search_message(call.message.chat.id)  # Отправляем список названий шаблонов
            user_data[0] = "send_template"  # Активируем режим выбора шаблона
            user_data[2] = -1  # Блокируем все меню
        elif call.data == 'picture_source_menu_3':  # Если выбран пункт "Загрузить новое"
            del_user_file(call.message.chat.id, "source")  # Удаляем старый исходник
            user_data[0] = "get_source"  # Активируем режим получения исходников для мема
            user_data[1] = 2  # Переходим к вводу текста и картинки пользователем
            user_data[2] = -1  # Блокируем все меню
            bot.send_message(call.message.chat.id,
                             phrases.send_picture_to_me)  # Просьба отправить текст и картинку для мема
        elif call.data == 'picture_source_menu_4':  # Если выбран пункт "Вернуться в главное меню"
            user_data[2] = 0
            main_menu(call.message.chat.id)

    elif user_data[2] == 2:  # Если активно меню после получения пикчи
        if call.data == 'send_picture_finish_menu_1':  # Если выбран пункт "Получить ещё пикчу"
            user_data[0] = "send_picture"
            user_data[2] = -1
            bot.send_message(call.message.chat.id, phrases.ask_picture_number)
        elif call.data == 'send_picture_finish_menu_2':  # Если выбран пункт "Вернуться в главное меню"
            user_data[2] = 0
            user_data[0] = "None"
            main_menu(call.message.chat.id)

    elif user_data[2] == 4:  # Если активно меню выбора источника изображения для мема
        if call.data == 'text_pos_menu_1':  # Если выбран пункт "Расположить текст по центру картинки"
            user_data[4] = ['percent', 50, 50]
            user_data[0] = "None"
            user_data[1] = 0
            user_data[2] = 6
            bot.send_message(call.message.chat.id, text=get_current_text_style(call.message.chat.id))
            set_text_settings_menu(call.message.chat.id)
        elif call.data == 'text_pos_menu_2':  # Если выбран пункт "Задать расположение текста вручную"
            user_data[0] = "get_text_pos"
            user_data[1] = 1
            # Клавиатура в px / в %
            percent_px_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            percent_px_keyboard.add(telebot.types.KeyboardButton(text=phrases.set_text_pos_in_px),
                                    telebot.types.KeyboardButton(text=phrases.set_text_pos_in_percents))
            bot.send_message(call.message.chat.id, text=phrases.set_text_pos_title, reply_markup=percent_px_keyboard)
        elif call.data == 'text_pos_menu_3':  # Если выбран пункт "Вернуться в главное меню"
            user_data[0] = "None"
            user_data[1] = 0
            user_data[2] = 0
            main_menu(call.message.chat.id)
    elif user_data[2] == 6:  # Если активно меню выбора способа настройки стиля текста, который будет использован
        if call.data == 'set_text_settings_menu_1':  # Если выбран пункт "Выбрать пакет"
            pack_choice_menu(call.message.chat.id)
            user_data[2] = 7
        elif call.data == 'set_text_settings_menu_2':  # Если выбран пункт "Задать вручную"
            change_text_settings_menu(call.message.chat.id)
            user_data[2] = 8
        elif call.data == 'set_text_settings_menu_3':  # Если выбран пункт "Использовать текущий"
            user_data[0:3] = final_send_picture(call.message.chat.id)

    elif user_data[2] == 7:  # Если активно меню выбора пакета настроек стиля текста
        if call.data.startswith('pack_choice_menu_'):
            if call.data[-1] != '6':
                user_data[3] = constants.text_setting_packs[int(call.data[call.data.rfind('_') + 1:]) - 1]
                bot.send_message(call.message.chat.id, phrases.pack_choice_success)
            rewrite_data_file(call.message.chat.id, user_data)
            bot.send_message(call.message.chat.id, text=get_current_text_style(call.message.chat.id))
            user_data[2] = 6
            set_text_settings_menu(call.message.chat.id)

    elif user_data[2] == 8:  # Если активно меню форматирования стиля текста
        if call.data.startswith('change_text_settings_menu_'):
            user_data[2] = -1  # Блокируем все меню
            if call.data[-1] != '7':
                user_data[0] = "font_settings"
        if call.data == 'change_text_settings_menu_1':
            bot.send_message(call.message.chat.id, phrases.font_setting_on)
            bot.send_message(call.message.chat.id, phrases.ask_font_name)
            user_data[1] = 1
        elif call.data == 'change_text_settings_menu_2':
            bot.send_message(call.message.chat.id, phrases.ask_font_name)
            user_data[1] = 6
        elif call.data == 'change_text_settings_menu_3':
            bot.send_message(call.message.chat.id, phrases.ask_font_size)
            user_data[1] = 7
        elif call.data == 'change_text_settings_menu_4':
            bot.send_message(call.message.chat.id, phrases.ask_font_bold, reply_markup=yesno_keyboard)
            user_data[1] = 8
        elif call.data == 'change_text_settings_menu_5':
            bot.send_message(call.message.chat.id, phrases.ask_font_italic, reply_markup=yesno_keyboard)
            user_data[1] = 9
        elif call.data == 'change_text_settings_menu_6':
            user_data[2] = 9
            user_data[1] = 10
            text_color_menu(call.message.chat.id)
        elif call.data == 'change_text_settings_menu_7':
            main_menu(call.message.chat.id)
            user_data[2] = 0

    elif user_data[2] == 9:  # Если активно меню выбора цвета
        text_color = constants.color_black
        if call.data == 'text_color_menu_1':
            text_color = constants.color_black
        elif call.data == 'text_color_menu_2':
            text_color = constants.color_white
        elif call.data == 'text_color_menu_3':
            text_color = constants.color_red
        elif call.data == 'text_color_menu_4':
            text_color = constants.color_orange
        elif call.data == 'text_color_menu_5':
            text_color = constants.color_yellow
        elif call.data == 'text_color_menu_6':
            text_color = constants.color_green
        elif call.data == 'text_color_menu_7':
            text_color = constants.color_blue
        elif call.data == 'text_color_menu_8':
            text_color = constants.color_purple
        elif call.data == 'text_color_menu_9':
            with open(f"img/colorsheme.jpg", 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption=phrases.arbitrary_color_instruction)

        if call.data.startswith('text_color_menu_') and int(call.data[-1]) < 9:
            if user_data[0] == "font_settings":
                user_data[1] = 0
                user_data[0] = "None"
            user_data[2] = 10
            cts_finish_menu(call.message.chat.id)
            user_data[3][4] = text_color

    elif user_data[2] == 10:  # Если активно меню выбора способа настройки стиля текста, который будет использован
        if call.data == 'cts_finish_menu_1':
            bot.send_message(call.message.chat.id, get_current_text_style(call.message.chat.id))
            set_text_settings_menu(call.message.chat.id)
            user_data[2] = 6
        elif call.data == 'cts_finish_menu_2':
            user_data[0] = "None"
            user_data[1] = 0
            user_data[2] = 0
            main_menu(call.message.chat.id)

    elif user_data[2] == 11:  # Если активно меню выбора шаблона
        if call.data == "send_template_finish_menu_1":
            user_data[0] = "get_source"
            user_data[1] = 1
            user_data[2] = -1
            bot.send_message(call.message.chat.id, phrases.send_mem_text_to_me)
        elif call.data == "send_template_finish_menu_2":
            user_data[2] = -1
            user_data[0] = "send_template"
            bot.send_message(call.message.chat.id, phrases.ask_template_number)

    rewrite_data_file(call.message.chat.id, user_data)  # Перезапись обновлённого списка с настройками пользователя


# ======================ОБРАБОТКА КОМАНД========================
@bot.message_handler(commands=['menu'])
def menu(message):
    """Показываем главное меню"""
    user_data = read_data_file(message.chat.id)
    user_data[0] = "None"
    user_data[1] = 0
    user_data[2] = 0  # Активируем главное меню
    rewrite_data_file(message.chat.id, user_data)
    main_menu(message.chat.id)  # Показываем главное меню


@bot.message_handler(commands=['start'])
def start(message):
    """Показываем главное меню, создаём папку пользователя и сохраняем туда стандартные настройки"""
    user_id = message.chat.id  # id пользователя (чата)
    # Создаём персональную папку
    try:
        os.mkdir(f'users/{user_id}')  # Путь к папке для данного пользователя (имя папки - id пользователя (чата))
        os.mkdir(f'users/{user_id}/img')  # Путь к папке с картинками данного пользователя
    except OSError:
        pass
        # print("Ошибка во время создания папки или папка для этого пользователя уже создана")
    else:
        pass
        # print("Папка успешно создана")

    # Инициализируем формат пользовательски настроек
    user_data = [0, 0, 0, 0, 0, 0]
    user_data[0] = "None"  # mode - режим работы бота
    user_data[1] = 0  # step - номер шага в данном режиме работы бота
    user_data[2] = 0  # active_menu - активное в данный момент меню
    user_data[3] = constants.standard_text_setting  # text_style - стиль текста
    user_data[4] = constants.standard_text_position  # text_position - позиция текста
    user_data[5] = ''  # source_text - текст, который ввел пользователь
    # Записываем в файл с пользовательскими настройками стандартные настройки
    rewrite_data_file(user_id, user_data)

    bot.send_message(message.chat.id, text=phrases.first_msg)  # Отправляем сообщение с приветствием
    main_menu(message.chat.id)  # Показываем главное меню


# ======================ОБРАБОТКА ПОЛЬЗОВАТЕЛЬСКИХ СООБЩЕНИЙ========================
@bot.message_handler(content_types=['photo'])
def handle_start_help(message):
    """Обработка всех сообщений с картинкой"""
    user_data = read_data_file(message.chat.id)
    # Если включен режим получения исходников для мема и нужно считать картинку
    if user_data[0] == "get_source" and user_data[1] == 2:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        source_picture = f"users/{message.chat.id}/img/source_picture.jpg"
        with open(source_picture, 'wb') as new_file:
            new_file.write(downloaded_file)
        user_message = message.caption  # Подпись к картинке
        if isinstance(user_message, str):  # Подпись к картинке есть
            if 0 <= len(user_message) <= constants.max_mem_text_len:  # Если её длина не больше макс. длины текста
                user_data[5] = user_message
                user_data[0] = "None"
                user_data[1] = 0
                user_data[2] = 4
                text_pos_menu(message.chat.id)
            else:
                user_data[1] = 1
                bot.send_message(message.chat.id, text=f"Макс. длина текста {constants.max_mem_text_len} симв.")
                bot.send_message(message.chat.id, phrases.send_mem_text_to_me + ', ещё раз')
        else:
            user_data[1] = 1
            bot.send_message(message.chat.id, phrases.send_mem_text_to_me)
        rewrite_data_file(message.chat.id, user_data)  # Перезапись обновлённого списка с настройками пользователя


@bot.message_handler(content_types=["text"])
def processing_all_text_messages(message):
    """Обработка всех текстовых сообщений"""
    user_data = read_data_file(message.chat.id)
    user_message = message.text  # Сообщение пользователя

    if user_data[0] == "font_settings":  # Если включен режим ввода параметров шрифта
        user_message = user_message.lower()  # Преобразуем все буквы сообщения в нижний регистр
        if user_data[1] == 1 or user_data[1] == 6:  # Если название шрифта ещё не введено
            user_data[3][0], user_data[1] = get_font_name(message, user_message, user_data[1])
        elif user_data[1] == 2 or user_data[1] == 7:  # Если размер шрифта ещё не введён
            user_data[3][1], user_data[1] = get_font_size(message, user_message, user_data[1])
        elif user_data[1] == 3 or user_data[1] == 8:  # Если жирность шрифта ещё не введена
            user_data[3][2], user_data[1] = get_font_bold(message, user_message, user_data[1])
        elif user_data[1] == 4 or user_data[1] == 9:  # Если курсивность шрифта ещё не введена
            user_data[3][3], user_data[1], user_data[2] = get_font_italic(message, user_message, user_data[1])
        elif user_data[1] == 5 or user_data[1] == 10:  # Если цвет текста ещё не введён
            user_data[3][4], user_data[1] = get_text_color(message, user_message, user_data[1])

        if user_data[1] == 0:  # Если настройка завершена
            user_data[0] = "None"
            user_data[2] = 6  # Активируем меню завершения настройки текста
            rewrite_data_file(message.chat.id, user_data)
            bot.send_message(message.chat.id, text=get_current_text_style(message.chat.id))
            set_text_settings_menu(message.chat.id)

    elif user_data[0] == "get_source":  # Если включен режим получения исходников для мема
        if user_data[1] == 1:
            if 0 <= len(user_message) <= constants.max_mem_text_len:
                user_data[5] = user_message
                user_data[0] = "None"
                user_data[1] = 0
                user_data[2] = 4
                text_pos_menu(message.chat.id)
            else:
                bot.send_message(message.chat.id, text=f"Макс. длина текста {constants.max_mem_text_len} симв.")
                bot.send_message(message.chat.id, phrases.send_mem_text_to_me + ', ещё раз')

    elif user_data[0] == "get_text_pos":  # Если включен режим получения позиции текста
        if user_data[1] == 1:
            if user_message == phrases.set_text_pos_in_px:
                image = pygame.image.load(f"users/{message.chat.id}/img/source_picture.jpg")  # Загружаем картинку
                bot.send_message(message.chat.id, f'Размеры Вашей картинки {image.get_size()}, в px')
                bot.send_message(message.chat.id, phrases.send_text_pos_to_me + "px",
                                 reply_markup=telebot.types.ReplyKeyboardRemove())
                user_data[1] = 2
            elif user_message == phrases.set_text_pos_in_percents:
                bot.send_message(message.chat.id, phrases.send_text_pos_to_me + "%",
                                 reply_markup=telebot.types.ReplyKeyboardRemove())
                user_data[1] = 3
            else:
                bot.send_message(message.chat.id, phrases.invalid_input)

        elif user_data[1] == 2 or user_data[1] == 3:
            x_max, y_max = get_user_img_size(message.chat.id)
            if is_2_digit(user_message):
                x, y = map(int, user_message.split())
                if user_data[1] == 2:
                    if 0 < x < x_max and 0 < y < y_max:
                        bot.send_message(message.chat.id, text=phrases.successful_input)
                        user_data[0] = "None"
                        user_data[1] = 0
                        user_data[4] = ['px', x, y]
                        user_data[2] = 6
                        bot.send_message(message.chat.id, text=get_current_text_style(message.chat.id))
                        set_text_settings_menu(message.chat.id)
                    else:
                        bot.send_message(message.chat.id, text=phrases.pos_out_of_range)
                else:
                    if 0 < x < 100 and 0 < y < 100:
                        user_data[0] = "None"
                        user_data[1] = 0
                        user_data[4] = ['percent', x, y]
                        user_data[2] = 6
                        bot.send_message(message.chat.id, text=get_current_text_style(message.chat.id))
                        set_text_settings_menu(message.chat.id)
                    else:
                        bot.send_message(message.chat.id, text=phrases.pos_out_of_range)
            else:
                bot.send_message(message.chat.id, text=phrases.invalid_input)

    elif user_data[0] == "send_picture":  # Если включён режим отправки пикчи
        if not user_message.isdigit() or int(user_message) == 0 or int(user_message) > len(
                names.pictures):  # Проверка на корректность
            bot.send_message(message.chat.id, text=phrases.invalid_input)
        else:
            picture = str(names.pictures[int(user_message) - 1])
            picture_name = picture[picture.find(' ') + 1:]
            bot.send_message(message.chat.id, text=picture_name)  # Отправка названия
            send_picture(message.chat.id, "pictures", picture_name[:-1])  # Отправка пикчи
            user_data[2] = 2
            user_data[0] = "None"
            send_picture_finish_menu(message.chat.id)

    elif user_data[0] == "send_template":  # Если включён режим отправки шаблона
        if not user_message.isdigit() or int(user_message) == 0 or int(user_message) > len(
                names.templates):  # Проверка на корректность
            bot.send_message(message.chat.id, text=phrases.invalid_input)
        else:
            template = str(names.templates[int(user_message) - 1])
            template_name = template[template.find(' ') + 1:]
            bot.send_message(message.chat.id, text=template_name)  # Отправка названия
            send_picture(message.chat.id, "templates", template_name[:-1])  # Отправка пикчи
            copy(f'img/templates/{template_name[:-1]}.jpg', f'users/{message.chat.id}/img/source_picture.jpg')
            user_data[2] = 11
            user_data[0] = "None"
            send_template_finish_menu(message.chat.id)
    else:  # Если введено непонятно что
        bot.send_message(message.chat.id, phrases.not_understand)

    rewrite_data_file(message.chat.id, user_data)


if __name__ == '__main__':  # Запуск
    bot.polling(none_stop=True)
