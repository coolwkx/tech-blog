---
article_id: "f122af99c7af"
learning_kind: "reference"
learning_category: "02-data"
---

# -MySQL进阶-索引与优化


> **一句话总结**：多表查询的精髓只有一句话——**先按关联条件和组合方式把多张表拼成一张表，再在这张表上做单表查询**；"进阶"真正解决三类难题：表与表怎么拼（JOIN / 子查询 / 自关联）、组内怎么排名取 TopN（window function）、复杂语句怎么写对写好（CTE、`case when`、把条件下推到 `where`）。
> **前置知识**：[03-MySQL基础与SQL语法](03-MySQL基础与SQL语法.md) 的 `select` 七段式、聚合函数、`group by`/`having`、主键与外键约束。
> **学完能做到**：1. 按业务关系设计一对多/多对多/一对一建表方案并正确使用外键；2. 写出内连接、外连接、子查询、自关联查询并说清各自结果集；3. 用窗口函数完成分组排名与分组 TopN，并用 CTE 把复杂查询拆成可读步骤。

## 1. 核心概念

### 1.1 表关系与建表原则

| 关系 | 业务举例 | 建表原则 |
| --- | --- | --- |
| 一对多 | 部门—员工、客户—订单、分类—商品 | 在**多的一方**加 1 列作外键，关联"1"的一方的主键 |
| 多对多 | 学生—选修课、订单—商品 | 新建**中间表**，至少 3 列（自身主键 + 两个外键列） |
| 一对一 | 人—身份证号、公司—注册地址 | 直接合并到一张表 |

外键两条铁律：① **外表的外键列不能出现主表主键列里没有的值**；② 外键与主键一样，本质是保证数据的完整性与安全性。

```sql
-- 建表时加外键
create table emp(id int primary key auto_increment, name varchar(10), salary int, dept_id int,
 foreign key(dept_id) references dept(id));
-- 建表后加外键（可自定义约束名）
alter table emp add constraint fk_01 foreign key(dept_id) references dept(id);
-- 删除外键：删的是"约束名"而不是列名，先用 show create table emp; 查真实名字
alter table emp drop foreign key fk_01;
```

### 1.2 连接查询类型对照

| 类型 | 写法 | 结果集 | 说明 |
| --- | --- | --- | --- |
| 交叉查询 | `from 表A, 表B` | A 条数 × B 条数 | 笛卡尔积，**一般不用** |
| 显式内连接 | `from A inner join B on 关联条件` | 两表**交集** | `inner` 可省略；推荐显式写法 |
| 隐式内连接 | `from A, B where 关联条件` | 交集 | 老写法，条件混在 where 里可读性差 |
| 左外连接 | `from A left [outer] join B on 条件` | **左表全集** + 交集 | 右表没匹配上为 null；**推荐掌握这一种** |
| 右外连接 | `from A right [outer] join B on 条件` | **右表全集** + 交集 | 交换表序后与左外连接等价 |

> `A left join B` ≡ `B right join A`。日常统一用**左外连接**，把"必须保全数据的主表"放左边，思路最清楚。

### 1.3 子查询与自关联

| 概念 | 说明 |
| --- | --- |
| 子查询 | 一个查询的**条件**依赖另一个查询的**结果**；里层叫子查询，外层叫父查询（主查询） |
| 使用位置 | 可出现在 `where` 中（最常见），也可作为"套表"出现在 `from` 中 |
| 自关联 | **同一张表自己和自己关联**；典型是树形/层级数据（省—市—区） |

自关联的经典设计——用**一张表**存省市区，靠 `pid` 指向父级，避免建三张表：

| id | title | pid |
| --- | --- | --- |
| 410000 | 河南省 | 0 |
| 410100 | 郑州市 | 410000 |
| 410700 | 新乡市 | 410000 |
| 410101 | 二七区 | 410100 |
| 410721 | 新乡县 | 410700 |

### 1.4 窗口函数（window function，MySQL 8.x 新增）

用于对**局部范围（窗口）**内的数据做操作，**不改变行数**——"给表新增 1 列"。

```sql
函数 over(partition by 分组字段 order by 排序字段)
```

| 类别 | 函数 | 说明 |
| --- | --- | --- |
| 排序类 | `row_number` | 纯行号，与数值无关，从 1 连续递增 |
| 排序类 | `rank` | 稀疏排名，并列同名次但**跳号** |
| 排序类 | `dense_rank` | 密集排名，并列同名次且**不跳号** |
| 排序类 | `ntile(n)` | 组内平均分 n 桶，常用于数据抽样 |
| 聚合类 | `count/sum/avg/max/min` | 配 `over` 得"组内总计"，可再算占比 |
| 其他类 | `lag(字段,n)` / `lead(字段,n)` | 取组内当前行的前 n / 后 n 行 |
| 其他类 | `first_value` / `last_value` | 组内第一行 / 最后一行 |

数据 `100, 90, 90, 60` 三个排名函数的差异：

| 数据 | `row_number` | `rank` | `dense_rank` |
| --- | --- | --- | --- |
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 60 | 4 | 4 | 3 |

两条最容易踩的规则：`over` 里**不写** `partition by` → 统计**全表**，写了 → 统计**组内**；**不写** `order by` → 统计**组内所有行**，写了 → 统计**组内第一行到当前行**（累计语义）。

### 1.5 CTE 与 `case when`

```sql
with 临时表名1 as (查询语句),
 临时表名2 as (查询语句)
select * from 临时表名1 ...;
```

CTE 把查询结果临时封装成一张表再查询，与"套表"（子查询写在 `from` 里）作用相同，但可读性更好且能链式定义多张临时表。`case when` 相当于 Python 的 `if`：

```sql
case when deptid=10 then '蜀国' when deptid=20 then '魏国' else '灭国' end as dept_name
-- 语法糖：同 1 字段且都是"等于"判断时可简写
case deptid when 10 then '蜀国' when 20 then '魏国' else '灭国' end as dept_name
```

## 2. 可运行示例

```sql
-- ========== 0. 建库 ==========
drop database if exists day02;
create database day02 charset 'utf8';
use day02;

-- ========== 1. 一对多：部门 — 员工 ==========
create table dept(id int primary key auto_increment, name varchar(10));
create table emp(
 id int primary key auto_increment, name varchar(10), salary int, dept_id int,
 foreign key(dept_id) references dept(id)
);
insert into dept values(null,'人事部'),(null,'研发部'),(null,'财务部');
insert into emp values
 (null,'乔峰',30000,1),(null,'虚竹',20000,2),(null,'段誉',3000,3),
 (null,'王语嫣',25000,2),(null,'阿朱',25000,2);
-- insert into emp values(null,'喜哥',66666,10); -- 报错：外键拦住脏数据

-- 每个部门的名称、人数、平均工资（用 left join 保住没有员工的部门）
select d.name as dept_name, count(e.id) as emp_cnt, round(avg(e.salary),2) as avg_salary
from dept d left join emp e on d.id = e.dept_id
group by d.name order by avg_salary desc;

-- ========== 2. 多表连接 ==========
create table hero(hid int primary key auto_increment, hname varchar(255), kongfu_id int);
create table kongfu(kid int primary key auto_increment, kname varchar(255));
insert into hero values (1,'鸠摩智',9),(3,'乔峰',1),(4,'虚竹',4),(5,'段誉',12);
insert into kongfu values (1,'降龙十八掌'),(2,'乾坤大挪移'),(3,'猴子偷桃'),(4,'天山折梅手');

select * from hero, kongfu; -- 交叉查询：4×4=16 行，不用
select * from hero h inner join kongfu k on h.kongfu_id = k.kid; -- 显式内连接
select * from hero h join kongfu k on kongfu_id = kid; -- inner 与表名前缀可省
select * from hero h, kongfu k where h.kongfu_id = k.kid; -- 隐式内连接
select * from hero h left join kongfu k on h.kongfu_id = k.kid; -- 左外：hero 全集
select * from hero h right join kongfu k on h.kongfu_id = k.kid; -- 右外：kongfu 全集
-- 等价性验证
select * from kongfu left join hero on kongfu_id = kid;
select * from hero right join kongfu on kongfu_id = kid;

-- ========== 3. 子查询 ==========
create table product(pid int primary key auto_increment, pname varchar(20),
 price double, category_id varchar(32));
insert into product(pid,pname,price,category_id) values
 (null,'联想',5000,'c001'),(null,'海尔',3000,'c001'),(null,'雷神',5000,'c001'),
 (null,'杰克琼斯',800,'c002'),(null,'真维斯',200,null),(null,'花花公子',440,'c002'),
 (null,'劲霸',2000,'c002'),(null,'香奈儿',800,'c003'),(null,'相宜本草',200,null),
 (null,'面霸',5,'c003'),(null,'好想你枣',56,'c004'),(null,'香飘飘奶茶',1,'c005'),
 (null,'海澜之家',1,'c002');

-- 需求：查询单价高于均价的商品（子查询一步完成）
select * from product where price > (select round(avg(price),3) from product);

-- ========== 4. 自关联：省市区 ==========
create table areas(id varchar(20) primary key, title varchar(50), pid varchar(20));
insert into areas values
 ('410000','河南省','0'),
 ('410100','郑州市','410000'),('410200','开封市','410000'),('410700','新乡市','410000'),
 ('410101','二七区','410100'),('410102','经开区','410100'),
 ('410701','红旗区','410700'),('410702','卫滨区','410700'),('410721','新乡县','410700');

select * from areas where pid = 410000; -- 河南省所有的市
select * from areas where pid = 410700; -- 新乡市所有的县区

-- 河南省所有"市 + 县区"：三层自关联 county -> city -> province
select province.title as province, city.title as city, county.title as county
from areas as county
join areas as city on county.pid = city.id
join areas as province on city.pid = province.id
where province.title = '河南省'
order by city.id, county.id;

-- 按身份证前 6 位反查家乡（同一条 SQL，只换 where）
select province.title, city.title, county.title
from areas as county
join areas as city on county.pid = city.id
join areas as province on city.pid = province.id
where county.id = '142222';

-- ========== 5. 窗口函数：分组排名与 TopN ==========
create table employee(id int, ename varchar(20), deptid int, salary decimal(10,2));
insert into employee values
 (1,'刘备',10,5500.00),(2,'赵云',10,4500.00),(3,'张飞',10,3500.00),(4,'关羽',10,4500.00),
 (5,'曹操',20,1900.00),(6,'许褚',20,4800.00),(7,'张辽',20,6500.00),(8,'徐晃',20,14500.00),
 (9,'孙权',30,44500.00),(10,'周瑜',30,6500.00),(11,'陆逊',30,7500.00);

-- 5.1 分组排名
select *,
 row_number over(partition by deptid order by salary desc) as rn,
 rank over(partition by deptid order by salary desc) as rk,
 dense_rank over(partition by deptid order by salary desc) as dr
from employee;

-- 5.2 分组 TopN：每组工资最高的 2 人
-- 错误示范：where 不能引用 select 里新建的别名
-- select *, rank over(partition by deptid order by salary desc) as rk from employee where rk<=2;
-- 方案一：套表
select * from (
 select *, rank over(partition by deptid order by salary desc) as rk from employee
) t1 where rk <= 2;
-- 方案二：CTE（推荐，可读性最好）
with t1 as (select *, rank over(partition by deptid order by salary desc) as rk from employee)
select * from t1 where rk <= 2;
-- CTE 链式定义多张临时表
with t1 as (select *, rank over(partition by deptid order by salary desc) as rk from employee),
 t2 as (select * from t1 where rk <= 2)
select * from t2;

-- 5.3 窗口函数 + 聚合：算部门与全公司工资占比
with t1 as (
 select *, sum(salary) over(partition by deptid) as dept_salary,
 sum(salary) over as total_salary
 from employee
)
select *, round(salary/dept_salary,2) as dept_ratio, round(salary/total_salary,2) as total_ratio
from t1;

-- 5.4 聚合函数 + over：组内总计 vs 累计
select *, sum(salary) over(partition by deptid) as dept_total from employee;
select *, max(salary) over(partition by deptid) as dept_max from employee;
-- 加了 order by 变成"从组内第一行到当前行"的累计语义
select *, sum(salary) over(partition by deptid order by salary) as running_total from employee;

-- 5.5 ntile 分桶（数据抽样）；lag 取组内前 2 行
select *, ntile(3) over(partition by deptid) as nt from employee;
select *, lag(salary, 2) over(partition by deptid order by salary) as lag_salary from employee;

-- ========== 6. case when 与常用函数 ==========
select *, case
 when deptid = 10 then '蜀国'
 when deptid = 20 then '魏国'
 when deptid = 30 then '吴国'
 else '灭国' end as dept_name
from employee;
select *, case deptid when 10 then '蜀国' when 20 then '魏国' when 30 then '吴国'
 else '灭国' end as dept_name
from employee;
select datediff('2024-12-25','2024-12-18') as diff_days; -- 7
select round(1346.3846153846155, 3) as r3; -- 1346.385
```

### 延伸补充（本主题展开）

> 只在 `limit 起始索引` 和练习题注释里出现过"索引/优化"字样，**并未系统讲解索引原理**。以下仅作进阶入门。

```sql
show index from emp; -- 查看索引
create index idx_emp_deptid on emp(dept_id); -- 普通索引
create unique index uk_emp_name on emp(name); -- 唯一索引
create index idx_emp_dept_salary on emp(dept_id, salary);-- 复合索引
explain select * from emp where dept_id = 2; -- 执行计划
```

| 概念 | 说明 |
| --- | --- |
| 索引本质 | 排好序的辅助结构（InnoDB 用 **B+ 树**），用空间换查询时间 |
| 聚簇索引 | InnoDB **主键索引即聚簇索引**，叶子节点直接存整行数据，所以主键要短、要自增 |
| 二级索引 | 叶子节点存主键值，查非索引列需**回表** |
| 最左前缀 | 复合索引 `(dept_id, salary)` 可用于 `where dept_id=?` 或两者同时，但**单独 `where salary=?` 用不上** |
| `explain` 关键列 | `type`（`ref` 优于 `index` 优于 `ALL`）、`key`、`rows`、`Extra` |
| 索引失效常见写法 | 索引列上做运算或套函数、前导 `%` 的 `like '%香'`、隐式类型转换、`or` 连接非索引列 |

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| 忘记写关联条件 | 结果行数暴涨 | `from A, B` 是笛卡尔积，A×B 行 | 内连接必须写 `on`/`where` 关联条件，并核对行数是否合理 |
| 把内连接当外连接用 | 主表里"没有下级"的行消失 | 内连接只保留两边都匹配的行 | 要保留全集就用 `left join`，主表放左边 |
| `over` 漏写 `partition by` | 变成全表排名 | 不写分区即统计全表 | 分组排名必须写 `partition by 分组字段` |
| 聚合的 `over` 里多写 `order by` | 聚合值变成累计值而非组内总计 | 有 `order by` 时窗口默认"首行到当前行" | 要组内总计就别写 `order by` |
| 自关联时别名混乱 | 不知道字段属于哪一层 | 同表出现多次，列名全部重名 | 每层起有语义的别名（province/city/county）并统一加前缀 |

## 4. 面试问答

### Q1：内连接、左外连接、右外连接的结果集有什么区别？为什么推荐用左外连接？

<details markdown="1"><summary markdown="1">参考答案</summary>

以 `hero`（左）与 `kongfu`（右）通过 `hero.kongfu_id = kongfu.kid` 关联为例：

- **内连接** `inner join`：只保留**两边都匹配**的行（交集）。`鸠摩智`(9)、`段誉`(12) 在 kongfu 里没有对应功夫会被过滤；`猴子偷桃`(3)、`乾坤大挪移`(2) 没有英雄使用也被过滤。
- **左外连接** `left join`：保留**左表全集**。`鸠摩智`、`段誉` 会保留，只是功夫名为 null。
- **右外连接** `right join`：保留**右表全集**，左表匹配不上的列填 null。

等价关系：`A left join B` ≡ `B right join A`（列顺序可能不同）。所以团队统一使用**左外连接**，把"必须保全的主表"放左边，语义最直观，避免两种写法混用带来的理解成本。

</details>

### Q2：`row_number`、`rank`、`dense_rank` 有什么区别？如何取分组 TopN？

<details markdown="1"><summary markdown="1">参考答案</summary>

对数据 `100, 90, 90, 60`：

| 值 | `row_number` | `rank` | `dense_rank` |
| --- | --- | --- | --- |
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 60 | 4 | 4 | 3 |

- `row_number`：纯行号，**不看数值**，永远 1,2,3,4 不重复；
- `rank`：并列同名次但**跳号**（"奥林匹克排名"）；
- `dense_rank`：并列同名次且**不跳号**（"密集排名"）。

取 TopN 的关键是"窗口函数不能直接写在 `where` 里"，必须包一层：

```sql
-- 方案一：套表
select * from (select *, rank over(partition by deptid order by salary desc) as rk from employee) t1
where rk <= 2;
-- 方案二：CTE（推荐）
with t1 as (select *, rank over(partition by deptid order by salary desc) as rk from employee)
select * from t1 where rk <= 2;
```

选哪个函数取决于业务定义：要**严格取 N 个人**用 `row_number`；允许并列（可能超过 N 人）用 `rank`；要名次连续用 `dense_rank`。

</details>

### Q3：为什么 `where` 不能直接引用 `select` 中定义的列别名？怎么解决？

<details markdown="1"><summary markdown="1">参考答案</summary>

因为 SQL 的**逻辑执行顺序**不是书写顺序：

```text
from → where → group by → having → select → order by → limit
```

`where` 在 `select` **之前**执行，别名此时还未创建，所以 `where rk <= 2` 会报 `Unknown column 'rk' in 'where clause'`。同理 `where` 里也不能用聚合函数，因为聚合发生在 `group by` 之后。

三种解决方案：① **套表**（子查询写在 `from` 里，外层再筛）；② **CTE**（`with t1 as (...) select * from t1 where rk<=2`，语义相同但把"计算"和"筛选"分成两步，可读性最好，复杂查询首选）；③ 在 `where` 里把表达式重复抄一遍（不推荐，开销大且易错）。

补充：`having` 与 `order by` **可以**使用 `select` 别名，因为它们都在 `select` 之后执行。

</details>

## 5. 自测题

### 1. 写出"每个部门的名称、人数、平均工资"，要求**没有员工的部门也显示**。

<details markdown="1"><summary markdown="1">参考答案</summary>

```sql
select d.name as dept_name, count(e.id) as emp_cnt, round(avg(e.salary), 2) as avg_salary
from dept d left join emp e on d.id = e.dept_id
group by d.name order by avg_salary desc;
```

三个关键点：① 用 `left join` 且 `dept` 放左边，才能保住没有员工的部门；② 计数用 `count(e.id)` 而**不是** `count(*)`——后者会把"左表有、右表为 null"的那一行也数成 1，得到错误人数 1，`count(e.id)` 跳过 null 得到 0；③ `group by` 后 `select` 只能写分组字段和聚合函数。

</details>

### 2. 写出"每个部门工资最高的 2 名员工"。若希望名次连续不跳号，用哪个窗口函数？

<details markdown="1"><summary markdown="1">参考答案</summary>

```sql
with t1 as (
 select *, dense_rank over(partition by deptid order by salary desc) as dr from employee
)
select * from t1 where dr <= 2;
```

用 `dense_rank` 得到密集排名（并列同名次、名次不跳号），符合"名次连续"的要求。若业务要求严格取 2 个人（并列也只取一个）改用 `row_number`；若允许并列且接受跳号（可能超过 2 人）用 `rank`。必须用 CTE 或套表包一层，因为 `where` 不能引用窗口函数产生的别名。

</details>

### 3. 为什么 `over(partition by deptid)` 与 `over(partition by deptid order by salary)` 的 `sum` 结果不同？

<details markdown="1"><summary markdown="1">参考答案</summary>

- `over(partition by deptid)`：没有 `order by`，窗口范围是**整个分组**，结果是该部门工资总额，同部门每行相同；
- `over(partition by deptid order by salary)`：有 `order by`，窗口范围默认是**组内第一行到当前行**，结果是按工资升序的累计和，同部门内逐行递增。

| `over` 内容 | 统计范围 |
| --- | --- |
| 什么都不写 | 全表 |
| 只有 `partition by` | 组内所有行 |
| `partition by` + `order by` | 组内第一行到当前行（累计） |

若确实要"组内总计"又需要排序，应显式指定帧：`rows between unbounded preceding and unbounded following`。

</details>

## 6. 延伸阅读

- [MySQL 8.0 Reference Manual：JOIN 语法](https://dev.mysql.com/doc/refman/8.0/en/join.html)
- [MySQL 8.0 Reference Manual：Window Functions](https://dev.mysql.com/doc/refman/8.0/en/window-functions.html)
- [MySQL 8.0 Reference Manual：WITH（Common Table Expressions）](https://dev.mysql.com/doc/refman/8.0/en/with.html)
- [MySQL 8.0 Reference Manual：Optimization and Indexes](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
- [MySQL 8.0 Reference Manual：EXPLAIN Output Format](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html)

---

[⬅️ 返回数据处理目录](README.md)
