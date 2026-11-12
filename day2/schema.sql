create database logdb;
-- log_file	一次分析一行：文件名、总行数、5xx 数量、分析时间、文件 md5（唯一键）
create table log_file(
    id int primary key auto_increment,
    file_name varchar(255),
    total int,
    count_5xx int,
    analyze_time varchar(255),
    file_md5 varchar(255) unique

)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- log_stat	维度行：外键指向 log_file.id，stat_type 区分 ip／status／qps，stat_key＋stat_value
-- log_stat — 每条统计结果对应一行
-- id、log_file_id（外键 → log_file.id，ON DELETE CASCADE）、
-- stat_type（ip/status/qps）、stat_key、stat_value
create table log_stat(
    id int primary key auto_increment,
    log_file_id int,
    stat_type varchar(255),
    stat_key varchar(255),
    stat_value varchar(255),
    foreign key (log_file_id) references log_file(id) on delete cascade

)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;