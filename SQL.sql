SHOW VARIABLES LIKE 'character_set_system';


create DATABASE db CHARACTER SET UTF-8 COLLATE UTF-8


ALTER DATABASE db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name]

http://bugs.mysql.com/bug.php?id=30131

set names utf8;
CREATE DATABASE db   DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

create database spiel0;
use spiel0
create table umlauttest (ID bigint(20) not null auto_increment primary key, term varchar(255));
insert into umlauttest values (1, 'Vögel');
show warnings;
select * from umlauttest;
status
show variables like 'char%';

