CREATE TABLE establishment (
	id serial PRIMARY KEY
	, name varchar(255)
	, address varchar(255)
);

CREATE TABLE service (
	num int PRIMARY KEY
	, name varchar(256) NOT NULL
);

CREATE TABLE focus (
	num int PRIMARY KEY
	, name varchar(256) NOT NULL
);

CREATE TABLE designation (
	num int PRIMARY KEY
	, name varchar(256) UNIQUE NOT NULL
);

CREATE TABLE expertise (
	num int PRIMARY KEY
	, name varchar(256) UNIQUE NOT NULL
);

CREATE TABLE contract (
	num int PRIMARY KEY
	, name varchar(256) UNIQUE NOT NULL

);

CREATE TABLE doctor (
	id serial PRIMARY KEY
	, name varchar(255)
	, establishment_id integer REFERENCES establishment(id)
	, address varchar(255)
	, telephone varchar(32)
	, url varchar(512)
	, coordinates point
	, UNIQUE (name,address,url)
);

CREATE TABLE doctor_service (
	doctor_id integer REFERENCES doctor(id) NOT NULL
	, service_num integer REFERENCES service(num) NOT NULL
	, UNIQUE (doctor_id, service_num)
);

CREATE TABLE doctor_focus (
	doctor_id integer REFERENCES doctor(id) NOT NULL
	, focus_num integer REFERENCES focus(num) NOT NULL
	, UNIQUE (doctor_id, focus_num)
);

CREATE TABLE doctor_designation (
	doctor_id integer REFERENCES doctor(id) NOT NULL
	, designation_num integer REFERENCES designation(num) NOT NULL
	, UNIQUE (doctor_id, designation_num)
);

CREATE TABLE doctor_contract (
	doctor_id integer REFERENCES doctor(id) NOT NULL
	, contract_num integer REFERENCES contract(num) NOT NULL
	, UNIQUE (doctor_id, contract_num)
);

CREATE TABLE doctor_time (
	doctor_id integer REFERENCES doctor(id) NOT NULL NOT NULL
	, day varchar(10)
	, start_at time NOT NULL
	, end_at time NOT NULL
	, description varchar(50)
	, UNIQUE (doctor_id, day, start_at, end_at, description)
);

CREATE TABLE doctor_expertise (
	doctor_id integer REFERENCES doctor(id) NOT NULL
	, expertise_num integer REFERENCES expertise(num) NOT NULL
	, UNIQUE(doctor_id,expertise_num)
);

