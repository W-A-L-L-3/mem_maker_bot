# Модуль для работы с файлами

import os  # Модуль для создания и удаления папок (в данном случае)
from shutil import copy, rmtree  # Ф-ция для копирования файлов и удаления папки
import pickle  # Модуль для работы с файлами

import phrases


def read_data(message, send_msg_func, start_func):
    """Открытие файла с пользовательскими данными и выгрузка их в user_data"""
    try:
        data_file = open(f"users/{message.chat.id}/data", "rb")
        reset = False
    except FileNotFoundError:  # Если файла data данного пользователя нет
        send_msg_func(message.chat.id, phrases.database_error)
        start_func(message)  # Инициализируем пользователя
        data_file = open(f"users/{message.chat.id}/data", "rb")
        reset = True
    user_data = pickle.load(data_file)
    data_file.close()
    # print('read', chat_id, user_data)  # Вывод для тестов
    return user_data, reset


def rewrite_data(message, user_data, send_msg_func, start_func):
    """Открытие файла с пользовательскими данными и загрузка в него user_data"""
    try:
        data_file = open(f"users/{message.chat.id}/data", "wb")
    except FileNotFoundError:  # Если файла data данного пользователя нет
        send_msg_func(message.chat.id, phrases.database_error)
        start_func(message)  # Инициализируем пользователя
        data_file = open(f"users/{message.chat.id}/data", "wb")
    pickle.dump(user_data, data_file)
    data_file.close()
    # print('rewrite', chat_id, user_data)  # Вывод для тестов


def del_user_img(chat_id, name):
    """
    Удаление картинки пользователя (answer или source, в зависимости от name)
    name - answer / source
    """
    os.remove(f"users/{chat_id}/img/{name}_picture.jpg")


def add_user_folder(user_id):
    """Создание папки для данного пользователя"""
    try:
        os.makedirs(f'users/{user_id}/img')
    except OSError:
        print("Папка этого пользователя уже создана, " +
              "либо произошла какая-то ошибка")
    else:
        print("Папка успешно создана")


def check_previous_img(user_id):
    """Существует ли предыдущее изображение"""
    prev_pict = f"users/{user_id}/img/source_picture.jpg"
    return os.path.exists(prev_pict)


def copy_to_user_folder(name, user_id):
    """Копирование шаблона с именем name в папку пользовател"""
    copy(f'img/templates/{name}.jpg', f'users/{user_id}/img/source_picture.jpg')


def clear_all_users_folders(del_data=False):
    """
    Удаление всех папок с файлами пользователя
    del_data - удалять ли файл data каждого пользователя (True/False)
    """

    def check(name):
        """Проеварка на то, является ли объект с данным путём папкой"""
        return os.path.isdir(f"./users/{name}")

    e = 0  # Счётчик ошибок
    # Обход всех папок в каталоге "users"
    for folder_name in filter(check, os.listdir(path="./users")):
        try:
            if del_data:  # Удаление папки целиком (вместе с "data")
                rmtree(f"./users/{folder_name}")
            else:  # Удаление только папки "img"
                rmtree(f"./users/{folder_name}/img")
        except OSError as e:  # Если возникла ошибка при поиске данного пути
            print(f"Error: {e.filename} - {e.strerror}.")
            e += 1
        else:
            print(f"Данные пользователя {folder_name} удалены")

    if e == 0:  # Если ошибок не было
        print()
        print("Все папки успешно удалены")
    else:
        print(f"Ошибки при удалении {e} папки(ок)")
