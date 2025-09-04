import socket, threading, colorama
import os
from pynput.keyboard import Listener
import time
colorama.init()
ver = 0.85


is_first_key = False
keylog_on = False
f10_pressed = False
errors_cnt = 0
TIME_WAIT = 1


def receive_message():
    global close_program
    while True:
        try:
            global keylog_on, is_first_key
            server_message = server.recv(1024).decode(coding)

            if chr(256) in server_message:
                keylog_on = False
                print(colorama.Fore.GREEN, "кейлогер", keylog_on)
                time.sleep(TIME_WAIT)
            elif chr(257) in server_message:
                keylog_on = True
                print(colorama.Fore.GREEN, "кейлогер", keylog_on)
                is_first_key = True
                time.sleep(TIME_WAIT)
            elif chr(258) in server_message:
                os.system("cls")
            elif chr(259) in server_message:
                server_message = server_message.replace(chr(259), "")
                print(server_message, end="")
            else:
                print(server_message)

                if server_message == "":
                    global errors_cnt
                    print(colorama.Fore.RED, "сервер отправил пустую строку уже", errors_cnt, "раз подряд")
                    errors_cnt += 1
                    if errors_cnt >= 30:
                        print(f"\n\n\n{colorama.Fore.RED}Похоже, вы словили баг, или сервер крашнулся. Попробуйте перезайти, я хз")
                        time.sleep(10)
                else:
                    errors_cnt = 0

        except UnicodeDecodeError:
            print(colorama.Fore.RED, "ошибка: видимо, в этом лобби повреждённый файл, хз")
        except ConnectionResetError as error:
            print(colorama.Fore.RED, error)
            print(f"\n\n\nСервер закрылся, тебе придётся перезапустить свою прогу")
            time.sleep(10)


def send_keyboard_key():
    def key_hold(key):
        global f10_pressed
        key = str(key) + "_hold"
        if keylog_on and is_first_key is False:
            if f10_pressed is False:
                server.send(key.encode(coding))

    def key_release(key):
        global f10_pressed, is_first_key
        key = str(key) + "_release"
        if keylog_on:
            if is_first_key is False:
                if key == "Key.f10_release":
                    if f10_pressed is True:
                        f10_pressed = False
                        print(colorama.Fore.GREEN, "кейлогер включён")
                        time.sleep(TIME_WAIT)
                    else:
                        f10_pressed = True
                        print(colorama.Fore.GREEN, "кейлогер отключён")
                        time.sleep(TIME_WAIT)

                elif f10_pressed is False:
                    server.send(key.encode(coding))

            else:
                is_first_key = False

    with Listener(on_press=key_hold, on_release=key_release) as listener:
        listener.join()



ip = input("введите ip сервера (пример: 29.179.133.187) [")
print("ver", ver)
print(colorama.Fore.YELLOW, "пробуем подключиться")
server = socket.socket()
try:
    server.connect((ip, 2000))
except ConnectionRefusedError as error:
    print(colorama.Fore.RED, "    Cервер пока не запущен, наверное")
    print(colorama.Fore.RED, error)
    time.sleep(10)

coding = server.recv(1024).decode("utf-8")

print(colorama.Fore.GREEN,"подключение успешно")
print(colorama.Fore.YELLOW, "игровым серверам нужно быстро отправлять ваши клавиши, для этого здесь установлен кейлоггер")
print(colorama.Fore.YELLOW, "вы будете уведомлены о состоянии кейлоггера зелёным текстом, можете ввести /keylogger, если не уверены")
print(colorama.Fore.YELLOW, "вы в любой момент можете выключить кейлоггер на 'f10', сейчас он выключен")

threading.Thread(target=receive_message).start()
threading.Thread(target=send_keyboard_key).start()


while True:
    message = input()
    if message == "/keylogger":
        print(f"{colorama.Fore.GREEN}кейлоггер: {keylog_on}, F10 блокирует кейлоггер: {f10_pressed}")

    elif (keylog_on is True) and (f10_pressed is False):
        pass
    else:
        server.send(message.encode(coding))
