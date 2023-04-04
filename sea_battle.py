from random import randint

size = 0

def Hello():
    print('_' * 35)
    print("  Приветствую тебя  ")
    print("      в игре       ")
    print('   "Морской бой"!   ')
    print('_' * 35)
    print(" Формат ввода: X, Y")
    print(" X - номер строки")
    print(" Y - номер столбца")
    global size
    while True:
        dif_level = input('_' * 35 +
                                '\nВыбери уровень сложности: '
                                '\nнажми 1 (легкий), 2 (средний) или 3 (сложный) '
                                '\n(от уровня сложности зависит размер поля) ___ ')
        if not dif_level.isnumeric():
            print(''
                  '\nНекорректный ввод! Попробуй снова.')
        elif not 1 <= int(dif_level) <= 3:
            print(''
                  '\nНекорректное число! Попробуй снова.')
        else:
            if int(dif_level) == 1:
                size = 6
                break
            elif int(dif_level) == 2:
                size = 7
                break
            else:
                size = 8
                break
    return size


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Ты пытаешься выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Ты уже стрелял в эту клетку!"

class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:

    def __init__(self, hid = False):
        self.hid = hid
        self.count = 0
        self.field = [["_"] * size for _ in range(size)]
        self.busy = []
        self.ships = []


    def __str__(self):
        res = ""
        if size == 6:
            res += "   _1_|_2_|_3_|_4_|_5_|_6_"
        elif size == 7:
            res += "   _1_|_2_|_3_|_4_|_5_|_6_|_7_"
        else:
            res += "   _1_|_2_|_3_|_4_|_5_|_6_|_7_|_8_"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "_")
        return res

    def out(self, d):
        return not ((0 <= d.x < size) and (0 <= d.y < size))

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, size), randint(0, size))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Твой ход: ").split()

            if len(cords) != 2:
                print(" Введи 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введи цифры!')
                continue

            x, y= int(x), int(y)

            return Dot(x - 1, y -1)


class Game:
    def __init__(self):
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, size), randint(0, size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board


    def loop(self):
        num = 0
        while True:
            print('_' * 35)
            print('')
            print("Доска пользователя:")
            print(self.us.board)
            print('_' * 35)
            print('')
            print("Доска компьютера:")
            print(self.ai.board)
            print('_' * 35)
            print('')
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print('')
                print('_' * 35)
                print("Поздравляю! Ты победил! ☻")
                print('')
                print('Нажми Enter, чтобы выйти из игры.')
                break

            if self.us.board.defeat():
                print('_' * 35)
                print("Увы, искусственный разум одержал победу над тобой... ")
                print('')
                print('Нажми Enter, чтобы выйти из игры.')
                break
            num += 1

    def start(self):
        self.loop()


Hello()
g = Game()
g.start()