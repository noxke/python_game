import time
from random import randint
import keyboard
import win32console
import threading
import os

class Buffers():
    def __init__(self, num=2):
        '''
        控制台多缓冲区
        '''
        self.__num = num
        self.__buffer_list = []
        self.__create_buffers()
        self.__current = 0
        self.__last = 0

    def __create_buffers(self):
        for i in range(self.__num):
            self.__buffer_list.append(win32console.CreateConsoleScreenBuffer())

    def print(self, str='\n'):
        '''
        向缓冲区输入内容
        '''
        self.__buffer_list[self.__current].WriteConsole(str)

    def switch(self):
        '''
        切换刷新缓冲区
        '''
        self.__last = self.__current
        self.__current = (self.__current + 1) % self.__num
        self.__buffer_list[self.__current] = win32console.CreateConsoleScreenBuffer()

    def flash(self):
        '''
        刷新显示缓冲区
        '''
        self.__buffer_list[self.__current].SetConsoleActiveScreenBuffer()   # 使当前缓冲区可见
        self.__buffer_list[self.__last].Close() # 关闭上一个缓冲区

# Buffers()类的demo
# buffer = Buffers(5)
# n = 0
# while (n < 100):
#     buffer.switch() # 第一步切换到下一个缓冲区(此时显示的还是上一个缓冲区)
#     buffer.print("当前的buffer是: {}".format(n % 5))    # 向缓冲区输入内容
#     buffer.flash()  # 输入所有内容后刷新缓冲区
#     time.sleep(0.1)
#     n += 1


class Map():
    def __init__(self, width=10, height=10):
        if (width < 10):
            width = 10
        if (height < 10):
            height = 10
        self.size = (width, height)
        self.__map = [[0 for i in range(width)] for i in range(height)]
        # 0为空白块，1为食物，2为炸弹，3为蛇头，4为蛇尾

    def read(self, x, y):
        if (x >= 0 and x < self.size[0] and y >= 0 and y < self.size[1]):
            return self.__map[y][x]
        return -1

    def write(self, x, y, val=0):
        self.__map[y][x] = val

    def list(self):
        '''
        将地图按行返回到列表中
        '''
        ls = []
        ls.append('# ' * (self.size[0] + 2))
        for line in self.__map:
            li = '# '
            for k in line:
                if (k == 0):
                    li += '  '
                elif (k == 1):
                    li += "\033[0;32m$\033[0m "
                elif (k == 2):
                    li += "\033[0;31m@\033[0m "
                elif (k == 3):
                    li += "\033[0;33m■\033[0m "
                elif (k == 4):
                    li += "\033[0;36m■\033[0m "
            li += '#'
            ls.append(li)
        ls.append('# ' * (self.size[0] + 2))
        return ls

# ma = Map(20, 20)
# ls = ma.list()
# for line in ls:
#     print(line)

class Food():
    def __init__(self, map : Map):
        self.x = randint(0, map.size[0] - 1)
        self.y = randint(0, map.size[1] - 1)
        while (map.read(self.x, self.y) != 0):
            self.x = randint(0, map.size[0] - 1)
            self.y = randint(0, map.size[1] - 1)
        self.life = randint(3, 6)

class Foods():
    def __init__(self):
        self.list = []

    def update(self, map : Map):
        tmp = self.list.copy()
        self.list.clear()
        if (randint(0, 49) == 0):
            tmp.append(Food(map))
        for food in tmp:
            map.write(food.x, food.y, 0)
            food.life -= 1 / 50
            if (food.life > 0):
                self.list.append(food)
        del tmp
        for food in self.list:
            map.write(food.x, food.y, 1)

    def eat(self, x, y):
        for index, food in enumerate(self.list):
            if (food.x == x and food.y == y):
                self.list[index].life = 0


class Bomb():
    def __init__(self, map : Map):
        self.x = randint(0, map.size[0] - 1)
        self.y = randint(0, map.size[1] - 1)
        while (map.read(self.x, self.y) != 0):
            self.x = randint(0, map.size[0] - 1)
            self.y = randint(0, map.size[1] - 1)
        self.life = randint(3, 6)

class Bombs():
    def __init__(self):
        self.list = []

    def update(self, map : Map):
        tmp = self.list.copy()
        self.list.clear()
        if (randint(0, 49) == 0):
            tmp.append(Bomb(map))
        for bomb in tmp:
            map.write(bomb.x, bomb.y, 0)
            bomb.life -= 1 / 50
            if (bomb.life > 0):
                self.list.append(bomb)
        del tmp
        for bomb in self.list:
            map.write(bomb.x, bomb.y, 2)


class Snake():
    def __init__(self, map : Map):
        # [x, y]
        self.__head = [randint(3, map.size[0] - 5), randint(3, map.size[1] - 5)]
        # [[x, y], [x, y], ....]
        self.__body = []
        self.__direction = randint(1, 4)

    def move(self, map : Map, direction=0):
        self.__body.insert(0, [self.__head[0], self.__head[1]])
        map.write(self.__body[0][0], self.__body[0][1], 4)    # 第一节身体位置移动到原蛇头位置
        map.write(self.__body[-1][0], self.__body[-1][1], 0)    # 删除最后一节蛇尾位置
        if (direction != 0):
            self.__direction = direction
        if (self.__direction == 1):     # 向上
            self.__head[1] -= 1
        elif (self.__direction == 2):   # 向下
            self.__head[1] += 1
        elif (self.__direction == 3):   # 向左
            self.__head[0] -= 1
        elif (self.__direction == 4):   # 向右
            self.__head[0] += 1
        result = map.read(self.__head[0], self.__head[1])   # 移动结果
        longer = False
        move = True
        tip = "just move"
        if (result == -1):  # 碰墙
            move = False
            tip = "hit the wall"
        elif (result == 1): # 碰到食物
            longer = True
            tip = "eat food"
        elif (result == 2): # 碰到炸弹
            move = False
            tip = "hit the bomb"
        elif (result == 4): # 碰到蛇尾
            move = False
            tip = "eat your body"
        else:
            pass
        if (move):
            if (not longer):
                self.__body.pop()
            else:
                map.write(self.__body[-1][0], self.__body[-1][1], 4)
            map.write(self.__head[0], self.__head[1], 3)
        return (tip, (self.__head[0], self.__head[1]))


def key_envent(key):
    global direction
    global gaming
    global pause
    if (key.name == "up"):
        direction = 1
    elif (key.name == "down"):
        direction = 2
    elif (key.name == "left"):
        direction = 3
    elif (key.name == "right"):
        direction = 4
    elif (key.name == "space"):
        pause = not pause
    elif (key.name == "esc" and gaming):
        gaming = False

def num(d, line):
    if (line == 1):
        if (d in [1]):
            return "      #"
        elif (d in [2, 3, 5, 6, 7, 8, 9, 0]):
            return "# # # #"
        elif (d in [4]):
            return "#     #"
    elif (line == 2):
        if (d in [1, 2, 3, 7]):
            return "      #"
        elif (d in [4, 8, 9, 0]):
            return "#     #"
        elif (d in [5, 6]):
            return "#      "
    elif (line == 3):
        if (d in [1, 7]):
            return "      #"
        elif (d in [2, 3, 4, 5, 6, 8, 9]):
            return "# # # #"
        elif (d in [0]):
            return "#     #"
    elif (line == 4):
        if (d in [1, 3, 4, 5, 7, 9]):
            return "      #"
        elif (d in [2]):
            return "#      "
        elif (d in [6, 8, 0]):
            return "#     #"
    elif (line == 5):
        if (d in [1, 4, 7]):
            return "      #"
        elif (d in [2, 3, 5, 6, 8, 9, 0]):
            return "# # # #"

def show_info(map_ls, score, game_time):
    ls = ["",
        "\033[0;36m  # # # #    \033[0m  ",
        "\033[0;36m     #       \033[0m  ",
        "\033[0;36m     #       \033[0m  ",
        "\033[0;36m     #       \033[0m  ",
        "\033[0;36m     #       \033[0m  ",
        "",
        "\033[0;32m  # # # #    \033[0m  ",
        "\033[0;32m  #          \033[0m  ",
        "\033[0;32m  # # # #    \033[0m  ",
        "\033[0;32m        #    \033[0m  ",
        "\033[0;32m  # # # #    \033[0m  "]
    a = game_time // 100 % 10
    b = game_time // 10 % 10
    c= game_time % 10
    for i in range(1, 6):
        ls[i] = ls[i] + "\033[0;34m" + num(a, i) + "  " + num(b, i) + "  " + num(c, i) + "\033[0m"
    a = score // 100 % 10
    b = score // 10 % 10
    c = score % 10
    for i in range(1, 6):
        ls[i + 6] = ls[i + 6] + "\033[0;35m" + num(a, i) + "  " + num(b, i) + "  " + num(c, i) + "\033[0m"
    for i in range(12):
        map_ls[i] += ls[i]
    return map_ls


def end(tip, score, map_ls):
    os.system("cls")
    for line in map_ls:
        print(line)
    if (tip == "hit the wall"):
        print("\033[0;31m您撞墙后不治身亡!\033[0m")
    elif (tip == "hit the bomb"):
        print("\033[0;31m炸弹真美味, 可惜会爆炸\033[0m")
    elif (tip == "eat your body"):
        print("\033[0;31m您真狠, 饿了连自己都不放过\033[0m")
    elif (tip == ""):
        print("\033[0;31m请问你为什么要退出游戏呢?\033[0m")
    print("\033[0;33m游戏结束\033[0m")
    print("\033[0;34m您的得分为: \033[0;32m{}\033[0m".format(score))
    print("\033[0;33m输入任意内容退出游戏  \033[0;32m输入\033[0;34m空格\033[0;32m重新开始游戏\033[0m")

def game():
    global direction
    global gaming
    global pause
    buffers = Buffers()
    game_map = Map(20, 20)
    bombs = Bombs()
    foods = Foods()
    snake = Snake(game_map)
    tick = 0
    direction = 0
    score = 0
    tip = ""
    map_ls = []
    gaming = True
    pause = False
    start_time = time.time()
    while gaming:
        if (pause):
            start_time += 1
            time.sleep(1)
            continue
        loop_time = time.perf_counter()    # 记录循环开始时间

        move = ("just move", (0, 0))
        if (tick == 0):
            move = snake.move(game_map, direction)
        if (move[0] == "eat food"):
            foods.eat(move[1][0], move[1][1])
            score += 1
        elif (move[0] != "just move"):
            tip = move[0]
            gaming = False
            break
        foods.update(game_map)
        bombs.update(game_map)

        buffers.switch()
        map_ls = game_map.list()
        map_ls = show_info(map_ls, score, int(time.time() - start_time)) # 添加提示信息
        for line in map_ls:
            buffers.print(line+'\n')
        buffers.print("ESC键退出游戏  空格键暂停\\继续")
        buffers.flash()

        tick = (tick + 1) % 5
        time.sleep(0.02 - (loop_time - time.perf_counter()))
    end(tip, score, map_ls)


def main():
    keyboard.on_press(key_envent)
    while True:
        game_thread = threading.Thread(target=game)
        game_thread.setDaemon(False)
        game_thread.start()
        game_thread.join()
        if (input("\n") != " "):
            break

main()