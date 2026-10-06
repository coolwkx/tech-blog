---
article_id: kp-1679d31b75ff0a93
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-d512e4a67eb2
learning_sourceId: d512e4a67eb2
learning_order: 3
learning_objective: 理解并验证：账号与权限闭环
---

# 账号与权限闭环

> **学习目标**：能够解释「账号与权限闭环」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：建议先掌握 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) 中的 `ls/cd/mkdir/cp/mv/rm/find/grep/管道/重定向/vi`。
>
> **所属主题**：-Linux实用操作 · 可运行示例

## 本次只学这一点

```sh
# ---------- 1. 建组、建用户 ----------
groupadd dev
useradd -g dev zhangsan # 指定主组为 dev
passwd zhangsan # 交互式设置密码
id zhangsan # 查看 uid/gid 与所属组
usermod -aG dev zhangsan # 追加附加组（-a 必须与 -G 连用，否则会覆盖组列表）

# ---------- 2. 查看系统里已有的账号与组 ----------
getent passwd | head -5
getent group | head -5

# ---------- 3. 授权与验证 ----------
mkdir -p /opt/demo
echo "echo hello zhangsan" > /opt/demo/1.sh
chmod 755 /opt/demo/1.sh # 属主 rwx，其他 r-x
ls -l /opt/demo/1.sh
chown zhangsan:dev /opt/demo/1.sh
ls -l /opt/demo/1.sh

# ---------- 4. 符号法调权限（常用组合） ----------
chmod u=rwx,g=rx,o=r /opt/demo/1.sh # 等价于 chmod 754
chmod -R +x /opt/demo # 目录内所有文件追加执行位

# ---------- 5. 切用户并借权 ----------
su zhangsan
sudo ls /root # 首次输入 zhangsan 的密码，短暂免密
exit

# ---------- 6. 删除（-r 连家目录一起删） ----------
userdel -r zhangsan
groupdel dev
```

预期输出片段：

```text
[root@mynode1 ~]# id zhangsan
uid=1001(zhangsan) gid=1001(dev) groups=1001(dev)
[root@mynode1 ~]# ls -l /opt/demo/1.sh
-rwxr-xr-x. 1 zhangsan dev 20 1月 13 12:01 /opt/demo/1.sh
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「账号与权限闭环」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)
