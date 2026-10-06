---
article_id: kp-454344bdc3f34249
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-d512e4a67eb2
learning_sourceId: d512e4a67eb2
learning_order: 1
learning_objective: 理解并验证：命令速查表
---

# 命令速查表

> **学习目标**：能够解释「命令速查表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：建议先掌握 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) 中的 `ls/cd/mkdir/cp/mv/rm/find/grep/管道/重定向/vi`。
>
> **所属主题**：-Linux实用操作 · 核心概念

## 本次只学这一点

**用户与用户组**

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `useradd [-g 组名] 用户名` | 创建用户；不指定组时自动创建同名组作为主组 | `useradd zhangsan` |
| `passwd 用户名` | 设置/修改密码 | `passwd zhangsan` |
| `getent passwd` | 查看所有用户 | — |
| `id 用户名` | 查看某用户的 uid/gid/所属组 | `id zhangsan` |
| `usermod -aG 组名 用户名` | 把用户追加到附加组 | `usermod -aG dev zhangsan` |
| `userdel [-r] 用户名` | 删除用户，`-r` 连同家目录一起删 | `userdel -r zhangsan` |
| `groupadd 组名` | 新增用户组 | `groupadd dev` |
| `groupdel 组名` | 删除用户组 | `groupdel dev` |
| `su 用户名` | 切换用户 | `su zhangsan` |
| `sudo 命令` | 以 root 权限执行单条命令 | `sudo mkdir /opt/x` |

**权限与归属**

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `chmod [-R] u=,g=,o= 路径` | 符号法改权限 | `chmod u=rx,g=w,o=x 1.txt` |
| `chmod [-R] 数字 路径` | 数字法改权限 | `chmod -R 755 aa` |
| `chown [-R] 用户[:组] 路径` | 改属主/属组 | `chown zhangsan 1.txt`、`chown :dev 1.txt`、`chown zhangsan:dev 1.txt` |

**系统、服务与软件**

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `yum [-y] install\|search\|remove 包名` | 包管理（自动解决依赖） | `yum -y install lrzsz` |
| `rpm` | 底层包管理（**不解决依赖**） | 需自行处理依赖 |
| `systemctl start\|stop\|restart\|status\|enable\|disable 服务名` | 服务控制 | `systemctl restart network` |

**网络、端口、进程**

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `ifconfig` | 查看本机 IP | — |
| `hostname` | 查看主机名 | — |
| `hostnamectl set-hostname 新名` | 修改主机名 | 永久生效 |
| `vim /etc/hosts` | 配置域名映射 | `192.168.88.100 mynode1` |
| `ping [-c 次数] 目标` | 测试连通性 | `ping -c 3 www.baidu.com` |
| `wget url` | 联网下载资源 | `wget https://xxx/a.jpg` |
| `curl url` | 发起 HTTP 请求取回响应 | `curl https://www./ >> .txt` |
| `netstat -anp` | 查看端口占用（all network port） | `netstat -anp \| grep 3306` |
| `ps -ef` | 查看所有进程 | `ps -ef \| grep ssh` |
| `kill -9 pid` | 强制结束进程 | `kill -9 12345` |

**环境变量、传输、打包**

| 命令 | 作用 | 示例 |
| --- | --- | --- |
| `env` | 查看全部环境变量 | — |
| `echo $PATH` | 查看 PATH 的值 | — |
| `vim /etc/profile` | 修改 PATH（全局） | 改完 `source /etc/profile` 生效 |
| `变量名=值` / `echo ${变量名}` | 定义、打印变量 | `name=zhangsan`；`echo ${name}` |
| `yum -y install lrzsz` + `rz` / `sz` | 上传 / 下载（需终端支持） | `rz`、`sz 1.txt` |
| `tar -zcvf 包名.tar.gz 目标` | 打包压缩 | `tar -zcvf my.tar.gz *.txt` |
| `tar -zxvf 包名.tar.gz -C 目录` | 解压到指定目录 | `tar -zxvf my.tar.gz -C aa/` |
| `zip -r 包名.zip 目标` / `unzip 包.zip -d 目录` | zip 格式压缩 / 解压 | — |

**快捷键**

| 快捷键 | 作用 |
| --- | --- |
| `Ctrl + C` | 强制停止当前命令 |
| `Ctrl + D` | 退出登录（等价于 `exit`） |
| `history` | 查看历史命令 |
| `!前缀` | 匹配并执行最近一条以该前缀开头的命令 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「命令速查表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/02-Linux实用操作.md)
