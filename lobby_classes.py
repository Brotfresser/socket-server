import datetime
import os
import time

import colorama
import random


class Lobby:
    """
    Каждому нужна личная папка, обозначающая его имя и [тип]
    heck [text]
    """
    def __init__(self, name, path, type):
        self.name = name
        self.path = path
        self.players_dict = {}
        self.files_dict = {}
        self.type = type

        self.default_commands = ["/admin", "/lobby", "/exit", "/new_lobby", "/new_name", "/help"]
        self.comand_desription = ["отправить сообщение админу (/admin ...)", "вывести текущее лобби", "перезайти", "выбрать другое лобби", "сменить имя", "стать админом"]
        self.new_commands = []

    def load_files(self):
        pass
    
    def exit_user(self, user):
        """user_file = self.players_dict[user.name]["info"]["file"]
        del self.players_dict[user.name]
        self.files_dict[user_file]["users"].remove(user)"""
    
    def user_join(self, user):
        pass
    
    def send_message(self, message, file_name: str):
        pass
        
    def user_update(self, user):
        pass

    def new_user_exec(self, message, user):
        pass

    def default_user_exec(self, command, user):
        if command == "/help":
            if self.players_dict[user.name]["info"]["last command"] == command:
                if user.is_admin is True:
                    user.send("вы уже админ, неужели не пон... а, понял, ок")
                    for _ in range(10):
                        user.send("0%")
                    user.send("100%")

                    user.send("Всё, готово")
                    user.is_admin = None
                elif user.is_admin is False:
                    user.send("поздравляю, теперь вы админ")
                    user.is_admin = True
                else:
                    user.send("Хех, бысто ты. Ну, сделанного не воротишь...")
            else:
                msg = ""
                for i in range(len(self.default_commands)):
                    msg += self.default_commands[i] + " - " + self.comand_desription[i] + "\n"

                for i in range(len(self.new_commands)):
                    msg += self.new_commands[i] + " - " + self.comand_desription[i] + "\n"

                user.send(f"{colorama.Fore.YELLOW}{msg}")

        elif command == "/lobby":
            user.send(self.name)

        elif command == "/new_lobby":
            user.choose_lobby()
            self.exit_user(user)

        elif command == "/new_name":
            self.exit_user(user)
            user.change_name()

        elif command == "/exit":
            self.exit_user(user)
            self.user_join(user)

        elif "/admin" in command:
            print(f"{colorama.Fore.YELLOW}////К вам, админу, из {self.name} обратился {user.name}:", command[command.index("/admin") + 6:])
            self.players_dict[user.name]["info"]["last command"] = command
            return "continue"

        self.players_dict[user.name]["info"]["last command"] = command


class TextLobby(Lobby):
    def __init__(self, name, path):
        super().__init__(name, path, "text lobby")
        self.new_commands = ["/file"]
        self.comand_desription += ["выводит текущий файл/подлобби"]

    def load_files(self):
        for file_name in os.listdir(self.path):
            if file_name[-4:] == ".txt":
                self.files_dict[file_name] = {}
                self.files_dict[file_name]["path"] = self.path + "/" + file_name
                self.files_dict[file_name]["users"] = []

    def user_update(self, user):
        try:
            while True:
                try:
                    message = user.recv()
                    if message is None:
                        exit()
                    else:
                        if message.split()[0] in self.default_commands:
                            if self.default_user_exec(message, user) != "continue":
                                continue
                        elif message.split()[0] in self.new_commands:
                            if self.new_user_exec(message, user) != "continue":
                                continue

                        elif (user.is_admin is True) and (message[0] == "/"):
                            exec(message[1:])
                            continue

                        if user.is_ban:
                            if "/admin" in message:
                                message = f"{colorama.Fore.RED}Ждите рассмотрения заявки"
                            else:
                                message = f"{colorama.Fore.RED}Вы, {user.name}, забаненны, вам никто не слышит. Пишите /admin, чтобы админ вас услышал"

                            user.send(message)
                        else:
                            if len(message) < 1024:
                                self.send_message(f"{user.color_status}{user.name}: {message}", self.players_dict[user.name]["info"]["file"])
                            else:
                                user.ban()

                except ConnectionResetError:
                    user.exit("принудительно")
                    return

                except ValueError as error:
                    if error.args[0] == "ValueError: list.remove(x): x not in list":
                        return
        except KeyError:
            return

    def exit_user(self, user):
        try:
            user_file = self.players_dict[user.name]["info"]["file"]
            del self.players_dict[user.name]
            self.files_dict[user_file]["users"].remove(user)
        except KeyError:
            pass

    def user_join(self, user):
        self.players_dict[user.name] = {"user": user, "info": {"last command": None}}

        while True:
            all_files = ""
            for file_name in self.files_dict:
                all_files += f"{file_name[:-4]}, "
            user.send(f"\n{colorama.Fore.BLUE}выберите лобби для текущего лобби:")
            user.send(f"{colorama.Fore.YELLOW}{all_files[:-2]}")

            try:
                user_file = user.recv()
                while user_file in self.default_commands:
                    self.default_user_exec(user_file, user)
                    user_file = user.recv()

                user_file += ".txt"

            except TypeError:
                del self.players_dict[user.name]
                return

            if user_file in self.files_dict:
                break
            else:
                user.send("таково файла не существует")

        self.players_dict[user.name]["info"]["file"] = user_file
        self.files_dict[user_file]["users"].append(user)
        with open(self.files_dict[user_file]["path"], "r") as file:
            message = "".join(file.readlines())
            user.send(message)
        self.user_update(user)

    def send_message(self, message: str, file_name: str):
        if file_name is None:
            for file in self.files_dict:
                self.send_message(message, file)
        else:
            try:
                with open(self.files_dict[file_name]["path"], "a+") as file:
                    file.write("\n" + message + "\n")

                for user in self.files_dict[file_name]["users"]:
                    user.send(message)
            except KeyError as error:
                print(error)

    def new_user_exec(self, command, user):
        if command == "/file":
            user.send(self.players_dict[user.name]["info"]["file"])


class Monopoly(Lobby):
    def __init__(self, name, path):
        super().__init__(name, path, "Monopoly")
        self.global_chat = ''
        self.players_list = []
        self.players_count = None

    def user_join(self, user):
        print("это монополия!")
        user.send(self.global_chat)
        self.send_message(f"{user.name} присоединился к нам!")

        self.players_dict[user.name] = {"user": user}
        self.players_list.append(user.name)

        self.send_message(f"Ждём игроков, сейчас ({len(self.players_list)}/{self.players_count})")

        if len(self.players_dict) == 1:
            self.players_count = int(user.recv("Сколько игроков будет?"))

        elif len(self.players_dict) == self.players_count:
            self.send_message("Все игроки в сборе, начинаем...")
            for name in self.players_list:
                self.user_update(self.players_dict[name])

    def send_message(self, message, file_name=None):
        self.global_chat += message
        for name in self.players_list:
            self.players_dict[name].send(message)

    def user_update(self, user):
        user.send(f"hi there! this players are here {self.players_list}")


if __name__ == "__main__":
    print("вы попали в lobby_classes")
    import server