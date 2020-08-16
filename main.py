# Главный код бота

import telebot  # Модуль для работы с telegram ботами

import mmbdatabase  # Модуль для работы с базой данных
import mmbpicture  # Модуль для создания мема
import mmbfiles  # Модуль для работы с файлами

from bottoken import TOKEN  # Мой токен из файла
import phrases  # Фразы для диалога
import constants  # Константные величины
import names  # Файл с названиями пикч и шаблонов

bot = telebot.TeleBot(TOKEN)  # Создаём бота

database = mmbdatabase.Database(file_name="database.xlsx")  # Объект базы

# Клавиатура да / нет
yesno_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2,
                                                   resize_keyboard=True)
yesno_keyboard.add(telebot.types.KeyboardButton(text=phrases.yes),
                   telebot.types.KeyboardButton(text=phrases.no))


# =====================ФУНКЦИИ=======================
def is_2_digit(string):
    """Проверка на корректность ввода. Должны быть введены 2 целых числа"""
    lst = string.strip().split()
    correct = len(lst) == 2 and len(list(filter(str.isdigit, lst))) == 2
    if correct:
        x, y = map(int, string.split())
    else:
        x = y = 0
    return correct, x, y


def color_to_rgb(color):
    """Проверка строки с rgb кодировкой и перевод цвета в кортеж из 3х знач."""

    def check(x):
        return x.isdigit() and 0 <= int(x) <= 255

    correct = bool(color[0] == "(" and color[-1] == ")" and
                   len(list(filter(check, color[1:-1].split(', ')))) == 3)
    if correct:
        rgb = tuple(map(int, color[1:-1].split(', ')))
    else:
        rgb = (0, 0, 0)
    return correct, rgb


def create_mem_with_user_settings(message):
    """Создание мема с пользовательскими настройками"""
    data, reset = mmbfiles.read_data(message, bot.send_message, start)
    mmbpicture.create_mem(message.chat.id, data[5], data[3], data[4])


def send_mem(chat_id):
    """Отправка файла с мемом пользователю"""
    with open(f"users/{chat_id}/img/answer_picture.jpg", 'rb') as photo:
        bot.send_photo(chat_id, photo)


def send_picture(chat_id, folder_name, name):
    """
    Отправка файла с пикчей или шаблоном, в зависимости от folder_name
    folder_name - имя папки (pictures / templates)
    name - имя файла (без порядкового номера и расширения)
    """
    with open(f"img/{folder_name}/{name}.jpg", 'rb') as photo:
        bot.send_photo(chat_id, photo)


# ======================ЗАПРОСЫ ПАРАМЕТРОВ ТЕКСТА========================
def get_font_name(message, user_message, step):
    """Запрос названия шрифта"""
    # Есть ли введённого шрифта нет в наборе шрифтов pygame
    if user_message not in mmbpicture.pygame_fonts:
        bot.send_message(message.chat.id, phrases.invalid_font_name)
        return -1, step

    if step == 1:  # Режим полной настройки - след. вопрос
        bot.send_message(message.chat.id, phrases.ask_font_size)
    else:  # Режим индивидуальной настройки - изменения применены
        bot.send_message(message.chat.id, phrases.successful_changes)
    return user_message, (2 if step == 1 else 0)


def get_font_size(message, user_message, step):
    """Запрос размера шрифта"""
    global yesno_keyboard
    is_correct = user_message.isdigit()
    size = 30
    if is_correct:
        size = int(user_message)
        is_correct = 0 < size < constants.max_font_size
    # Если ввод некорректен
    if not is_correct:
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step

    if step == 2:  # Режим полной настройки - след. вопрос и вкл. yesno клаву
        bot.send_message(message.chat.id, text=phrases.ask_font_bold,
                         reply_markup=yesno_keyboard)
    else:  # Режим индивидуальной настройки - изменения применены
        bot.send_message(message.chat.id, phrases.successful_changes)

    return size, (3 if step == 2 else 0)


def get_font_bold(message, user_message, step):
    """Запрос жирности шрифта"""
    # Если ввод некорректен
    if user_message not in (phrases.yes, phrases.no):
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step

    if step == 3:  # Режим полной настройки - след. вопрос
        bot.send_message(message.chat.id, phrases.ask_font_italic)
    else:  # Режим индивид. настройки - изменения применены и выкл. yesno клаву
        bot.send_message(message.chat.id, phrases.successful_changes,
                         reply_markup=telebot.types.ReplyKeyboardRemove())

    return user_message == phrases.yes, (4 if step == 3 else 0)


def get_font_italic(message, user_message, step):
    """Запрос курсивности (если есть такое слово) шрифта"""
    # Если ввод некорректен
    if user_message not in (phrases.yes, phrases.no):
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step, -1

    if step == 4:  # Режим полной настройки - след. вопрос
        bot.send_message(message.chat.id, phrases.ask_text_color,
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        text_color_menu(message.chat.id)
    else:  # Режим индивид. настройки - изменения применены и выкл. yesno клаву
        bot.send_message(message.chat.id, phrases.successful_changes,
                         reply_markup=telebot.types.ReplyKeyboardRemove())

    return user_message == phrases.yes, (5 if step == 4 else 0), \
           (9 if step == 4 else 10)


def get_text_color(message, user_message, step):
    """Запрос цвета текста"""
    correct, rgb = color_to_rgb(user_message)
    # Если ввод некорректен
    if not correct:
        bot.send_message(message.chat.id, phrases.invalid_input)
        return -1, step

    if step == 5:  # Режим полной настройки - настройка завершена
        bot.send_message(message.chat.id, phrases.font_setting_off)
    else:  # Режим индивидуальной настройки - изменения применены
        bot.send_message(message.chat.id, phrases.successful_changes)
    return rgb, 0


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

    return convert_dict.get(rgb, phrases.users_color)


def get_current_text_style(message):
    """Получение текущего стиля текста из файла с настройками"""
    user_data, reset = mmbfiles.read_data(message, bot.send_message, start)
    text_style = user_data[3]
    ans = "Текущий стиль текста: \n"
    ans += f"Название шрифта: {text_style[0]} \n"
    ans += f"Размер шрифта: {text_style[1]} \n"
    ans += f"Жирный шрифт: {'да' if text_style[2] else 'нет'} \n"
    ans += f"Курсив шрифта: {'да' if text_style[3] else 'нет'} \n"
    ans += f"Цвет текста: {rgb_to_name(text_style[4])}"
    return ans


# ======================МЕНЮ========================

def text_color_menu(chat_id):
    """Меню настройки цвета текста"""
    tc_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.text_colors_list)):
        tc_menu.add(telebot.types.InlineKeyboardButton(
            text=phrases.text_colors_list[i],
            callback_data=f'text_color_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.text_colors_title,
                     reply_markup=tc_menu)


def change_text_settings_menu(chat_id):
    """Меню настройки стиля текста вручную"""
    cts_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.change_text_settings_list)):
        cts_menu.add(telebot.types.InlineKeyboardButton(
            text=phrases.change_text_settings_list[i],
            callback_data=f'change_text_settings_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.change_text_settings_title,
                     reply_markup=cts_menu)


def pack_choice_menu(chat_id):
    """Меню выбора пакета настроек стиля текста"""
    bot.send_message(chat_id, text=phrases.available_packs)
    # Отправляем все варианты пакетов
    with open("img/five_packs.jpg", 'rb') as photo:
        bot.send_photo(chat_id, photo)

    pc_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    n = 5
    for i in range(1, n + 1):
        pc_menu.add(telebot.types.InlineKeyboardButton(
            text=f"Пакет настроек № {i}",
            callback_data=f'pack_choice_menu_{i}'))
    pc_menu.add(telebot.types.InlineKeyboardButton(
        text=phrases.back,
        callback_data=f'pack_choice_menu_{n + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.pack_choice_title,
                     reply_markup=pc_menu)


def set_text_settings_menu(chat_id):
    """Меню выбора способа настройки стиля текста, который будет использован"""
    sts_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.set_text_settings_list)):
        sts_menu.add(telebot.types.InlineKeyboardButton(
            text=phrases.set_text_settings_list[i],
            callback_data=f'set_text_settings_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.set_text_settings_title,
                     reply_markup=sts_menu)


def text_pos_menu(chat_id):
    """Меню настройки расположения текста"""
    tp_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.text_pos_menu_list)):
        tp_menu.add(telebot.types.InlineKeyboardButton(
            text=phrases.text_pos_menu_list[i],
            callback_data=f'text_pos_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.text_pos_menu_title,
                     reply_markup=tp_menu)


def picture_source_menu(chat_id):
    """Меню выбора источника изображения для мема"""
    create_mem_menu = telebot.types.InlineKeyboardMarkup()
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.picture_source_list)):
        create_mem_menu.add(
            telebot.types.InlineKeyboardButton(
                text=phrases.picture_source_list[i],
                callback_data=f'picture_source_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.picture_source_title,
                     reply_markup=create_mem_menu)


def picture_search_message(chat_id):
    """Режим поиска пикчи по названию"""
    # Просьба ввести номер пикчи
    bot.send_message(
        chat_id, text=phrases.ask_picture_number(names.quantity_of_pictures))
    msg = ''
    for name in names.pictures:
        msg += name
    bot.send_message(chat_id, text=msg)  # Вывод списка названий


def template_search_message(chat_id):
    """Вывод списка названий шаблонов"""
    bot.send_message(
        chat_id, text=phrases.ask_template_number(names.quantity_of_templates))
    msg = ''
    for name in names.templates:
        msg += name
    bot.send_message(chat_id, text=msg)  # Вывод списка названий


def send_picture_finish_menu(chat_id):
    """Меню после отправки пикчи"""
    sp_f_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    sp_f_menu.add(telebot.types.InlineKeyboardButton(
        text=phrases.sp_finish_continue,
        callback_data='send_picture_finish_menu_1'))
    sp_f_menu.add(telebot.types.InlineKeyboardButton(
        text=phrases.back_to_main,
        callback_data='send_picture_finish_menu_2'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.next_step, reply_markup=sp_f_menu)


def send_template_finish_menu(chat_id):
    """Меню после отправки шаблона"""
    st_f_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    st_f_menu.add(telebot.types.InlineKeyboardButton(
        text=phrases.use_this_template,
        callback_data='send_template_finish_menu_1'))
    st_f_menu.add(telebot.types.InlineKeyboardButton(
        text=phrases.choose_another_template,
        callback_data='send_template_finish_menu_2'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.next_step, reply_markup=st_f_menu)


def main_menu(chat_id):
    """Главное меню бота"""
    m_menu = telebot.types.InlineKeyboardMarkup()  # Создаём inline клаву
    # Добавляем все ф-ции в меню
    for i in range(len(phrases.main_menu_list)):
        m_menu.add(telebot.types.InlineKeyboardButton(
            text=phrases.main_menu_list[i],
            callback_data=f'main_menu_{i + 1}'))
    # Отправляем сообщение с инфой о меню и списком ф-ций
    bot.send_message(chat_id, text=phrases.main_menu_title, reply_markup=m_menu)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    """Обработчик нажатий на кнопки"""
    global yesno_keyboard
    user_data, reset = mmbfiles.read_data(call.message, bot.send_message, start)
    if reset:  # Если настройки были сброшены, обнуляем нажатие на кнопку
        call.data = ""
    # Пустое всплывающее сообщение
    bot.answer_callback_query(callback_query_id=call.id, text='')

    if user_data[2] == 0:  # Главное меню
        if call.data == 'main_menu_1':  # Пункт "Наложить текст на картинку"
            # Меню выбора источника изображения
            user_data[2] = 1
            picture_source_menu(call.message.chat.id)
        elif call.data == 'main_menu_2':  # Пункт "Найти пикчу по названию"
            picture_search_message(call.message.chat.id)  # Список названий пикч
            user_data[0] = "send_picture"  # Активируем режим выбора пикч
            user_data[2] = -1  # Блокируем все меню

    elif user_data[2] == 1:  # Меню выбора источника изображения для мема
        if call.data == 'picture_source_menu_1':  # Пункт "Предыдущее"
            # Проверка на то, существует ли предыдущее изображение
            if mmbfiles.check_previous_img(call.message.chat.id):
                user_data[0] = "get_source"  # Актив. режим получения исходников
                user_data[1] = 1  # Переходим к вводу текста пользователем
                user_data[2] = -1  # Блокируем все меню
                # Просьба отправить текст для мема
                bot.send_message(call.message.chat.id,
                                 phrases.send_mem_text_to_me)
            else:  # Предыдущего не существует - предупреждение
                bot.send_message(call.message.chat.id,
                                 phrases.previous_file_error)
                picture_source_menu(call.message.chat.id)
        elif call.data == 'picture_source_menu_2':  # Пункт "Выбрать шаблон"
            template_search_message(
                call.message.chat.id)  # Отправляем список названий шаблонов
            user_data[0] = "send_template"  # Активируем режим выбора шаблона
            user_data[2] = -1  # Блокируем все меню
        elif call.data == 'picture_source_menu_3':  # Пункт "Загрузить новое"
            mmbfiles.del_user_img(call.message.chat.id,
                                  "source")  # Удаляем старый исходник
            user_data[0] = "get_source"  # Актив. режим получения исходников
            user_data[1] = 2  # Ввод текста и картинки пользователем
            user_data[2] = -1  # Блокируем все меню
            # Просьба отправить текст и картинку для мема
            bot.send_message(call.message.chat.id, phrases.send_picture_to_me)

    elif user_data[2] == 2:  # Mеню после получения пикчи
        if call.data == 'send_picture_finish_menu_1':  # "Получить ещё пикчу"
            user_data[0] = "send_picture"
            user_data[2] = -1
            bot.send_message(
                call.message.chat.id,
                phrases.ask_picture_number(names.quantity_of_pictures))
        elif call.data == 'send_picture_finish_menu_2':  # Пункт "Главное меню"
            user_data[2] = 0
            user_data[0] = "None"
            main_menu(call.message.chat.id)

    elif user_data[2] == 4:  # Меню выбора источника изображения для мема
        if call.data == 'text_pos_menu_1':  # "Расположить текст по центру"
            user_data[4] = ['percent', 50, 50]
            user_data[0] = "None"
            user_data[1] = 0
            user_data[2] = 6
            bot.send_message(call.message.chat.id,
                             text=get_current_text_style(call.message))
            set_text_settings_menu(call.message.chat.id)
        elif call.data == 'text_pos_menu_2':  # "Расположение текста вручную"
            user_data[0] = "get_text_pos"
            user_data[1] = 1
            # Клавиатура в px / в %
            percent_px_keyboard = telebot.types.ReplyKeyboardMarkup(
                row_width=2,
                resize_keyboard=True)
            percent_px_keyboard.add(
                telebot.types.KeyboardButton(text=phrases.set_text_pos_in_px),
                telebot.types.KeyboardButton(
                    text=phrases.set_text_pos_in_percents))
            bot.send_message(call.message.chat.id,
                             text=phrases.set_text_pos_title,
                             reply_markup=percent_px_keyboard)
    elif user_data[2] == 6:  # Меню выбора способа настройки стиля текста
        if call.data == 'set_text_settings_menu_1':  # Пункт "Выбрать пакет"
            pack_choice_menu(call.message.chat.id)
            user_data[2] = 7
        elif call.data == 'set_text_settings_menu_2':  # Пункт "Задать вручную"
            change_text_settings_menu(call.message.chat.id)
            user_data[2] = 8
        elif call.data == 'set_text_settings_menu_3':  # "Использовать текущий"
            create_mem_with_user_settings(call.message)
            send_mem(call.message.chat.id)
            mmbfiles.del_user_img(call.message.chat.id, "answer")
            user_data[0] = "None"
            user_data[1] = 0
            user_data[2] = 0
            main_menu(call.message.chat.id)

    elif user_data[2] == 7:  # Меню выбора пакета настроек стиля текста
        if call.data.startswith('pack_choice_menu_'):
            if call.data[-1] != '6':
                pack_num = int(call.data[call.data.rfind('_') + 1:]) - 1
                user_data[3] = constants.text_setting_packs[pack_num]
                bot.send_message(call.message.chat.id,
                                 phrases.pack_choice_success)
            mmbfiles.rewrite_data(call.message, user_data, bot.send_message,
                                  start)
            bot.send_message(call.message.chat.id,
                             text=get_current_text_style(call.message))
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
            bot.send_message(call.message.chat.id, phrases.ask_font_bold,
                             reply_markup=yesno_keyboard)
            user_data[1] = 8
        elif call.data == 'change_text_settings_menu_5':
            bot.send_message(call.message.chat.id, phrases.ask_font_italic,
                             reply_markup=yesno_keyboard)
            user_data[1] = 9
        elif call.data == 'change_text_settings_menu_6':
            user_data[2] = 9
            user_data[1] = 10
            text_color_menu(call.message.chat.id)

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
            # Инструкция по вводу цвета в rgb
            with open(f"img/color_scheme.jpg", 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo,
                               caption=phrases.arbitrary_color_instruction)
        # Если выбран цвет из списка
        if call.data.startswith('text_color_menu_') and int(call.data[-1]) < 9:
            if user_data[0] == "font_settings":
                user_data[0] = "None"
                user_data[1] = 0
            user_data[2] = 6
            user_data[3][4] = text_color
            # bot.send_message(call.message.chat.id, phrases.font_setting_off)
            mmbfiles.rewrite_data(call.message, user_data, bot.send_message,
                                  start)
            bot.send_message(call.message.chat.id,
                             get_current_text_style(call.message))
            set_text_settings_menu(call.message.chat.id)

    elif user_data[2] == 11:  # Меню выбора шаблона
        if call.data == "send_template_finish_menu_1":
            user_data[0] = "get_source"
            user_data[1] = 1
            user_data[2] = -1
            bot.send_message(call.message.chat.id, phrases.send_mem_text_to_me)
        elif call.data == "send_template_finish_menu_2":
            user_data[2] = -1
            user_data[0] = "send_template"
            bot.send_message(
                call.message.chat.id,
                phrases.ask_template_number(names.quantity_of_templates))

    # Перезапись обновлённого списка с настройками пользователя
    mmbfiles.rewrite_data(call.message, user_data, bot.send_message, start)


# ======================ОБРАБОТКА КОМАНД========================
@bot.message_handler(commands=['menu'])
def menu(message):
    """Показываем главное меню"""
    user_data, reset = mmbfiles.read_data(message, bot.send_message, start)
    user_data[0] = "None"
    user_data[1] = 0
    user_data[2] = 0  # Активируем главное меню
    mmbfiles.rewrite_data(message, user_data, bot.send_message, start)
    main_menu(message.chat.id)  # Показываем главное меню


@bot.message_handler(commands=['start'])
def start(message):
    """
    1) Показываем главное меню
    2) Добавляем пользователя в базу данных
    3) Создаём папку пользователя
    4) Сохраняем туда стандартные настройки
    """
    global database
    user_id = message.chat.id  # id пользователя (чата)

    database.new_user(message)  # Обработка навого пользователя в базе данных

    mmbfiles.add_user_folder(user_id)  # Создание папки для данного пользователя

    # Инициализируем формат пользовательски настроек
    user_data = [0, 0, 0, 0, 0, 0]
    user_data[0] = "None"  # mode - режим работы бота
    user_data[1] = 0  # step - номер шага в данном режиме работы бота
    user_data[2] = 0  # active_menu - активное в данный момент меню
    user_data[3] = constants.standard_text_setting  # text_style - стиль текста
    user_data[4] = constants.standard_text_position  # text_position
    user_data[5] = ''  # source_text - текст, который ввел пользователь
    # Записываем в файл с пользовательскими настройками стандартные настройки
    mmbfiles.rewrite_data(message, user_data, bot.send_message, start)
    # Сообщение с приветствием
    bot.send_message(message.chat.id,
                     text=phrases.first_msg,
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    main_menu(message.chat.id)  # Показываем главное меню


# ======================ОБРАБОТКА ПОЛЬЗОВАТЕЛЬСКИХ СООБЩЕНИЙ====================
@bot.message_handler(content_types=['photo'])
def handle_start_help(message):
    """Обработка всех сообщений с картинкой"""
    user_data, reset = mmbfiles.read_data(message, bot.send_message, start)
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
            # Если её длина не больше макс. длины текста
            if 0 <= len(user_message) <= constants.max_mem_text_len:
                user_data[5] = user_message
                user_data[0] = "None"
                user_data[1] = 0
                user_data[2] = 4
                text_pos_menu(message.chat.id)
            else:
                user_data[1] = 1
                bot.send_message(
                    message.chat.id,
                    text=phrases.max_text_len_info(constants.max_mem_text_len))
                bot.send_message(message.chat.id, phrases.send_mem_text_to_me_2)
        else:
            user_data[1] = 1
            bot.send_message(message.chat.id, phrases.send_mem_text_to_me)
        # Перезапись обновлённого списка с настройками пользователя
        mmbfiles.rewrite_data(message, user_data, bot.send_message, start)


@bot.message_handler(content_types=["text"])
def processing_all_text_messages(message):
    """Обработка всех текстовых сообщений"""
    user_data, reset = mmbfiles.read_data(message, bot.send_message, start)
    if reset:  # Если настройки были сброшены, обнуляем нажатие на кнопку
        message = "reset"
    user_message = message.text  # Сообщение пользователя

    if user_data[0] == "font_settings":  # Режим ввода параметров шрифта
        user_message = user_message.lower()
        if user_data[1] == 1 or user_data[1] == 6:  # Ввод названия шрифта
            user_data[3][0], user_data[1] = get_font_name(message, user_message,
                                                          user_data[1])
        elif user_data[1] == 2 or user_data[1] == 7:  # Ввод размера шрифта
            user_data[3][1], user_data[1] = get_font_size(message, user_message,
                                                          user_data[1])
        elif user_data[1] == 3 or user_data[1] == 8:  # Ввод жирности шрифта
            user_data[3][2], user_data[1] = get_font_bold(message, user_message,
                                                          user_data[1])
        elif user_data[1] == 4 or user_data[1] == 9:  # Ввод курсивности шрифта
            user_data[3][3], user_data[1], user_data[2] = \
                get_font_italic(message, user_message, user_data[1])
        elif user_data[1] == 5 or user_data[1] == 10:  # Ввод цвета шрифта
            user_data[3][4], user_data[1] = \
                get_text_color(message, user_message, user_data[1])

        if user_data[1] == 0:  # Если настройка завершена
            user_data[0] = "None"
            user_data[2] = 6  # Активируем меню завершения настройки текста
            mmbfiles.rewrite_data(message, user_data, bot.send_message, start)
            bot.send_message(message.chat.id,
                             text=get_current_text_style(message))
            set_text_settings_menu(message.chat.id)

    elif user_data[0] == "get_source":  # Режим получения исходников для мема
        if user_data[1] == 1:
            if 0 <= len(user_message) <= constants.max_mem_text_len:
                user_data[0] = "None"
                user_data[1] = 0
                user_data[2] = 4
                user_data[5] = user_message
                text_pos_menu(message.chat.id)
            else:
                bot.send_message(message.chat.id,
                                 text=phrases.max_text_len_info)
                bot.send_message(message.chat.id, phrases.send_mem_text_to_me_2)

    elif user_data[0] == "get_text_pos":  # Режим получения позиции текста
        if user_data[1] == 1:
            if user_message == phrases.set_text_pos_in_px:
                bot.send_message(
                    message.chat.id,
                    phrases.user_pict_size(
                        mmbpicture.get_img_size(message.chat.id)))

                bot.send_message(
                    message.chat.id,
                    phrases.send_text_pos_in_px,
                    reply_markup=telebot.types.ReplyKeyboardRemove())
                user_data[1] = 2
            elif user_message == phrases.set_text_pos_in_percents:
                bot.send_message(
                    message.chat.id,
                    phrases.send_text_pos_in_per,
                    reply_markup=telebot.types.ReplyKeyboardRemove())
                user_data[1] = 3
            else:
                bot.send_message(message.chat.id, phrases.invalid_input)

        elif user_data[1] in (2, 3):
            x_max, y_max = mmbpicture.get_img_size(message.chat.id)
            correct, x, y = is_2_digit(user_message)
            if correct:
                in_px = user_data[1] == 2 and (0 < x < x_max and 0 < y < y_max)
                in_percent = user_data[1] == 3 and (0 < x < 100 and 0 < y < 100)
                if in_px or in_percent:
                    bot.send_message(
                        message.chat.id,
                        text=phrases.successful_input)
                    user_data[0] = "None"
                    user_data[1] = 0
                    user_data[2] = 6
                    user_data[4][1:] = x, y
                    if in_px:
                        user_data[4][0] = "px"
                    else:
                        user_data[4][0] = "percent"
                    bot.send_message(
                        message.chat.id,
                        text=get_current_text_style(message))
                    set_text_settings_menu(message.chat.id)
                else:
                    bot.send_message(
                        message.chat.id,
                        text=phrases.pos_out_of_range)
            else:
                bot.send_message(message.chat.id, text=phrases.invalid_input)

    elif user_data[0] == "send_picture":  # Если включён режим отправки пикчи
        correct = user_message.isdigit()
        picture_number = 1
        if correct:
            picture_number = int(user_message)
            correct = 0 < picture_number <= names.quantity_of_pictures

        if correct:
            picture = names.pictures[picture_number - 1]
            picture_name = picture[picture.find(' ') + 1:]
            bot.send_message(message.chat.id,
                             text=picture_name)  # Отправка названия
            send_picture(message.chat.id, "pictures", picture_name[:-1])
            user_data[2] = 2
            user_data[0] = "None"
            send_picture_finish_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, text=phrases.invalid_input)

    elif user_data[0] == "send_template":  # Если включён режим отправки шаблона
        correct = user_message.isdigit()
        template_number = 1
        if correct:
            template_number = int(user_message)
            correct = 0 < template_number <= names.quantity_of_templates

        if correct:
            template = names.templates[template_number - 1]
            template_name = template[template.find(' ') + 1:]
            bot.send_message(message.chat.id, text=template_name)
            send_picture(message.chat.id, "templates", template_name[:-1])
            # Копируем шаблон в папку пользователя
            mmbfiles.copy_to_user_folder(template_name[:-1], message.chat.id)

            user_data[2] = 11
            user_data[0] = "None"
            send_template_finish_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, text=phrases.invalid_input)

    else:  # Если введено непонятно что
        if message != "reset":  # Если данные не были сброшены
            bot.send_message(message.chat.id, phrases.not_understand)

    mmbfiles.rewrite_data(message, user_data, bot.send_message, start)


if __name__ == '__main__':  # Запуск
    bot.polling(none_stop=True)
