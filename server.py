import socket
import threading
import datetime
import os
import lobby_classes
import colorama
colorama.init()

coding = 'utf-8'
data_folder = "for users"
all_lobbys = {}
all_users = {}
all_users_ip = {}
trash_var = None


# TODO: /player info Brotfresser
#  профили(нужны только в игровых лобби) (ну, и сами игровые лобби, конечно)

class User:
    def __init__(self, user, name, ip_user):
        self.user = user
        self.name = name
        self.ip = ip_user
        self.lobby = None
        self.path = ""
        self.dir_pos = 0
        self.is_ban = False
        self.is_admin = False
        self.online = False
        self.join_commands = ""
        self.color_status = colorama.Fore.RESET

        all_users[name] = self
        all_users_ip[ip_user] = self

    def __str__(self):
        if isinstance(self.lobby, lobby_classes.Lobby):
            return f"Имя: {self.name}| Лобби: {self.lobby.name}| Забанен:{self.is_ban}| ip: {self.ip}| {type(self.user)}"
        else:
            return f"Имя: {self.name}| Лобби: выбирает| Забанен:{self.is_ban}| ip: {self.ip}| {type(self.user)}"

    def change_name(self):
        self.send(f"{colorama.Fore.GREEN}Введите новое имя")
        name = self.recv()
        del all_users[self.name]
        self.name = name
        all_users[name] = self
        self.lobby.user_join(self)

    def choose_lobby(self):
        try:
            self.keylogger_on()
            self.lobby = None
            while True:
                all_files = []
                if self.path != "":
                    all_files.append("...")
                # Смотрим все файлы и помечаем их
                for file_name in os.listdir(data_folder + self.path):
                    file_name = file_name.replace(".lnk", "")
                    if ("[" in file_name) and ("]" in file_name):  # Lobby
                        file_name = file_name + "|lobby"

                    elif file_name[-4:] == ".txt":
                        file_name = file_name + "|txt"

                    else:  # folder
                        file_name = file_name + "|folder"

                    all_files.append(file_name)

                # Обрисовываем
                for i in range(len(all_files)):
                    mess = ""
                    if i == self.dir_pos:
                        mess = colorama.Back.LIGHTBLACK_EX
                    line = all_files[i]

                    if line[-4:] == "|txt":
                        if i == self.dir_pos:
                            mess += colorama.Fore.BLACK
                        else:
                            mess += colorama.Fore.LIGHTBLACK_EX
                        mess += line[:-4]

                    elif line[-7:] == "|folder":
                        mess += colorama.Fore.YELLOW + line[:-7]

                    elif line[-6:] == "|lobby":
                        mess += colorama.Fore.LIGHTWHITE_EX + line[:-6]

                    else:
                        mess += line

                    self.send(mess + colorama.Style.RESET_ALL)

                command = self.recv()
                while command[-7:] != "release":
                    command = self.recv()

                if command[1] in "0123456789":
                    command = command[1:]
                    try:
                        command = command[:command.index("'")]
                        dir_pos = int(command)
                        if self.path == "":
                            self.dir_pos -= 1

                        if dir_pos in range(len(all_files)):
                            self.dir_pos = dir_pos
                    except ValueError:
                        pass

                elif command[:8] == "Key.down":
                    self.dir_pos += 1
                    if self.dir_pos >= len(all_files):
                        self.dir_pos = 0

                elif command[:6] == "Key.up":
                    self.dir_pos -= 1
                    if self.dir_pos < 0:
                        self.dir_pos = len(all_files) - 1

                elif command[:9] == "Key.enter":
                    try:
                        line = all_files[self.dir_pos]

                        if line == "...":
                            path = self.path.split("/")
                            self.path = "/".join(path[:-1])
                            self.dir_pos = 0

                        elif line[-6:] == "|lobby":
                            print(self.name, "зашёл в лобби!")
                            lobby = all_lobbys[line[:line.index(" [")]]
                            self.lobby = lobby
                            self.keylogger_off()
                            self.lobby.user_join(self)

                        elif line[-7:] == "|folder":
                            self.path += "/" + line[:-7]
                            if len(os.listdir(data_folder + self.path)) == 0:
                                self.dir_pos = 0
                            else:
                                self.dir_pos = 1

                        elif line[-4:] == "|txt":
                            line = all_files[self.dir_pos][:-4]
                            with open(data_folder + self.path + "/" + line) as file:
                                text = ""
                                for s_line in file:
                                    while "|" in s_line:
                                        global trash_var
                                        trash_var = ""
                                        line = s_line[:s_line.index("|")]
                                        s_line = s_line[s_line.index("|") + 1:]
                                        com = s_line[:s_line.index("|")]

                                        if com[0] == "@":
                                            com = "global trash_var; trash_var = " + com[1:]
                                        exec(com)
                                        s_line = line + trash_var + s_line[s_line.index("|") + 1:]

                                    text += s_line

                                self.send(text)
                                self.send(" ...")
                                command = self.recv()
                                while (command != "Key.enter_release") and (command is not None):
                                    command = self.recv()

                    except IndexError:
                        print(f"{colorama.Fore.RED}///{self.name} во время выбора лобби как-то выбрал не ту позицию, {self.dir_pos}| {self.path}")
                        self.dir_pos = 0

                self.clear_console()
        except (ConnectionResetError, TypeError, AttributeError):
            return

    def send(self, message, color=colorama.Style.RESET_ALL):
        """
        Отправляет игроку сообщение.
        :param message: Сообщение игроку.
        :param color: Добавляется в начале сообщения + '\n'. Если color is None -> ничего не добавляет
        :return:
        """
        try:
            if color is None:
                self.user.send(message.encode(coding))
            else:
                self.user.send(f"{color}{message}\n".encode(coding))
        except ConnectionResetError:
            if self.online:
                self.exit()

    def clear_console(self):
        self.send(chr(258))

    def keylogger_on(self):
        self.send(chr(257))

    def keylogger_off(self):
        self.send(chr(256))

    def recv(self, size=1024, color=None):
        """

        :param color: Если is not None -> добавляется в начале return.  Если игрок вышел -> return is None
        """
        try:
            if color is None:
                message = f"{self.user.recv(size).decode(coding)}"
            else:
                message = f"{color}{self.user.recv(size).decode(coding)}"

            return message
        except (ConnectionResetError, AttributeError):
            print(f"{self.name} | ошибка: вышел | ")
            self.exit()
            return None

    def ban(self):
        self.is_ban = True
        print(f"{self.name} забанен")

    def unban(self):
        if self.is_ban:
            self.is_ban = False
        else:
            print("////дибил, он не в бане")

    def exit(self):
        self.online = False
        self.send("И больше не возвращайся")
        self.user = None
        if self.lobby is not None:
            self.lobby.exit_user(self)


def registration_user(user, ip_user):
    user.send(f"{colorama.Fore.BLUE}Новый пользователь: начинается регистрация\n\n".encode(coding))
    while True:
        user.send(f"{colorama.Fore.BLUE}Введите ваш логин\n".encode(coding))
        user_name = user.recv(1024).decode(coding)
        if user_name in all_users:
            user.send(f"{colorama.Fore.RED}'{user_name}' занято, введите другое имя\n".encode(coding))
        else:
            break

    return User(user, user_name, ip_user)


def user_join_server():
    while True:
        try:
            user_data = server.accept()
            user = user_data[0]
            ip_user = user_data[1][0]

            user.send(coding.encode("utf-8"))

            if ip_user in all_users_ip:
                if all_users_ip[ip_user].user is None:
                    all_users_ip[ip_user].user = user
                    user = all_users_ip[ip_user]

                    user.send(f"С возвращением, {user.name}!", colorama.Fore.GREEN)
                    exec(user.join_commands)

                else:
                    user.send("Ты уже подключён к серверу, но можно создать временный аккаунт\n".encode(coding))
                    user.send("Введи 458993725821242222".encode(coding))
                    while user.recv(1024).decode(coding) != "458993725821242222":
                        pass

                    for cnt in range(10):
                        num = lobby_classes.random.randint(0, 10)
                        if num not in all_users_ip:
                            break
                    else:
                        user.send("все места для временных аков заняты, пошёл нахуй")
                        continue
                    user = registration_user(user, f"f{num}")

            else:
                user = registration_user(user, ip_user)

            global_message = f"{user.name} присоединился к нам в {datetime.datetime.now()}"
            print(global_message)
            user.send(f"{colorama.Fore.GREEN}авторизация закончилась, добро пожаловать!")
            user.online = True
            threading.Thread(target=user.choose_lobby).start()
        except ConnectionResetError:
            print("ошибка: чел вышел, пока регался")


def update_all_lobby(path=""):
    # Загружаем все лобби Lobby
    for file in os.listdir(data_folder + path):

        if "[" in file and file[-1] == "]":  # Lobby

            if file[-6:] == "[text]":
                lobby_name = file[:-7]
                lobby = lobby_classes.TextLobby(lobby_name, data_folder + path + "/" + file)
            elif file[-10:] == "[monopoly]":
                lobby_name = file[:-11]
                lobby = lobby_classes.Monopoly(lobby_name, data_folder + path + "/" + file)
            else:
                continue

            if lobby_name not in all_lobbys:
                all_lobbys[lobby_name] = lobby
                lobby.load_files()
            else:
                del lobby

        else:
            try:
                os.listdir()
                update_all_lobby(path + "/" + file)

            except NotADirectoryError:
                continue


def update_all_users_data():
    with open("all users data.txt") as file:
        for line in file:
            if line != "\n":  # если не пустая строка
                line = line.split()
                ip_user = line[0]
                if ip_user not in all_users_ip:
                    user_name = line[1]
                    user = User(None, user_name, ip_user)

                    if len(line) > 3:
                        command = " ".join(line[3:])
                        user.join_commands = command


def write_to_lobby(lobby_name: str, message: str, file=None):
    all_lobbys[lobby_name].send_message(f"{colorama.Fore.RED}{message}{colorama.Fore.RESET}", file)


def write_to_all_players(message: str):
    for name in all_users:
        user = all_users[name]
        if user.user is not None:
            user.send(f"{colorama.Fore.RED}{message}{colorama.Fore.RESET}")


def write_to_all_lobby(message: str):
    for lobby_name in all_lobbys:
        all_lobbys[lobby_name].send_message(f"{colorama.Fore.RED}{message}{colorama.Fore.RESET}", None)


server = socket.socket()
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
ip = input("введите ip сервера (пример: 29.179.133.187) [")
server.bind((ip, 2000))
server.listen()  # было 5

message = f"{colorama.Fore.BLUE}////Сервер создался " + str(datetime.datetime.now())
update_all_lobby()  # сначала лобби, потом игроки
update_all_users_data()
print(message)
threading.Thread(target=user_join_server).start()


def exec_command():
    while True:
        command = input()

        try:
            if command[0] == "/":
                if command[:5] == "/read":
                    command = command[6:].split()
                    lobby = command[0]
                    file = command[1]
                    lines = int(command[2]) * 2
                    path = all_lobbys[lobby].files_dict[file + ".txt"]["path"]
                    with open(path, "r") as file:
                        for line in file.readlines()[-lines:]:
                            if line != "\n":
                                print(line[:-1])

                elif command == "/users":
                    cnt = 0
                    for user in all_users:
                        if all_users[user].user is not None:
                            print(user)
                            cnt += 1
                    print(cnt, "Пользователей онлайн")
                elif command == "/lobbys":
                    for lobby in all_lobbys:
                        print(lobby)
                    print(len(all_lobbys), "Лобби")

                elif command[:4] == "/all":
                    command = command[5:]
                    if command[0] == "l":
                        write_to_all_lobby(command[2:])
                    elif command[0] == "p":
                        write_to_all_players("Внимание! " + command[2:])

                elif command[:2] == "/l":
                    command = command[3:].split()
                    message = " ".join(command[1:-1])
                    if "-no" not in command:
                        message = "Админ: " + message
                    else:
                        message = message.replace("-no", "")

                    if message == "":
                        message = command[1]
                    if ".txt" in command[-1]:
                        write_to_lobby(command[0], message, command[-1])
                        print(message, "написано в", command[0], command[-1])
                    else:
                        write_to_lobby(command[0], message + command[-1])
                        print(message + command[-1], "написано в", command[0])

                elif command[:2] == "/p":
                    command = command[3:].split()
                    message = f"{colorama.Fore.RED}Админ: " + " ".join(command[1:])
                    all_users[command[0]].send(message)

            else:
                try:
                    exec(command)
                except Exception as error:
                    print("command error")
                    print(error)

        except Exception as error:
            print("///WARNING")
            print("global error")
            print(error)


while True:
    try:
        exec_command()

    finally:
        print("server is over")
        with open("all users data.txt", "w+") as file:
            for user_ip in all_users_ip:
                if user_ip[0] != "f":
                    user_name = all_users_ip[user_ip].name
                    user_lobby = all_users_ip[user_ip].lobby
                    if user_lobby is not None:
                        user_lobby = user_lobby.name
                    else:
                        user_lobby = "Nonee"

                    user_com = all_users_ip[user_ip].join_commands

                    line = " ".join([user_ip, user_name, user_lobby, user_com])
                    file.write(line + "\n\n")
        input()
        exec_command()
