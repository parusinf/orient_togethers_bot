from tools import ftimedelta, ptimedelta
import config as cfg
from copy import copy


class Race:
    def __init__(self, data: list):
        """
        Забег
        :param data: данные забега в формате orgeo.ru
        1
        Корвяков Николай №348
        Протвино, лично
        37:30
        +00:00	12:19:00	02:11 (54)	03:36 (32)	06:22 (40)	10:48 (62)	13:19 (37)	15:02 (36)	17:51 (35)	19:41 (60)	22:16 (34)	24:22 (33)	28:38 (38)	31:02 (58)	31:49 (45)	33:33 (46)	35:12 (57)	37:10 (100)
        """
        if len(data) < 5:
            raise IndexError('Таблица результатов должна быть в формате orgeo.ru')
        self.place = int(data[0])
        name = data[1].split(' ')
        self.family = name[0]
        self.name = name[1]
        self.number = int(name[2][1:])
        self.team = data[2]
        self.result = ptimedelta(data[3])
        details = data[4].split('\t')
        self.start = ptimedelta(details[1])
        self.cp_time = [self.start + ptimedelta(cp.split(' ')[0]) for cp in details[2:]]
        self.cp_number = [int(cp.split(' ')[1][1:-1]) for cp in details[2:]]
        # Удаление КП, которых нет у того, кто занял первое место
        if self.place == 1:
            Race.cp_number = self.cp_number
        else:
            cp_number = []
            cp_time = []
            for i in range(len(self.cp_number)):
                if self.cp_number[i] in Race.cp_number:
                    cp_number.append(self.cp_number[i])
                    cp_time.append(self.cp_time[i])
            self.cp_number = cp_number
            self.cp_time = cp_time

    def __str__(self):
        return f'Место: {self.place}\nФамилия: {self.family}\nКоманда: {self.team}\n'\
               f'Результат: {ftimedelta(self.result)} {[ftimedelta(t) for t in self.cp_time]}'

    def __eq__(self, other):
        if not isinstance(other, Race):
            raise TypeError("Операнд справа должен иметь тип Race")
        return self.number == other.number


def calc_togethers_pair(a: Race, b: Race):
    # Список КП со встречами
    togethers = []
    a_count = 0
    b_count = 0
    for i in range(len(a.cp_time)):
        if abs(a.cp_time[i] - b.cp_time[i]).seconds < cfg.TOGETHER_SECONDS:
            togethers.append(i+1)
            # a отметился раньше b
            if a.cp_time[i] < b.cp_time[i]:
                a_count += 1
            # a отметился позже b
            else:
                b_count += 1
    if a_count == b_count:
        parovoz = a if a.place < b.place else b
        vagon = a if a.place > b.place else b
    elif a_count > b_count:
        parovoz = a
        vagon = b
    else:
        parovoz = b
        vagon = a
    # КП с минусом, если vagon отметился раньше parovoz
    for i in range(len(togethers)):
        # vagon отметился раньше parovoz
        if vagon.cp_time[togethers[i]-1] < parovoz.cp_time[togethers[i]-1]:
            togethers[i] = -togethers[i]
    return togethers, (parovoz, vagon)
