import random


# 用工厂模式
class Specialized:
    def __init__(self, name, teacher, location):
        self.name = name
        self.teacher = teacher
        self.location = location

    def lesson(self):
        pass


class It(Specialized):

    def lesson(self):
        m, n = random.randint(1, 10), random.randint(1, 10)
        return f'随机生成2个10以内的数字:{m},{n}'


class English(Specialized):

    def lesson(self):
        l = []
        m = random.randint(0, 26)
        abc = [chr(i) for i in range(97, 123)]
        for _ in range(m):
            l.append(random.choice(abc))
            abc.remove(l[-1])
        return f'随机生成一个小于26的数字{m}，并随机输出m个不重复的小写英文字母组成的字符串：' + ''.join(l)


class Math(Specialized):

    def lesson(self):
        m = random.randint(100, 1000)
        a = m % 10
        b = m // 10 % 10
        c = m // 100
        n = a * 100 + b * 10 + c
        if a == 0:
            n = '0' + str(b) + str(c)
        return f'随机生成一个3位的正整数:{m}，并反转输出:{n}'


class WenXue(Specialized):

    def lesson(self):
        m = []
        for _ in range(3):
            val = random.randint(0x4e00, 0x9fa5)
            m.append(chr(val))
        return '随机输出3个汉字:' + ''.join(m)


class SpecializedFactory:
    def __init__(self):
        self.specialized_objects = {
            '计算机': It,
            '英语': English,
            '数学': Math,
            '文学': WenXue,
        }

    def create_specialized(self, name, teacher, location):
        return self.specialized_objects[name](name, teacher, location)


specialized_info = {
    '计算机': {'teacher': '张四', 'location': 'A', 'plan': 'plan_a'},
    '英语': {'teacher': '李五', 'location': 'B', 'plan': 'plan_b'},
    '数学': {'teacher': '王六', 'location': 'C', 'plan': 'plan_c'},
    '文学': {'teacher': '赵七', 'location': 'D', 'plan': 'plan_d'},
}

specialized_objects = {}

for name, info in specialized_info.items():
    specialized_objects[name] = SpecializedFactory().create_specialized(name, info['teacher'], info['location'])
while True:
    student = input('请输入学生姓名：')
    with open('students.csv', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            name, specialized = line.strip().split(',')
            if student == name:
                print(f'学生姓名：{name}, 专业名称：{specialized}')
                print(f'专业老师：{specialized_objects[specialized].teacher}')
                print(f'教师地点：{specialized_objects[specialized].location}')
                print(f'上课操作：{specialized_objects[specialized].lesson()}')
                break
        else:
            print('学生不存在')
