# Файл для очистки различных разделов базы данных

import mmbdatabase  # Модуль для работы с базой данных
import mmbfiles

database = mmbdatabase.Database("database.xlsx")  # Объект базы данных

database.clear_main_sheet()  # Очистка основной таблицы базы данных
mmbfiles.clear_all_users_folders(del_data=True)  # Удаление всех папок с файлами пользователя
