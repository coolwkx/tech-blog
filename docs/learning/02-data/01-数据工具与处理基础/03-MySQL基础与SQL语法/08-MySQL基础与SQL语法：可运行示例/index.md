---
article_id: kp-c5d436f031ed7cce
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-4da3eec20eac
learning_sourceId: 4da3eec20eac
learning_order: 7
learning_objective: 理解并验证：-MySQL基础与SQL语法：可运行示例
---

# -MySQL基础与SQL语法：可运行示例

> **学习目标**：能够解释「-MySQL基础与SQL语法：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会启动 MySQL（或用提供的虚拟机）、能用 DataGrip 或命令行连上数据库；理解"表 = 行 + 列"。
>
> **所属主题**：-MySQL基础与SQL语法 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-MySQL基础与SQL语法：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)
