CREATE TABLE establishment (
	id serial PRIMARY KEY,
	name varchar(255),
	address varchar(255)
);

CREATE TABLE service (
	num int PRIMARY KEY,
	name varchar(100) NOT NULL,
	UNIQUE(num,name)
);

CREATE TABLE focus (
	num int PRIMARY KEY,
	name varchar(100) NOT NULL,
	UNIQUE(num,name)
);

CREATE TABLE designation (
	num int PRIMARY KEY,
	name varchar(100) UNIQUE NOT NULL,
	UNIQUE(num,name)
);

CREATE TABLE expertise (
	num int PRIMARY KEY,
	name varchar(100) UNIQUE NOT NULL
);

CREATE TABLE specialContract (
	num int PRIMARY KEY,
	name varchar(100) UNIQUE NOT NULL,
	UNIQUE(num,name)

);

CREATE TABLE doctor (
	id serial PRIMARY KEY,
	name varchar(255),
	establishment_id integer REFERENCES establishment(id),
	field varchar(100),
	address varchar(255),
	telephone varchar(16),
	url varchar(512)
);

CREATE TABLE doctor_service (
	doctor_id integer REFERENCES doctor(id),
	service_num integer REFERENCES service(num),
	UNIQUE (doctor_id, service_num)
);

CREATE TABLE doctor_focus (
	doctor_id integer REFERENCES doctor(id),
	focus_num integer REFERENCES focus(num),
	UNIQUE (doctor_id, focus_num)
);

CREATE TABLE doctor_designation (
	doctor_id integer REFERENCES doctor(id),
	designation_num integer REFERENCES designation(num),
	UNIQUE (doctor_id, designation_num)
);

CREATE TABLE doctor_contract (
	doctor_id integer REFERENCES doctor(id),
	contract_num integer REFERENCES specialContract(num),
	UNIQUE (doctor_id, contract_num)
);

CREATE TABLE doctor_time (
	id serial PRIMARY KEY,
	doctor_id integer REFERENCES doctor(id) NOT NULL,
	day varchar(10),
	start_at time NOT NULL,
	end_at time NOT NULL,
	description varchar(50),
	UNIQUE (doctor_id, day, start_at, end_at, description)
);

CREATE TABLE doctor_expertise (
	doctor_id integer REFERENCES doctor(id),
	expertise_num integer REFERENCES expertise(num),
	UNIQUE(doctor_id,expertise_num)
);
