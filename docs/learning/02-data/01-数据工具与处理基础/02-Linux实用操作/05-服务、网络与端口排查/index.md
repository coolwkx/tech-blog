---
article_id: kp-7f995e3906cfb42a
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-d512e4a67eb2
learning_sourceId: d512e4a67eb2
learning_order: 4
learning_objective: 理解并验证：服务、网络与端口排查
---

# 服务、网络与端口排查

> **学习目标**：能够解释「服务、网络与端口排查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：建议先掌握 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) 中的 `ls/cd/mkdir/cp/mv/rm/find/grep/管道/重定向/vi`。
>
> **所属主题**：-Linux实用操作 · 可运行示例

## 本次只学这一点

```sh
# ---------- 1. 查看 IP 与主机名 ----------
ifconfig
hostname
hostnamectl set-hostname mynode1

# ---------- 2. IP 变成 127.0.0.1 的经典处理 ----------
systemctl stop NetworkManager # 关闭主网络服务
systemctl disable NetworkManager # 禁止其开机自启
systemctl restart network # 重启副网络服务
ifconfig # 重新查看 IP

# ---------- 3. 配置域名映射（之后可用域名代替 IP） ----------
vim /etc/hosts
# 追加一行：192.168.88.100 mynode1 mynode1.

# ---------- 4. 连通性测试与下载 ----------
ping -c 3 www.baidu.com
wget https://www./ -O .html
curl https://www./ >> .txt

# ---------- 5. 端口与进程 ----------
netstat -anp | grep 3306 # 谁占用了 MySQL 端口
netstat -anp | grep ssh
ps -ef | grep ssh # 找到 sshd 的 pid
kill -9 <pid> # 强制结束（先确认 pid 无误）

# ---------- 6. 常用服务控制 ----------
systemctl status network
systemctl enable network # 开机自启
systemctl disable network # 取消开机自启
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「服务、网络与端口排查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)
