from collections import UserDict
from datetime import datetime, timedelta


# Класи для роботи з контактами
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, number):
        self.value = self.validate_number(number)

    def validate_number(self, number):
        if len(number) == 10 and number.isdigit():
            return number
        raise ValueError("Phone number must contain exactly 10 digits")


class Birthday(Field):
    def __init__(self, value):
        self.value = self.validate_birthday(value)

    def validate_birthday(self, value):
        try:
            # Перевіряємо формат і коректність дати
            datetime.strptime(value, "%d.%m.%Y")
            return value  # Зберігаємо рядок, якщо дата валідна
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return
        raise ValueError("Phone number not found")

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = Phone(new_number).value
                return
        raise ValueError("Old phone number not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday.value if self.birthday else "No birthday set"

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = f", birthday: {self.show_birthday()}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        results = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value
                next_birthday = birthday_date.replace(year=today.year)

                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                if today <= next_birthday <= next_week:
                    if next_birthday.weekday() >= 5:  # 5 = субота, 6 = неділя
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))

                    results.append({
                        "name": record.name.value,
                        "birthday": next_birthday.strftime("%d.%m.%Y")
                    })

        return results

    def __str__(self):
        contacts = "\n".join(str(record) for record in self.data.values())
        return f"AddressBook:\n{contacts}"


# Обробники помилок
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This user does not exist. Enter a valid user name."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough information provided. Try again."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return wrapper


# Команди для взаємодії
@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return f"Contact {name} added or updated."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone for {name} changed."
    return "Contact not found."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    return "Contact not found."


def show_all(book):
    return str(book) if book.data else "No contacts found."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    return "Contact not found."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s birthday is {record.show_birthday()}."
    return "Contact not found."


def upcoming_birthdays(book):
    birthdays = book.get_upcoming_birthdays()
    if not birthdays:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{b['name']} - {b['birthday']}" for b in birthdays)


# Парсер вводу
def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


# Головна функція
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(upcoming_birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
