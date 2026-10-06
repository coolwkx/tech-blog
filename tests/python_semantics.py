"""Run small, dependency-free examples used by the Python object lessons."""
from copy import deepcopy

class Bag:
    def __len__(self):
        return 3

assert len(Bag()) == 3
a = [1, 2]
b = a
b += [3]
assert a == [1, 2, 3] and a is b
x = [[1]]
shallow = x.copy()
deep = deepcopy(x)
shallow[0].append(2)
assert x == [[1, 2]] and deep == [[1]]
repeated = [[]] * 2
repeated[0].append(1)
assert repeated == [[1], [1]]
print('Python 对象协议、变量绑定、浅深拷贝和重复引用示例通过。')
