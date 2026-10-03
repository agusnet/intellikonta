/*
* Modelo de base de datos del sistema de Akoo Max v1.1
* @author evilnapsis
* @url http://evilnapsis.com/product/akoo-max
*/
create database akoomax;
use akoomax;

create table user(
	id int not null auto_increment primary key,
	name varchar(50) not null,
	lastname varchar(50) not null,
	username varchar(50),
	email varchar(255) not null,
	password varchar(60) not null,
	image varchar(255),
	status int not null default 1,/*0. inactive, 1. active*/
	kind int not null default 1,/*1. admin 2. almacenista 3. vendedor 4. gerente*/
	created_at datetime not null
);

insert into user(name,lastname,email,password,status,kind,created_at) value ("Administrador", "","admin","90b9aa7e25f80cf4f64e990b78a9fc5ebd6cecad",1,1,NOW());

create table tax(
	id int not null auto_increment primary key,
	name varchar(50) not null,
	description text not null,
	kind int, /* 1. category, 2. pay method */
	created_at datetime not null
);
/* categorias iniciales*/
insert into tax(name,kind,created_at) value ("Casa",1,NOW());
insert into tax(name,kind,created_at) value ("Comida",1,NOW());
insert into tax(name,kind,created_at) value ("Transporte",1,NOW());
/* metodos de pago iniciales*/
insert into tax(name,kind,created_at) value ("Efectivo",2,NOW());
insert into tax(name,kind,created_at) value ("Deposito bancario",2,NOW());
insert into tax(name,kind,created_at) value ("Cheque",2,NOW());
insert into tax(name,kind,created_at) value ("Paypal",2,NOW());
insert into tax(name,kind,created_at) value ("Western Union",2,NOW());

create table person(
	id int not null auto_increment primary key,
	image varchar(255) not null,
	no varchar(255) not null,
	name varchar(255) not null,
	lastname varchar(50) not null,
	company varchar(50) not null,
	address1 varchar(50) not null,
	address2 varchar(50) not null,
	phone1 varchar(50) not null,
	phone2 varchar(50) not null,
	email1 varchar(50) not null,
	email2 varchar(50) not null,
	created_at datetime not null
);

create table account(
	id int not null auto_increment primary key,
	name varchar(50) not null,
	description text not null,
	balance float,
	created_at datetime not null
);

insert into account(name,created_at) value ("Mi cartera",NOW());
insert into account(name,created_at) value ("Bancomer",NOW());
insert into account(name,created_at) value ("Banco Azteca",NOW());


create table operation (
	id int not null auto_increment primary key,
	concept varchar(255),
	description text,
	amount float,
	date_at date,
	kind int,/*1. in, 2. out*/
	category_id int ,
	person_id int,
	employee_id int,
	paymethod_id int not null,
	account_id int not null,
	created_at datetime,
	foreign key (account_id) references account(id),
	foreign key (person_id) references person(id),
	foreign key (employee_id) references user(id),
	foreign key (category_id) references tax(id),
	foreign key (paymethod_id) references tax(id)
);


create table message(
	id int not null auto_increment primary key,
	code varchar(255),
	message varchar(255),
	user_from int not null,
	user_to int not null,
	is_read boolean not null default 0,
	created_at datetime
);

/*
configuration kind
1.- Boolean
2.- Text
3.- Number
*/
create table configuration(
	id int not null auto_increment primary key,
	short varchar(255) not null unique,
	name varchar(255) not null unique,
	kind int not null,
	val varchar(255) not null
);
insert into configuration(short,name,kind,val) value("company_name","Nombre de la empresa",2,"AKOO MAX 1.1");
