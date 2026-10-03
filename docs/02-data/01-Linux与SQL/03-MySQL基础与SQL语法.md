> **一句话总结**：SQL 是把"我想要什么数据"翻译成数据库能执行的声明式语言；本分三块——**DDL 定结构**（库、表、字段、约束）、**DML 改数据**（增删改）、**DQL 取数据**（`select` 七段式语法），其中 `select ... from ... where ... group by ... having ... order by ... limit` 的执行顺序必须背下来。
> **前置知识**：会启动 MySQL（或用提供的虚拟机）、能用 DataGrip 或命令行连上数据库；理解"表 = 行 + 列"。
> **学完能做到**：1. 独立建库建表，正确选用数据类型并加上主键/非空/唯一/默认约束；2. 熟练写出带条件、排序、聚合、分组、分页的查询；3. 说清 `delete` 与 `truncate`、`where` 与 `having`、`count(*)` 与 `count(列)` 这几组高频面试对比。

## 1. 核心概念

### 1.1 为什么需要数据库

| 存储方式 | 能否持久 | 精细化管理（CURD） | 适用场景 |
| --- | --- | --- | --- |
| 变量 / 列表 / 字典 | 否，程序结束即丢 | 谈不上 | 程序运行期的临时数据 |
| 文件（csv、txt） | 是 | 差，查找更新要自己写逻辑，并发差 | 小规模、离线分析 |
| **数据库** | 是 | 强，有规律组织数据，支持索引、约束、事务、并发 | **实际开发中真正存数据的地方** |

| 分类 | 数据组织方式 | 代表产品 |
| --- | --- | --- |
| 关系型 | 用**数据表**存储，表与表有关系（一对一、一对多、多对多），用 SQL 操作 | MySQL、Oracle、SQL Server、DB2、SQLite |
| 非关系型 | 多为 **Key-Value** 或文档形式 | Redis、HBase、MongoDB（文档型） |

存储引擎：`MyISAM` **不支持事务和约束**；`InnoDB` **支持事务和约束**，是现代默认选择。

### 1.2 SQL 语句基本规则

| 规则 | 说明 |
| --- | --- |
| 大小写 | SQL **不区分大小写**，约定**关键字大写、其他小写** |
| 换行缩进 | 一条语句可写一行或多行，缩进空格只为可读性 |
| 语句结束 | 以分号 `;` 结束 |
| 注释 | `-- 单行`（`--` 后**必须有空格**）、`# 单行`、`/* 多行 */` |

### 1.3 常用数据类型

| 类别 | 类型 | 说明 | 选型建议 |
| --- | --- | --- | --- |
| 数值 | `int` | 整数 | id、数量、年龄 |
| 数值 | `float` / `double` | 浮点数，有精度误差 | 一般统计值 |
| 数值 | `decimal(m,n)` | 定点数，精确 | **金额**必须用这个 |
| 字符串 | `varchar(n)` | 不定长，按实际长度占用 | 姓名、地址、编号（最常用） |
| 字符串 | `char(n)` | 定长，不足补空格 | 长度固定的编码，如性别、MD5 |
| 日期 | `date` / `datetime` | 年月日 / 年月日时分秒 | 生日 / 订单时间 |

### 1.4 约束（constraint）

约束是在数据类型之上对列值的进一步限定，目的是**保证数据的完整性和安全性**。

| 约束 | 关键字 | 特点 |
| --- | --- | --- |
| 主键 | `primary key` | **非空 + 唯一**，一张表只能有一个；常与 `auto_increment` 连用 |
| 自增 | `auto_increment` | 只能用于整型列；每次在**当前最大主键值基础上 +1**；插入写 `null` 交给数据库分配 |
| 非空 | `not null` | 不能为 null，但**可以重复** |
| 唯一 | `unique` | 不能重复，但**可以为空**（多个 null 不冲突） |
| 默认 | `default 值` | 插入时未给该列值则用默认值；类似 Python 缺省参数 |
| 外键 | `foreign key` | 多表约束，外表的外键列不能出现主表主键列里没有的值 |

### 1.5 DDL：库、表、字段

| 对象 | 操作 | 语法 |
| --- | --- | --- |
| 库 | 查看全部 / 创建 | `show databases;` / `create database [if not exists] 库名 charset 'utf8';` |
| 库 | 看码表 / 改码表 | `show create database 库名;` / `alter database 库名 charset 'utf8';` |
| 库 | 删除 / 切换 / 看当前 | `drop database 库名;` / `use 库名;` / `select database;` |
| 表 | 查看全部 / 结构 | `show tables;` / `desc 表名;` |
| 表 | 创建 | `create table [if not exists] 表名(字段 类型 [约束], ...);` |
| 表 | 改表名 / 删除 | `alter table 旧名 rename 新名;`（或 `rename table 旧名 to 新名;`） / `drop table 表名;` |
| 字段 | 新增 | `alter table 表名 add 字段 类型 [约束];` |
| 字段 | 只改类型/约束 | `alter table 表名 modify 字段 新类型 [新约束];` |
| 字段 | 改列名+类型+约束 | `alter table 表名 change 旧字段 新字段 新类型 [新约束];` |
| 字段 | 删除 | `alter table 表名 drop 字段;` |

### 1.6 DML：增、删、改

| 操作 | 语法 | 说明 |
| --- | --- | --- |
| 增 | `insert into 表名(列1,列2) values(值1,值2);` | 列与值的**个数、类型、顺序必须一致** |
| 增 | `insert into 表名 values(值1,...);` | 省略列名 = 全列名，必须给全 |
| 增 | `insert into 表名 values(null, 值2, ...);` | 主键自增列写 `null`，由数据库分配 |
| 增 | `insert into 表名 values(...),(...),(...);` | 一次插入多行 |
| 改 | `update 表名 set 列1=值1 where 条件;` | **不加 where 会改全表** |
| 删 | `delete from 表名 where 条件;` | **不加 where 会删全表** |

| 维度 | `delete from 表名` | `truncate table 表名` |
| --- | --- | --- |
| 语句类别 | DML | DDL |
| 事务回滚 | 可以 | 一般不可以 |
| 删除范围 | 可带 where 删部分，也可删全部 | 只能整表清空 |
| 自增 id | **不重置** | **重置** |
| 本质 | 逐行删除记录 | 摧毁表再重建同结构的空表 |

### 1.7 DQL：单表查询的完整语法（必须背的顺序）

```sql
select [distinct] 列1 as 别名, 列2, ...
from 表名
where 组前筛选
group by 分组字段
having 组后筛选
order by 排序字段 [asc | desc]
limit 起始索引, 数据条数;
```

| 子句 | 作用 | 关键点 |
| --- | --- | --- |
| `select` | 选列、起别名、算表达式 | `as` 可省略；`distinct` 去重 |
| `from` | 指定表 | 表也可起别名 |
| `where` | **组前**筛选 | 分组前过滤行；**不能跟聚合函数** |
| `group by` | 分组 | 查询列**只能出现分组字段和聚合函数** |
| `having` | **组后**筛选 | 分组后过滤组；**可以跟聚合函数** |
| `order by` | 排序 | 默认 `asc` 升序，可多字段排序 |
| `limit` | 分页 | `limit 起始索引, 条数`，索引从 0 开始 |

**条件查询速查**

| 场景 | 写法 | 示例 |
| --- | --- | --- |
| 比较 | `=`, `!=`, `<>`, `>`, `>=`, `<`, `<=` | `where price > 60` |
| 逻辑 | `and`, `or`, `not` | `where price >= 200 and price <= 800` |
| 连续区间 | `between 值1 and 值2` | `where price between 200 and 800`（**包左包右**） |
| 固定值集合 | `in (值1, 值2)` | `where price in (200, 800)` |
| 模糊匹配 | `like`：`_` 任意 1 字符，`%` 任意多字符（可为 0） | `where pname like '香%'`、`like '_想%'` |
| 判空 | `is null` / `is not null` | `where category_id is null` |

**聚合函数**（多进一出）：`count` 统计个数（`count(列)` 只统计**非空值**）、`sum` 求和、`max`/`min` 最大最小、`avg` 平均值（分母是非空值个数）。

**分页参数计算公式**

| 参数 | 公式 |
| --- | --- |
| 数据总条数 | `select count(*) from 表;` |
| 第 n 页的起始索引 | `(n - 1) * 每页条数` |
| 总页数 | `(总条数 + 每页条数 - 1) // 每页条数`（向上取整） |

## 2. 可运行示例

```sql
-- ========== 0. 建库与切库 ==========
drop database if exists day01;
create database day01 charset 'utf8';
use day01;
select database;

-- ========== 1. DDL：建表并演示约束 ==========
drop table if exists stu;
create table stu(
 id int primary key auto_increment, -- 主键 + 自增
 name varchar(10) not null, -- 非空
 tel varchar(11) unique, -- 唯一，可为空
 gender varchar(2) default '男', -- 默认值
 address varchar(10) default '北京'
);
desc stu;
-- 下面前两条会报错，后三条成功
-- insert into stu values(null, null, '111', '男', '上海'); -- 报错：name 不能为空
-- insert into stu values(1, '黄蓉', '111', '女', '深圳'); -- 报错：tel 重复
insert into stu values(null, '乔峰', '111', '男', '上海');
insert into stu values(null, '虚竹', '222', '男', '广州');
insert into stu values(null, '梦姑', '333', '女'); -- 用默认 address
insert into stu(id, name, tel) values(null, '阿朱', '444'); -- 用默认 gender

-- 字段操作
alter table stu add age int not null default 18;
alter table stu modify age int not null default 20; -- 约束要写全，否则会丢
alter table stu change age user_age int not null default 20; -- 改列名
alter table stu drop user_age;

-- ========== 2. DML：改与删 ==========
update stu set name = '杨过', gender = '男' where id = 2; -- 一定要带 where
delete from stu where id = 4;
select * from stu;
-- delete from stu; -- 清空全部，自增 id 不重置
-- truncate table stu; -- 清空全部，自增 id 重置

-- ========== 3. 准备商品表 ==========
drop table if exists product;
create table product(pid int primary key auto_increment, pname varchar(20),
 price double, category_id varchar(32));
insert into product(pid, pname, price, category_id) values
 (null,'联想',5000,'c001'), (null,'海尔',3000,'c001'), (null,'雷神',5000,'c001'),
 (null,'杰克琼斯',800,'c002'), (null,'真维斯',200,null), (null,'花花公子',440,'c002'),
 (null,'劲霸',2000,'c002'), (null,'香奈儿',800,'c003'), (null,'相宜本草',200,null),
 (null,'面霸',5,'c003'), (null,'好想你枣',56,'c004'), (null,'香飘飘奶茶',1,'c005'),
 (null,'海澜之家',1,'c002');

-- ========== 4. 简单查询与别名 ==========
select * from product;
select pname, price from product;
select pname as 商品名, price 商品价格 from product as p; -- as 可省略
select pname, price + 10 as price from product; -- 结果是表达式

-- ========== 5. 条件查询 ==========
select * from product where pname = '花花公子';
select * from product where price != 800; -- 等价 price <> 800
select * from product where price between 200 and 800; -- 包左包右
select * from product where price in (200, 800);
select * from product where price not in (800);
select * from product where pname like '香%'; -- 以"香"开头
select * from product where pname like '_想%'; -- 第二个字是"想"
select * from product where category_id is null; -- 判空：不能用 = null
select * from product where category_id is not null;

-- ========== 6. 排序 ==========
select * from product order by price; -- 默认升序
select * from product order by price asc; -- 效果同上
select * from product order by price desc; -- 降序
select * from product order by price desc, category_id desc; -- 多字段排序

-- ========== 7. 聚合查询 ==========
select count(*) as total_cnt from product; -- 13
select count(category_id) as not_null_cnt from product; -- 11，不含 null
select count(1) as total_cnt2 from product; -- 13
select count(pid) as cnt_gt200 from product where price > 200;
select sum(price) as total_price from product where category_id = 'c001';
select avg(price) as avg_price from product where category_id = 'c002';
select max(price) as max_price, min(price) as min_price from product;

-- ========== 8. 分组查询 ==========
select category_id, count(*) as total_cnt from product group by category_id;

-- 组前筛选用 where，组后筛选用 having
select category_id, count(*) as total_cnt
from product where price > 100 group by category_id having total_cnt > 1;

-- 只分组不聚合 = 按分组字段去重
select category_id from product group by category_id;
select distinct category_id from product; -- 效果同上
select distinct category_id, price from product; -- 两列整体去重
select category_id, price from product group by category_id, price; -- 效果同上

-- ========== 9. 分页查询（5 条/页，共 13 条 -> 3 页） ==========
select * from product limit 5; -- 第 1 页，等价 limit 0, 5
select * from product limit 5, 5; -- 第 2 页
select * from product limit 10, 5; -- 第 3 页

-- ========== 10. 七段式综合演练 ==========
-- 每类商品的单价总和；只看单价 100 以上的商品；只看总价 500 以上的分类；
-- 按总价降序；取前 2 条
select category_id, sum(price) as total_price
from product
where price > 100 -- 组前筛选
group by category_id
having total_price > 500 -- 组后筛选
order by total_price desc
limit 0, 2;
```

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| `update`/`delete` 忘写 `where` | 全表数据被改/被删 | 无条件即匹配所有行 | **先 `select` 验证条件，再换成 update/delete** |
| `where 列 = null` | 不报错但永远查不到数据 | null 表示"未知"，`= null` 结果是 unknown 而非 true | 用 `is null` / `is not null` |
| `where` 里写聚合函数 | 报 `Invalid use of group function` | `where` 在分组**之前**执行 | 改用 `having` |
| 分组查询 select 了非分组列 | `ONLY_FULL_GROUP_BY` 报错或结果不确定 | 一组内该列有多个值 | `select` 只写分组字段 + 聚合函数 |
| `modify` 丢约束 | 原来的 `not null` 消失 | `modify` 是**整体重定义**该列 | 把类型和所有需要的约束一次写全 |
| `count(列)` 结果比 `count(*)` 小 | 数量对不上 | `count(列)` 跳过 null | 统计总行数用 `count(*)` 或 `count(1)` |

## 4. 面试问答

### Q1：`delete from`、`truncate table`、`drop table` 有什么区别？

<details><summary>参考答案</summary>

| 维度 | `delete from` | `truncate table` | `drop table` |
| --- | --- | --- | --- |
| 语句类别 | DML | DDL | DDL |
| 删除对象 | 表中的**数据行**（可带 where 删部分） | 表中的**全部数据行** | **整张表**（结构 + 数据） |
| 事务回滚 | 可以 | 一般不可以 | 不可以 |
| 自增计数器 | 不重置 | 重置 | — |
| 表结构 | 保留 | 保留 | 删除 |
| 速度 | 逐行删除，较慢 | 快（重建空表） | 快 |
| 触发触发器 | 会 | 不会 | 不会 |

记忆要点：`delete` 是"擦掉内容"，`truncate` 是"倒空容器并换一个全新的容器"，`drop` 是"把容器也扔掉"。

</details>

### Q2：`where` 和 `having` 有什么区别？为什么 `where` 后面不能跟聚合函数？

<details><summary>参考答案</summary>

- **执行时机不同**：`where` 在 `group by` **之前**执行，作用对象是**行**；`having` 在 `group by` **之后**执行，作用对象是**分组**。
- **能否用聚合函数**：`where` 不能（此时还没分组，`sum`、`count` 无从算起）；`having` 可以。
- **性能差异**：`where` 先过滤掉不需要的行，参与分组的行更少，通常更快。原则是"**能写在 `where` 里的条件，不要写在 `having` 里**"。

```sql
select category_id, count(*) as cnt
from product
where price > 100 -- 组前筛选：先扔掉便宜的商品
group by category_id
having cnt > 1; -- 组后筛选：再扔掉只有 1 件的分类
```

</details>

### Q3：`count(*)`、`count(1)`、`count(列)` 有什么区别？

<details><summary>参考答案</summary>

**区别一：是否统计 null。** `count(*)` 与 `count(1)` 统计结果集的**行数**（包含 null 行）；`count(列)` 只统计该列**非 null** 的值的个数。例如商品表 13 行、其中 2 行 `category_id` 为 null，则 `count(category_id)` 返回 11。

**区别二：效率。** 面试常背的口诀是"`count(主键列) > count(1) > count(*) > count(普通列)`"，但这个结论**依赖存储引擎与版本**，不要当铁律：

- InnoDB 没有像 MyISAM 那样维护总行数计数器，`count(*)` 也需要遍历（通常走最小的二级索引或主键索引）；
- **MySQL 8.0.14 之后** InnoDB 对 `count(*)` 做了优化，效率与 `count(1)` 基本一致甚至更优；
- `count(列)` 若该列没有可用二级索引，需要回表判断是否为 null，才真的更慢。

**实用结论**：统计总行数统一用 `count(*)`（语义最清晰，优化器也会选最优路径）；只有明确要统计"该列有值的记录数"时才用 `count(列)`。

</details>

## 5. 自测题

### 1. 写出创建"用户表 `users`"的语句：`id` 主键自增、`username` 非空且唯一、`age` 默认 18、`create_time` 为 datetime。

<details><summary>参考答案</summary>

```sql
create table if not exists users(
 id int primary key auto_increment,
 username varchar(20) not null unique,
 age int default 18,
 create_time datetime
);
desc users;
```

要点：`primary key auto_increment` 让 id 非空、唯一、自动增长；`not null unique` 可并列写在同一个列上；`default 18` 只在插入时未给该列值才生效。

</details>

### 2. 商品表 `product` 共 13 行，其中 2 行 `category_id` 为 null。`count(*)`、`count(1)`、`count(category_id)` 的结果分别是多少？

<details><summary>参考答案</summary>

```sql
select count(*) from product; -- 13（所有行）
select count(1) from product; -- 13（所有行）
select count(category_id) from product; -- 11（跳过 2 个 null）
```

规律：`count(*)`/`count(1)` 数**行**，`count(列)` 数**该列的非空值**。

</details>

### 3. 查询"每个分类的商品数量，只显示数量大于 1 的分类，并按数量降序"。

<details><summary>参考答案</summary>

```sql
select category_id, count(*) as total_cnt
from product
group by category_id
having total_cnt > 1
order by total_cnt desc;
```

要点：`group by` 分组 → `having` 过滤分组（因为条件用到聚合结果）→ `order by` 排序。若把 `total_cnt > 1` 写到 `where` 里会直接报错。

</details>

### 4. `product` 表 13 条数据、每页 5 条，写出第 3 页的查询语句并算出总页数。

<details><summary>参考答案</summary>

```sql
-- 第 3 页：起始索引 = (3 - 1) * 5 = 10
select * from product limit 10, 5;
```

</details>

### 5. 为什么 `select * from product where category_id = null;` 查不出"没有分类的商品"？如何修正？

<details><summary>参考答案</summary>

因为 SQL 中的 `null` 表示**未知值**，不是"空字符串"也不是 0。任何与 null 的比较（`= null`、`!= null`、`> null`）结果都是 `unknown`，而 `where` 只保留结果为 `true` 的行，所以永远返回空结果集，且**不报错**——很容易被误认为"本来就没有这样的数据"。

```sql
select * from product where category_id is null; -- 查没有分类的
select * from product where category_id is not null; -- 查有分类的
select * from product where category_id <=> null; -- MySQL 的空值安全等于
```

</details>

## 6. 延伸阅读

- [MySQL 8.0 Reference Manual：SQL Statement Syntax](https://dev.mysql.com/doc/refman/8.0/en/sql-statements.html)
- [MySQL 8.0 Reference Manual：Data Types](https://dev.mysql.com/doc/refman/8.0/en/data-types.html)
- [MySQL 8.0 Reference Manual：CREATE TABLE 与约束](https://dev.mysql.com/doc/refman/8.0/en/create-table.html)
- [MySQL 8.0 Reference Manual：Aggregate Functions](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html)
- [MySQL 8.0 Reference Manual：SELECT 语法](https://dev.mysql.com/doc/refman/8.0/en/select.html)

---

[⬅️ 返回数据处理目录](README.md)
