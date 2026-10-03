> **一句话总结**：Linux 的"实用操作"可以归成四条主线——**身份与权限**（谁能做什么）、**系统与服务**（装什么、跑什么）、**网络与传输**（连得上、传得动）、**打包与脚本**（搬得走、跑得自动），每条主线背后都是"最小权限 + 可复现"这两个工程原则。
> **前置知识**：建议先掌握 [01-Linux基础命令](01-Linux基础命令.md) 中的 `ls/cd/mkdir/cp/mv/rm/find/grep/管道/重定向/vi`。
> **学完能做到**：1. 独立完成"建用户 → 建组 → 授权 → chmod/chown 调权限"的账号闭环；2. 用 yum 装软件、用 systemctl 管服务，并排查服务没起来的问题；3. 用软链接/环境变量/打包/Shell 脚本把重复操作自动化，并用 netstat/ps/kill 定位占用端口与进程。

## 1. 核心概念

### 1.1 用户、用户组与权限模型

Linux 用 **UID/GID** 标识身份，`ls -l` 第一列就是权限位：

```text
-rwxr-xr--. 1 zhangsan dev 1024 1月 13 12:01 1.sh
│└┬┘└┬┘└┬┘ └───┬──┘ └┬┘
│ │ │ │ │ └── 属组 group
│ │ │ │ └──────── 属主 owner
│ │ │ └───────────────── 其他人 other 权限
│ │ └──────────────────── 属组权限
│ └─────────────────────── 属主权限
└───────────────────────── 文件类型：- 普通文件、d 目录、l 软链接
```

`rwx` 对**文件**和**目录**的含义完全不同，这是最容易出错的地方：

| 权限 | 对文件的含义 | 对目录的含义 |
| --- | --- | --- |
| `r` (4) | 可读取文件内容 | 可 `ls` 列出目录内文件名 |
| `w` (2) | 可修改文件内容 | 可在目录内创建/删除/改名文件 |
| `x` (1) | 可作为程序执行 | 可 `cd` 进入该目录、可访问其中文件 |

数字权限就是把 `rwx` 相加：`r=4, w=2, x=1, -=0`，因此 `777` = 所有人可读可写可执行，`644` = 属主读写、其他只读，`755` = 属主全权、其他可读可执行。

### 1.2 命令速查表

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

### 1.3 软链接 vs 硬链接

| 维度 | 软链接（symbolic link） | 硬链接（hard link） |
| --- | --- | --- |
| 创建命令 | `ln -s 源 链接名` | `ln 源 链接名` |
| 类比 | Windows/Mac 的快捷方式 | 同一份数据的第二个名字 |
| `ls -l` 显示 | `lrwxrwxrwx ... ip -> /etc/.../ifcfg-ens33` | 与普通文件无异 |
| 源删除后 | 链接失效（悬空链接） | 数据仍在，另一个名字照常可读 |
| 跨分区 | 可以 | 不可以（inode 不能跨文件系统） |
| 典型用途 | 把深层配置/目录挂到好记的路径下 | 同一文件多入口的动态备份 |

## 2. 可运行示例

### 2.1 账号与权限闭环

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

### 2.2 服务、网络与端口排查

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

### 2.3 软链接、环境变量、打包与 Shell 脚本

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

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| `usermod -G dev zhangsan` 漏掉 `-a` | 用户的附加组被"重置"成只剩 dev，原有组全丢 | `-G` 是覆盖语义，`-a` 才是追加 | 一律写 `usermod -aG dev zhangsan` |
| 目录权限只给 `r` | `ls` 能看到文件名，但 `cd` 进不去 | 目录的进入权限由 `x` 控制，`r` 只让你列名字 | 目录至少给 `rx`，如 `chmod 755 dir` |
| 给文件 `w` 但没给目录 `w` | 能改文件内容，却删不掉/改不了名 | 删除和改名是"目录的权限"，与文件本身无关 | 想删文件要给**所在目录**写权限 |
| 生产环境 `chmod -R 777` | 任何用户都能改写程序文件，易被篡改 | 777 = 所有人可读写执行 | 按最小权限给：脚本 755、配置 644、私钥 600 |
| 软链接源写相对路径 | 链接一移动就失效 | 相对路径以链接所在目录为基准解析 | `ln -s` 的源路径用绝对路径 |
| 改完 `/etc/profile` 不生效 | `echo $PATH` 还是旧值 | 该文件只在登录时读取 | 执行 `source /etc/profile` 或重新登录 |
| `disable` 与 `stop` 混用 | 本次停了，重启后服务又起来了 | `stop` 只停当前运行，`enable/disable` 管开机自启 | 两者按需组合：`stop` + `disable` |
| `kill` 不带 `-9` 没反应 | 进程依然存在 | 默认信号是温和终止，进程可忽略 | 确认 pid 无误后 `kill -9 pid` |
| `tar` 参数顺序写错 | 报 `Cowardly refusing to create an empty archive` | 压缩包名必须紧跟 `-f` | 固定记 `tar -zcvf 包 源`、`tar -zxvf 包 -C 目录` |
| `sh 1.sh` 与 `./1.sh` 效果不同 | 脚本里 `cd`、变量、`exit` 的表现不一致 | `source`/`sh` 与 `./` 的进程与权限要求不同 | 需要影响当前 Shell 用 `source`；独立运行用 `./` 并先 `chmod +x` |

## 4. 面试问答

### Q1：`chmod 755` 和 `chmod 777` 差在哪？为什么生产环境禁用 777？

<details><summary>参考答案</summary>

数字权限是 `r=4, w=2, x=1` 的求和，三位分别对应 **属主 / 属组 / 其他人**。

- `755` = 属主 `rwx`(7)、属组 `r-x`(5)、其他 `r-x`(5)：属主可改，其他人只能读和执行。
- `777` = 三类人全部 `rwx`：任何人都能改写甚至替换该文件。

生产禁用 777 的原因：

1. **安全**：Web 目录若是 777，攻击者上传一个脚本就能覆盖站点程序或植入后门；
2. **数据可靠性**：任意账号误改配置文件都会直接引发故障；
3. **审计困难**：谁改的都可能是"有权限的人"，追责链断裂。

正确做法是按最小权限原则：可执行脚本 `755`、只读配置与数据 `644`、私钥 `600`、需要组内协作的目录 `775` 并配好属组，而不是一律 777。

</details>

### Q2：软链接和硬链接的区别是什么？分别适合什么场景？

<details><summary>参考答案</summary>

| 维度 | 软链接 `ln -s` | 硬链接 `ln` |
| --- | --- | --- |
| 本质 | 一个独立文件，内容是"目标路径" | 指向同一 inode 的另一个目录项 |
| 源删除后 | 失效（悬空） | 数据仍可通过另一个名字访问 |
| 能否跨分区 | 可以 | 不可以 |
| 能否指向目录 | 可以 | 通常不允许 |
| inode | 新 inode | 与源相同 |

场景：

- **软链接**：把深层配置或数据目录挂到好记的路径（如把 `ifcfg-ens33` 链接成 `ip`）、版本切换（`current -> v2.1`）、跨分区引用。注意源路径用**绝对路径**。
- **硬链接**：同一份数据的多个入口，天然同步，用于"动态备份"——改任意一个名字，另一个立刻同步。

</details>

### Q3：服务起不来，你按什么顺序排查？

<details><summary>参考答案</summary>

按"服务本体 → 端口 → 进程 → 日志 → 配置"的顺序，从内到外收窄：

1. `systemctl status 服务名`：看是 `active (running)` 还是 `failed`，失败原因常在最后几行；
2. `netstat -anp | grep 端口`：端口被别的进程占用会直接导致启动失败，比如 3306 被旧实例占着；
3. `ps -ef | grep 进程名`：进程是否存在、启动命令与用户是否正确；
4. 看日志文件（如 `/var/log/` 下的对应日志）定位报错行；
5. 检查配置文件：`/etc` 下对应的 conf 是否有语法错误、路径是否存在、权限是否允许该用户读取；
6. 检查网络类服务：若 IP 异常变成 `127.0.0.1`，按 `stop/disable NetworkManager` → `restart network` → `ifconfig` 的顺序修复；
7. 若是权限导致（例如读不了证书文件），用 `ls -l` 核对属主与权限。

</details>

## 5. 自测题

### 1. 创建用户 zhangsan，让其主组为 dev，并把 `/opt/demo` 目录及其内容的所有者改为 zhangsan、属组改为 dev。

<details><summary>参考答案</summary>

```sh
groupadd dev
useradd -g dev zhangsan
passwd zhangsan
mkdir -p /opt/demo
chown -R zhangsan:dev /opt/demo
ls -l /opt/demo
```

要点：`useradd -g` 指定**主组**（不指定则自动建同名组）；`chown -R 用户:组` 递归改属主与属组。

</details>

### 2. `1.sh` 内容为 `echo hello`，为什么 `sh 1.sh` 能跑，而 `./1.sh` 报 `Permission denied`？

<details><summary>参考答案</summary>

`./1.sh` 是把该文件**当作可执行程序**直接执行，因此需要文件具备**执行权限 `x`**。新建的文件默认权限通常是 `644`（无 `x`），所以报 `Permission denied`。

`sh 1.sh` 是把文件路径作为**参数**传给 `sh` 解释器，真正被执行的是 `sh` 本身（它当然有执行权限），所以对脚本文件的 `x` 位没有要求。

修复：

```sh
chmod +x 1.sh
./1.sh
```

补充：`source 1.sh` 也在**当前 Shell** 里执行（能影响当前环境的变量与目录），而 `sh 1.sh` 和 `./1.sh` 都在子进程中执行，脚本里的 `cd`、变量不会影响当前终端。

</details>

### 3. 写出：把 `/root` 下所有 `.txt` 打包为 `logs.tar.gz`，解压到 `/opt/bak` 目录。

<details><summary>参考答案</summary>

```sh
cd /root
tar -zcvf logs.tar.gz *.txt
mkdir -p /opt/bak
tar -zxvf logs.tar.gz -C /opt/bak
```

参数含义：`-z` gzip 压缩、`-c` 创建归档、`-v` 显示过程、`-f` 指定包名（**必须紧跟包名**）；解压用 `-x`；`-C` 指定解压目标目录。

</details>

### 4. 想查看 3306 端口被哪个进程占用，并强制结束它，写出命令。

<details><summary>参考答案</summary>

```sh
netstat -anp | grep 3306 # 观察最后一列，形如 12345/mysqld
ps -ef | grep mysqld # 进一步确认进程与启动用户
kill -9 12345 # 强制结束（先核对 pid，避免误杀）
netstat -anp | grep 3306 # 复查端口已释放
```

`netstat -anp` 中 `-a` 所有连接、`-n` 以数字显示地址与端口、`-p` 显示占用端口的进程。结合 `grep` 是最常用的"端口排查"组合。

</details>

## 6. 延伸阅读

- [Red Hat Enterprise Linux 文档：管理用户和组](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9)
- [systemd 官方文档（systemctl 与 unit 文件）](https://www.freedesktop.org/software/systemd/man/systemd.html)
- [GNU Tar 官方手册](https://www.gnu.org/software/tar/manual/tar.html)
- [Linux man-pages：chmod(1)、chown(1)、ln(1)](https://www.kernel.org/doc/man-pages/)
- [GNU Bash 手册：Shell 脚本与环境变量](https://www.gnu.org/software/bash/manual/bash.html)

---

[⬅️ 返回数据处理目录](README.md)
