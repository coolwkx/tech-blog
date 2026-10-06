---
article_id: kp-8bc3cd76db7f6a85
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-94cd3f2167c7
learning_sourceId: 94cd3f2167c7
learning_order: 5
learning_objective: 理解并验证：-Linux基础命令：可运行示例
---

# -Linux基础命令：可运行示例

> **学习目标**：能够解释「-Linux基础命令：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：无需编程基础；了解 Windows 的盘符、文件夹、快捷方式概念即可类比。
>
> **所属主题**：-Linux基础命令 · 可运行示例

## 本次只学这一点

一条主线：建目录 → 造文件 → 查内容 → 过滤 → 写日志 → 追踪 → 编辑 → 求助。以下命令可直接在 root 账号下依次执行。

```sh
# ---------- 1. 定位与创建 ----------
pwd # 查看当前目录，root 登录默认在 /root
mkdir -p aa/bb # 递归创建多级目录，不加 -p 会因 aa 不存在而报错
cd aa/bb # 相对路径进入
pwd # /root/aa/bb
cd - # 回到上一个目录 /root
cd ~ # 回到当前账号家目录

# ---------- 2. 造文件与查看 ----------
touch 1.txt 2.txt # 创建两个空文件
echo "python pandas numpy" >> 1.txt # 追加写入
echo "python mysql" >> 1.txt
echo "java hadoop" >> 2.txt
cat 1.txt # 一次性看全部内容
ls -alh # 长格式 + 隐藏文件 + 人性化大小
ll # 等价于 ls -l

# ---------- 3. 过滤与管道 ----------
grep -n python 1.txt # 只打印含 python 的行，并显示行号
cat 1.txt | grep python | grep numpy # 两级过滤：先 python，再 numpy
cat 1.txt 2.txt | wc -l # 统计总行数（wc = word count）

# ---------- 4. 查找 ----------
which python # 查看 python 命令放在哪个目录
find /root -name '*.txt' # 按文件名查找
find / -size +10M # 找大于 10MB 的文件（递归全盘，较慢）

# ---------- 5. 重定向与日志追踪 ----------
ls / >> 1.txt # 追加，不覆盖原内容
ls / > 3.txt # 覆盖写
tail -3 1.txt # 只看最后 3 行
tail -f 1.txt # 持续追踪（新写入内容会实时打印，Ctrl+C 退出）

# ---------- 6. 复制、移动、删除 ----------
cp 1.txt 1_bak.txt # 复制文件
cp -r aa aa_bak # 复制目录必须加 -r
mv 1_bak.txt 1_old.txt # 同目录下移动 = 改名
rm -rf aa_bak # 递归强制删除目录
# rm -rf /* ← 高危：删掉整个系统，任何情况下都不要执行

# ---------- 7. 编辑配置并求助 ----------
vim /etc/hosts # 按 i 输入，按 Esc，再输入 :wq 保存退出
ls --help # 快速看选项说明
man ls # 看完整手册，按 q 退出
man ls >> ls_manual.txt # 把手册存成文件慢慢看
```

预期输出片段（部分）：

```text
[root@mynode1 ~]# grep -n python 1.txt
1:python pandas numpy
2:python mysql
[root@mynode1 ~]# tail -3 1.txt
python pandas numpy
python mysql
bin
```

用户与权限的最小闭环（`sudo` 赋权）：

```sh
useradd zhangsan # 创建普通用户，默认同时创建一个同名用户组
passwd zhangsan # 为该用户设置密码
vim /etc/sudoers # 找到 root ALL=(ALL) ALL 那一行，仿写一行 zhangsan ALL=(ALL) ALL
su zhangsan # 切换用户
sudo mkdir /opt/test # 借调 root 权限执行；首次需要输入密码，之后短时间内免密
exit # 退回原用户
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-Linux基础命令：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md)
