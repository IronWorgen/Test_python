import sys
import json
import os
from datetime import datetime


# wiew
def run():
    flag = True
    while flag:
        print("Введите команду (add, list, open 'название заметки', dell 'название заметки', help, exit)")
        command = input(":").strip().lower()
        if command == "exit":
            return

        command_controller(command.split())


# контроллер команд
def command_controller(command):
    if command[0] == "add":
        add()
    elif command[0] == "list":
        show_notes_list(command)
    elif command[0] == "open":
        open_note(command)
    else:
        show_error_message("Неверная команда '" +
                           command[0]+"'. Чтобы открыть справку введите 'help'")


# создание новой заметки
def add():
    print("\nСоздание заметки(введите 'q' чтобы отменить создание): ")
    print("----------------------------------------")

    title_note = input("Введите заголовок:   ").strip()
    if title_note == "q":
        return

    print("\nВведите текст заметки (чтобы завешить редактирование введите на новой строке 'Ctrl+z' для Windows или 'Ctrl+d' для Linux/Mac):")
    text_note = sys.stdin.readlines()

    input_is_ok = True
    while (input_is_ok):
        input_is_ok = False
        save = input("\nСохранить заметку?(yes/no): ").strip().lower()

        if save == "yes":

            date_created = datetime.now()
            date_created = date_created.strftime("%d.%m.%Y %H:%M:%S")
            date_edited = date_created

            save_note(title_note, text_note, date_created, date_edited)

        elif save != "no":
            show_error_message(
                "ОШИБКА!\nВведите 'yes' - чтобы сохранить заметку.\nВведите 'no' - чтобы отменить сохранение.")
            input_is_ok = True
    print("----------------------------------------\n")


# вывести список заметок
def show_notes_list(command):
    notes = get_note_list()

    if len(command) == 1:
        print("Список заметок:")
        print("----------------------------------------")

        counter = 1
        for i in range(len(notes)-1, -1, -1):
            current_note = notes[i]
            print(f"{counter}.  {current_note.get('title')}")
            print(f"Дата создания:  {current_note.get('create_date')}\n")
            counter += 1
    elif command[1] in ["-du", "-dua", "-dd", "-dda", "-dr", ]:
        notes_list_filter(notes, command[1])

    return


# фильтр по дате
def notes_list_filter(notes, key):

    if key == "-dua":
        message_to_user = "\nСписок заметок:\t\tСортировака по возрастанию даты."
        show_filtred_notes(notes, message_to_user)

    elif key == "-du":
        flag = True
        while flag:
            max_date = input(
                "Введите дату(дд.мм.гггг), начиная с которой нужно отобразить заметки('q'- отмена):  ")
            if max_date == "q":
                return

            if date_is_ok(max_date):
                filtred_notes_list = get_filtred_list(notes, "u", max_date)
                message_to_user = "\nСписок заметок:\t\tСортировака по возрастанию даты(начиная с "+str(
                    max_date)+")."
                show_filtred_notes(filtred_notes_list, message_to_user)
                flag = False

    elif key == "-dda":
        message_to_user = "\nСписок заметок:\t\tСортировака по убыванию даты."
        # разворот масиива 
        for i in range(len(notes)//2):
            notes[i], notes[-i-1]=notes[-i-1], notes[i]        
        
        show_filtred_notes(notes, message_to_user)

    elif key == '-dd':
        flag = True
        while flag:
            max_date = input(
                "Введите дату(дд.мм.гггг), начиная с которой нужно отобразить заметки('q'- отмена):  ")
            if max_date == "q":
                return

            if date_is_ok(max_date):
                filtred_notes_list = get_filtred_list(notes, "d", max_date)
                message_to_user = "\nСписок заметок:\t\tСортировака по убыванию даты(начиная с "+str(
                    max_date)+")."
                show_filtred_notes(filtred_notes_list, message_to_user)
                flag = False



# Отобразить список заметок пользователю
def show_filtred_notes(notes, message):
    if (notes == None):
        return
    print(message)
    print("----------------------------------------------------------------------------")
    counter = 1
    for i in notes:
        print(f"{counter}.  {i.get('title')}")
        print(f"Дата создания:  {i.get('create_date')}\n")
        counter += 1
    print("----------------------------------------------------------------------------\n")


# проверка формата даты
def date_is_ok(date):    
    date = date.split(".")
    if (len(date) != 3):
        show_error_message("Ошибка!!! Неверный формат даты.")
        return False

    for i in range(len(date)):
        try:
            date[i] = int(date[i])
        except Exception:
            show_error_message(
                "Ошибка!!! Неверный формат даты. '"+i+"' - это не число")
            return False

    if date[0] <= 0 or date[0] > 31:
        show_error_message("Ошибка!!! Невозможное число дней в месяце!")
        return False

    if date[1] <= 0 or date[1] > 12:
        show_error_message("Ошибка!!! В году 12 месяцев!")
        return False

    if date[2] <= 0:
        show_error_message("Ошибка!!! Год не может быть отрицательным!")
        return False

    return True

# вернуть отфильтрованный список


def get_filtred_list(notes, filtration_type, first_date, second_date=0):
    if filtration_type == "u":
        min_date = first_date
        # проверка краевых условий
        last_note_create_date=notes[len(notes)-1].get("create_date").split(" ")[0]
        first_note_create_date=notes[0].get("create_date").split(" ")[0]
        if not first_date_more(last_note_create_date, min_date):
            show_error_message("Нет записок подходящих под условие")
            return None
        if first_date_more(first_note_create_date, min_date):
            return notes

        min_date_index = binary_search_min(notes, first_date)
        result_notes_list = notes[min_date_index:]
        return result_notes_list
    
    elif filtration_type == "d":
        max_date = first_date
        # проверка краевых условий
        last_note_create_date=notes[len(notes)-1].get("create_date").split(" ")[0]
        first_note_create_date=notes[0].get("create_date").split(" ")[0]
        if first_date_more(first_note_create_date, max_date):
            show_error_message("Нет записок подходящих под условие")
            return None
        if not first_date_more(last_note_create_date, max_date):

            result_notes_list=notes
            for i in range(len(result_notes_list)//2):
                result_notes_list[i], result_notes_list[-i-1] =result_notes_list[-i-1], result_notes_list[i]
            return notes    
        
        max_date_index = binary_search_max(notes, first_date)
        
        result_notes_list=notes[:max_date_index+1]
        for i in range(len(result_notes_list)//2):
            result_notes_list[i], result_notes_list[-i-1] =result_notes_list[-i-1], result_notes_list[i] 
        return result_notes_list

# Сравнение дат. если first_date>second_date --> true, иначе --> false. если даты равны --> 0
def first_date_more(first_date, second_date):
    
    first_date = first_date.split('.')
    second_date = second_date.split('.')

    first_date_years = int(first_date[2])
    second_date_years = int(second_date[2])
    if (first_date_years > second_date_years):
        return True
    elif (first_date_years < second_date_years):
        return False

    first_date_month = int(first_date[1])
    second_date_month = int(second_date[1])
    if (first_date_month > second_date_month):
        return True
    elif (first_date_month < second_date_month):
        return False

    first_date_day = int(first_date[0])
    second_date_day = int(second_date[0])
    if (first_date_day > second_date_day):
        return True
    elif (first_date_day < second_date_day):
        return False

    return 0


# бинарный поиск минимальной даты
def binary_search_min(notes, required_date):
    low = 0

    hight = len(notes)-1

    while low <= hight:
        mid = (low + hight)//2
        if first_date_more(notes[mid].get("create_date").split(" ")[0], required_date):
            if not first_date_more(notes[mid-1].get("create_date").split(" ")[0], required_date):
                return mid
            else:
                hight = mid-1
        elif not first_date_more(notes[mid].get("create_date").split(" ")[0],required_date):
            if not first_date_more(notes[mid+1].get("create_date").split(" ")[0], required_date):
                return mid+1
            else:
                low = mid+1
        elif first_date_more(notes[mid].get("create_date").split(" ")[0], required_date) == 0:
            return mid
        
# бинарный поиск максимальной даты
def binary_search_max(notes, required_date):
    low = 0

    hight = len(notes)-1

    while low <= hight:
        mid = (low + hight)//2
        if not first_date_more(notes[mid].get("create_date").split(" ")[0], required_date):
            if  first_date_more(notes[mid+1].get("create_date").split(" ")[0], required_date):
                return mid
            else:
                low = mid+1
        elif first_date_more(notes[mid].get("create_date").split(" ")[0], required_date):
            if not first_date_more(notes[mid-1].get("create_date").split(" ")[0], required_date):
                return mid-1
            else:
                hight = mid+1
        elif first_date_more(notes[mid].get("create_date").split(" ")[0], required_date) == 0:
            return mid


# --------------------------модуль работы с заметками --------------------
# открыть заметку
def open_note(command):
    
    if len(command)>2:
        command[1]=" ".join(command[1:])
    if len(command)!=2:
        show_error_message("Неверный формат команды. для стравки введите help")
    
    notes = get_note_list()
    result_search=list()
    print (command[1][1:-1].strip())
    for i in notes:
        if i.get("title").strip()==command[1][1:-1].strip():
            result_search.append(i)

    if len(result_search)==0:
        show_error_message("Ошибка!!! записка "+command[1]+" ненайдена. чтобы посмотреть все записки введите 'list'")
    elif    len(result_search)>1:
        print (f"\nНайдено {len(result_search)} {'записки' if len(result_search)<=4 else 'записок'}.\n--------------------------------------")
        counter = 1
        for i in result_search:
            print(f"Записка №{counter}")
            print_note(i)
            counter+=1
    else: 
        print_note(result_search[0])
        flag = True
        while flag:
            print("Введите 'edit'- чтобы редактровать записку.'dell' - чтобы удалить записку. 'q'-вернуться в меню")
            user_input = input(":").strip().lower()
            if user_input == "q":
                return

        
    

def print_note(note):
    print(f"Заголовок:  {note.get('title')}")        
    print(f"Дата создания:  {note.get('create_date')}")
    print(f"Дата последнего изменения:  {note.get('edit_date')}")
    text_note = note.get("text")
    text_str = ""
    for i in text_note:
        text_str+="\t"+i
    print ("Текст заметки:\n"+text_str)


# сохранить заметку в формате JSON
def save_note(title_note, text_note, create_date, edit_date):
    data = get_note_list()

    new_title_json = {"title": title_note, "text": text_note,
                      "edit_date": edit_date, "create_date": create_date}
    data.append(new_title_json)

    with (open("test.json", mode="w")) as f:
        json.dump(data, f, indent=2)




# получить список всех заметок
def get_note_list():
    data = list()
    if os.path.getsize("test.json") > 0:

        with open("test.json", mode="r") as f:
            data = json.load(f)
            f.close
    else:
        show_error_message("Список заметок пуст")
    return data


# Вывести сообщение об ошибке
def show_error_message(message):
    print("====================================================")
    print(message)
    print("====================================================\n")


run()
