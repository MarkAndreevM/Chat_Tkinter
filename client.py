import socket
import threading
# tkinter - интерфейсная библиотека
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog


# наш клиент будет не просто скриптом, как модуль server, а будет отдельным классом, фактически объектом Python
class Client:

    # определяем метод инициализации и передаем всю поддержку (HOST & PORT)
    def __init__(self, host, port):

        # определяем клиентский сокет(сервер) и подключаемся к порту сервера
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.tk_chat_window = None

        # Создаём окно от для ввода никнэйма (имени) пользователя
        msg = tkinter.Tk()
        msg.withdraw()

        # Спрашиваем что-нибудь в диалоговом окне и результатом будет псевдоним, т.е. никнэйм
        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg).encode('utf-8')

        self.running = True

        if not self.nickname:
            self.stop()
            return

        # Запускаем два потока (цикл графического интерфейса и поток приема)
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()


    # Функция для создания графического интерфейса
    def gui_loop(self):
        self.tk_chat_window = tkinter.Tk()
        self.tk_chat_window.configure(bg="lightgray")

        self.chat_lable = tkinter.Label(self.tk_chat_window, text="Chat:", bg="lightgray")
        self.chat_lable.config(font=("Arial", 12))
        self.chat_lable.pack(padx=25, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.tk_chat_window)
        self.text_area.pack(padx=25, pady=5)
        self.text_area.config(state='disabled')

        self.msg_lable = tkinter.Label(self.tk_chat_window, text="Message:", bg="lightgray")
        self.msg_lable.config(font=("Arial", 12))
        self.msg_lable.pack(padx=25, pady=5)

        self.input_area = tkinter.Text(self.tk_chat_window, height=5)
        self.input_area.pack(padx=25, pady=5)

        # Создаём кнопку
        self.send_button = tkinter.Button(self.tk_chat_window, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=25, ipadx=5)

        self.tk_chat_window.mainloop()

        # Когда пользователь закрывает окно (завершается программа)
        self.tk_chat_window.protocol("WM_DELETE_WINDOW", self.stop)

    def write(self):
        # get('1.0', 'end') - означает получение всего текста
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    # Функция остановки
    def stop(self):
        self.running = False
        if self.tk_chat_window:
            self.tk_chat_window.destroy()
        self.sock.close()
        exit(0)


    # Функция обрабатывает новые соединения, мы получаем новые сообщения от сервера
    def receive(self):
        while self.running:
            try:
                # пытаемся получить сообщение от сервера
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.sock.send(self.nickname)
                else:
                    if self.tk_chat_window:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disable')

            except ConnectionAbortedError:
                break
            except:
                print('Error')
                self.sock.close()
                break


HOST = '127.0.0.1'
PORT = 9090

client = Client(HOST, PORT)
