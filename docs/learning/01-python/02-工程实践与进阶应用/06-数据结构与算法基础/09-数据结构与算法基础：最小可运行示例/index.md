---
article_id: kp-a3b83d42f61c1468
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-0875a16659df
learning_sourceId: 0875a16659df
learning_order: 8
learning_objective: 理解并验证：数据结构与算法基础：最小可运行示例
---

# 数据结构与算法基础：最小可运行示例

> **学习目标**：能够解释「数据结构与算法基础：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：列表与字典的复杂度直觉（01 篇）、函数与递归（02 篇）、类与对象（03 篇）。
>
> **所属主题**：数据结构与算法基础 · 最小可运行示例

## 本次只学这一点

```text
import time

# ---------- 1) 复杂度实测：三层循环 O(n^3) vs 代入法 O(n^2) ----------
def brute_force_triple(n):
 cnt = 0
 for a in range(1, n + 1):
 for b in range(1, n + 1):
 for c in range(1, n + 1):
 if a + b + c == n and a * a + b * b == c * c:
 cnt += 1
 return cnt

def brute_force(n):
 cnt = 0
 for a in range(1, n + 1):
 for b in range(1, n + 1):
 c = n - a - b # 用已知关系消掉一层循环
 if c > 0 and a * a + b * b == c * c:
 cnt += 1
 return cnt

# ---------- 2) 单链表：结点 + 链表两个类 ----------
class SingleNode:
 def __init__(self, item):
 self.item = item
 self.next = None

class SingleLinkList:
 def __init__(self, node=None):
 self.head = node

 def is_empty(self):
 return self.head is None

 def length(self):
 cur, count = self.head, 0
 while cur is not None: # 注意：不是 cur.next
 count += 1
 cur = cur.next
 return count

 def travel(self):
 out, cur = [], self.head
 while cur is not None:
 out.append(cur.item)
 cur = cur.next
 return out

 def add(self, item): # 头插 O(1)
 node = SingleNode(item)
 node.next = self.head # 顺序绝不能反
 self.head = node

 def append(self, item): # 尾插 O(n)
 node = SingleNode(item)
 if self.is_empty:
 self.head = node
 return
 cur = self.head
 while cur.next is not None:
 cur = cur.next
 cur.next = node

 def insert(self, pos, item):
 if pos <= 0:
 self.add(item)
 elif pos >= self.length:
 self.append(item)
 else:
 node, cur = SingleNode(item), self.head
 for _ in range(pos - 1):
 cur = cur.next
 node.next, cur.next = cur.next, node

 def search(self, item):
 cur = self.head
 while cur is not None:
 if cur.item == item:
 return True
 cur = cur.next
 return False

 def remove(self, item):
 cur, pre = self.head, None
 while cur is not None:
 if cur.item == item:
 if pre is None: # 删头结点要单独处理
 self.head = cur.next
 else:
 pre.next = cur.next
 return True
 pre, cur = cur, cur.next
 return False

# ---------- 3) 排序：冒泡（带提前退出）与快速 ----------
def bubble_sort(alist):
 n = len(alist)
 for j in range(n - 1):
 count = 0
 for i in range(n - j - 1):
 if alist[i] > alist[i + 1]:
 alist[i], alist[i + 1] = alist[i + 1], alist[i]
 count += 1
 if count == 0: # 一轮无交换 → 已有序，最优 O(n)
 break
 return alist

def quick_sort(alist):
 if len(alist) <= 1:
 return alist
 pivot = alist[len(alist) // 2]
 return (quick_sort([x for x in alist if x < pivot])
 + [x for x in alist if x == pivot]
 + quick_sort([x for x in alist if x > pivot]))

# ---------- 4) 二分查找（非递归版，教材写法） ----------
def binary_search(alist, item):
 start, end = 0, len(alist) - 1
 while start <= end: # 必须含等号
 mid = (start + end) // 2
 if item == alist[mid]:
 return True
 elif item < alist[mid]:
 end = mid - 1
 else:
 start = mid + 1
 return False

def linear_search(alist, item):
 for x in alist:
 if x == item:
 return True
 return False

# ---------- 5) 二叉树：层序插入 + 遍历 + 由先序中序还原 ----------
class Node:
 def __init__(self, item):
 self.item = item
 self.lchild = None
 self.rchild = None

class BinaryTree:
 def __init__(self, node=None):
 self.root = node

 def add(self, item):
 """用队列找第一个空位，保证得到完全二叉树"""
 node = Node(item)
 if self.root is None:
 self.root = node
 return
 queue = [self.root]
 while queue:
 cur = queue.pop(0)
 if cur.lchild is None:
 cur.lchild = node
 return
 queue.append(cur.lchild)
 if cur.rchild is None:
 cur.rchild = node
 return
 queue.append(cur.rchild)

 def breadth_travel(self):
 if self.root is None:
 return []
 out, queue = [], [self.root]
 while queue: # 层序 = 队列 + 广度优先
 cur = queue.pop(0)
 out.append(cur.item)
 if cur.lchild is not None:
 queue.append(cur.lchild)
 if cur.rchild is not None:
 queue.append(cur.rchild)
 return out

 def preorder(self, root): # 根左右
 if root is None:
 return []
 return [root.item] + self.preorder(root.lchild) + self.preorder(root.rchild)

 def inorder(self, root): # 左根右
 if root is None:
 return []
 return self.inorder(root.lchild) + [root.item] + self.inorder(root.rchild)

def build_from_pre_in(preorder, inorder):
 """由先序 + 中序还原二叉树"""
 if not preorder:
 return None
 node = Node(preorder[0]) # 先序第一个是根
 idx = inorder.index(preorder[0]) # 中序里根的位置划分左右子树
 node.lchild = build_from_pre_in(preorder[1:1 + idx], inorder[:idx])
 node.rchild = build_from_pre_in(preorder[1 + idx:], inorder[idx + 1:])
 return node

if __name__ == "__main__":
 for n in (150, 300):
 t = time.perf_counter; brute_force_triple(n); t3 = time.perf_counter - t
 t = time.perf_counter; brute_force(n); t2 = time.perf_counter - t
 print(f"n={n}: O(n^3) {t3:.3f}s | O(n^2) {t2:.3f}s")

 print("排序:", bubble_sort([5, 3, 4, 7, 2]), quick_sort([5, 3, 4, 7, 2]))

 arr = list(range(0, 100, 2))
 print("二分找 70:", binary_search(arr, 70), "| 找 71:", binary_search(arr, 71))
 big = list(range(1_000_000))
 t = time.perf_counter; binary_search(big, 999_999); tb = time.perf_counter - t
 t = time.perf_counter; linear_search(big, 999_999); tl = time.perf_counter - t
 print(f"100 万元素: 二分 {tb*1000:.4f} ms | 线性 {tl*1000:.3f} ms")

 ll = SingleLinkList
 for x in [1, 2, 3]:
 ll.append(x)
 ll.add(0); ll.insert(2, 99)
 print("链表:", ll.travel, "长度:", ll.length, "search(99):", ll.search(99))

 tree = BinaryTree
 for ch in "ABCDEFGHIJK":
 tree.add(ch)
 print("层序:", tree.breadth_travel)
 print("先序:", tree.preorder(tree.root))
 print("中序:", tree.inorder(tree.root))
 rebuilt = BinaryTree(build_from_pre_in("0137849256", "7381940526"))
 print("还原后中序:", "".join(rebuilt.inorder(rebuilt.root)))
```

本机实测输出：

```text
n=150: O(n^3) 0.103s | O(n^2) 0.001s
n=300: O(n^3) 1.012s | O(n^2) 0.007s
排序: [2, 3, 4, 5, 7] [2, 3, 4, 5, 7]
二分找 70: True | 找 71: False
100 万元素: 二分 0.0078 ms | 线性 15.763 ms
链表: [0, 1, 99, 2, 3] 长度: 4 search(99): True
层序: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
先序: ['A', 'B', 'D', 'H', 'I', 'E', 'J', 'K', 'C', 'F', 'G']
中序: ['H', 'D', 'I', 'B', 'J', 'E', 'K', 'A', 'F', 'C', 'G']
还原后中序: 7381940526
```

**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| n 从 150 翻倍到 300 | `O(n³)` 耗时 0.103 → 1.012s（约 10 倍），`O(n²)` 只从 0.001 → 0.007s。**复杂度可预测，运行时间不可预测** |
| `count` 提前退出 | 冒泡"最优 `O(n)`"的唯一来源；不加这个优化最优也是 `O(n²)` |
| 快排用推导式分区 | 可读性最好，但每层新建列表，空间是 `O(n log n)`；原地分区版空间 `O(log n)` |
| `while start <= end` | 二分必须含等号，否则漏查"区间只剩一个元素"的情况 |
| 100 万元素：二分 `0.0078ms` vs 线性 `15.763ms` | 约 2000 倍差距，直观印证 `O(log n)` 与 `O(n)` 的量级差 |
| `node.next = self.head` 先执行 | 头插两行顺序绝不能反，反了就丢掉整条链表 |
| 链表遍历用 `while cur is not None` | 用 `while cur.next` 会漏掉最后一个结点 |
| 二叉树 `add` 用队列 | 层序插入才能得到完全二叉树 |
| `build_from_pre_in` | 先序定根、中序分左右，再递归；**只有先序+后序无法唯一还原** |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/06-CPython与算法/10-数据结构与算法基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据结构与算法基础：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/06-CPython与算法/10-数据结构与算法基础.md)
