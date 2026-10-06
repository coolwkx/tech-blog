---
article_id: kp-d49e27fb8f63d220
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-d512e4a67eb2
learning_sourceId: d512e4a67eb2
learning_order: 5
learning_objective: 理解并验证：软链接、环境变量、打包与 Shell 脚本
---

# 软链接、环境变量、打包与 Shell 脚本

> **学习目标**：能够解释「软链接、环境变量、打包与 Shell 脚本」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：建议先掌握 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) 中的 `ls/cd/mkdir/cp/mv/rm/find/grep/管道/重定向/vi`。
>
> **所属主题**：-Linux实用操作 · 可运行示例

## 本次只学这一点

```sh
# ---------- 1. 软链接：给长路径起个短名字 ----------
ln -s /etc/sysconfig/network-scripts/ifcfg-ens33 ip
ls -l ip
cat ip # 读链接即读目标文件
echo 'IPADDR="192.168.88.77"' >> ip # 改链接即改目标文件
systemctl restart network && ifconfig

# ---------- 2. 硬链接：同一份数据的两个名字 ----------
echo "hello" > 1.txt
ln 1.txt 3.txt
echo "world" >> 3.txt
cat 1.txt # 两个文件内容同步变化

# ---------- 3. 环境变量 ----------
env
echo $PATH
name=zhangsan
age=23
echo ${name}
echo 姓名: ${name}, 年龄: ${age}
vim /etc/profile # 在文件末尾追加 export PATH=$PATH:/opt/demo
source /etc/profile # 立即生效，否则要重新登录
echo $PATH

# ---------- 4. 打包与解压 ----------
tar -zcvf my.tar.gz *.txt # 压缩
mkdir -p aa
tar -zxvf my.tar.gz -C aa/ # 解压到 aa/
zip -r my.zip *.txt
unzip my.zip -d aa/

# ---------- 5. 传文件（需先安装 lrzsz） ----------
yum -y install lrzsz
rz # 上传
sz my.tar.gz # 下载

# ---------- 6. Shell 脚本 ----------
echo $SHELL # 查看默认解析器，如 /bin/bash
vim 1.sh
# --- 文件内容 ---
# name='张三'
# age=23
# echo 姓名:${name}, 年龄:${age}
# ---------------
sh 1.sh # 方式1：对文件无执行权限要求
source 1.sh # 方式2：对文件无执行权限要求，在当前 Shell 中执行
chmod 777 1.sh # 方式3/4：需要执行权限
/root/1.sh # 绝对路径执行
./1.sh # 相对路径执行
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「软链接、环境变量、打包与 Shell 脚本」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)
