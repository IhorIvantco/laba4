from tkinter import *
import time
import socket
import threading


root = Tk()
root.title('[ Gamer 2 ]')
root.geometry('400x250')   # 470 / 700 || 1410 / 700
canv = Canvas(root, bg='#BC2E2E')
canv.pack(fill=BOTH, expand=1)
root.resizable(width=False, height=False)



host = 'localhost'		
port = 0
server = ('localhost', 2021)   
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(False)
shutdown = False
data = ''
s.sendto('g2.py'.encode('utf-8'), server)



class ball:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.position = [self.x, self.y]
        self.map = ''
        self.status = ''
        self.lin = [self.map, self.position, self.status]
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.goal = 0
        self.id = canv.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r, fill='white')

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.position[0] = self.x
        self.position[1] = self.y
        active_wall = list(set(canv.find_withtag('wall')) & set(
            canv.find_overlapping(self.x - self.r * 0.7, self.y - self.r * 0.7, self.x + self.r * 0.7,
                                  self.y + self.r * 0.7)))
        if active_wall:
            if 'x' in canv.gettags(active_wall[0]):
                self.vx = -self.vx
            if 'y' in canv.gettags(active_wall[0]):
                self.vy = -self.vy
                x1, y1, x2, y2 = canv.coords(active_wall[0])
                xc = (x1 + x2) / 2
                w = abs(x1 - x2)
                self.vx += (self.x - xc) / w * 10
        self.paint()
        lines = canv.find_overlapping(self.x - self.r * 0.7, self.y - self.r * 0.7, self.x + self.r * 0.7,
                                      self.y + self.r * 0.7)
        if len(lines) > 1:
            if "g1" in canv.gettags(lines[1]):
                self.goal = 'g1'
                self.kill()
            if "g2" in canv.gettags(lines[1]):
                self.goal = 'g2'
                self.kill()

    def kill(self):
        global game
        game = 1
        if self.goal == 'g1':
            self.map = '[Gamer2 -> Ball] :: '
            self.lin[0] = self.map
            self.lin[1] = self.position
            s.sendto(f'{self.lin[0]}${self.lin[1][0]}${self.lin[1][1]}'.encode('utf-8'), server)
            self.x = 235  
            self.y = 800 
            self.vx = 0
            self.vy = 0
            self.goal = 0
        elif self.goal == 'g2':
            self.map = '[Ball -> Goal_g2] :: '
            self.lin[0] = self.map
            self.status = '!Goal to Gamer2!'
            self.lin[2] = self.status
            s.sendto(f'{self.lin[0]}&{self.lin[2]}'.encode('utf-8'), server)
            self.x = 235 
            self.y = 800
            self.vx = 0
            self.vy = 0
            self.goal = 0
        self.paint()

    def paint(self):
        canv.coords(self.id, self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)


class gamer:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 60  # Довжина
        self.v = 3  # Швидкість
        self.d = 4  # Ширина
        self.mode = ''
        self.score = 0 
        self.xy_score = (0, 0)  
        self.id = canv.create_rectangle(self.x - self.w, self.y - self.d, self.x + self.w, self.y + self.d,
                                        fill='white', tags=('wall', 'y'))
        self.id_score = canv.create_text(0, 0, text='', font='Tahoma 24', fill='white')

    def paint(self):
        canv.coords(self.id, self.x - self.w, self.y - self.d, self.x + self.w, self.y + self.d)
        canv.coords(self.id_score, self.xy_score[0], self.xy_score[1])
        canv.itemconfig(self.id_score, text=self.score)

    def move(self): 
        if self.mode == 'left' and self.x > (10 + self.w):
            self.x -= self.v
        elif self.mode == 'right' and self.x < (390 - self.w):
            self.x += self.v
        self.paint()



b = ball()
b.x = 235
b.y = 800
b.vx = 0   
b.vy = 0   


# ---Створення стін---
canv.create_line(5, 245, 395, 245, width=2, fill='white', tags='g1')  # Bottom
canv.create_line(5, 5, 395, 5, width=2, fill='white', tags='g2')  # up | Торкання на 463

canv.create_line(5, 4, 5, 246, width=5, fill='white', tag=('wall', 'x'))  # left
canv.create_line(395, 4, 395, 246, width=5, fill='white', tag=('wall', 'x'))  # right

# --------------------

# ---Створення гравців---
g2 = gamer()
g2.x = 200 # Розташування по х
g2.y = 20  # Розташування по у
g2.paint()
g2.xy_score = (200, 150)  # Рахунок
game = 1
# -----------------------


# ---Нажимання клавіш---
def key_press(event):
    global game
    if event.keycode == 37:  # 37 = '<-'
        g2.mode = 'left'
    elif event.keycode == 39:   # 39 = '->'
        g2.mode = 'right'
    elif event.keycode == 32:   # 32 = 'Пробіл'
        game = 1


def key_release(event):
    if event.keycode == 37 or event.keycode == 39:
        g2.mode = ''


root.bind('<Key>', key_press)
root.bind('<KeyRelease>', key_release)
# ----------------------


# ---Обробка повідомлень---
def receving(name, sock):   # Прийнаття повідомлень
    global data
    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                data = data.decode('utf-8')
                print(data)

                time.sleep(0.2)
        except:
            pass


print('--- [ Gamer 2 ] ---')
print(f'IP :: {host}\n')
rT = threading.Thread(target=receving, args=('RecvThread', s))
rT.start()
# -------------------------

while 1:
    if game:
        b.move()
    g2.move()
    if b.goal == 1:
        b.goal = 0
    elif b.goal == 2:
        b.goal = 0
    time.sleep(0.02)
    canv.update()

    # ---Телепортаці і голи---
    if '$' in data:
        data_lin = data.split('$')  # [0] - x | [1] - y
        data = data.replace('$', '')
        data_x = float(data_lin[0])  # Зсування до лівої частини
        data_y = 200
        b.x = data_x
        b.y = data_y
        b.vx = 4
        b.vy = -4
        b.kill()
    elif data == '1':
        data = ''
        g2.score += 1
    # ------------------------

root.mainloop()
rT.join()
s.close()
