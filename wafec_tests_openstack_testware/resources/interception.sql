
CREATE TABLE INTERCEPTION (
    id int primary key auto_increment,
    created_at datetime not null,
    name text,
    x text,
    ps text,
    trace text
);

CREATE TABLE INTERCEPTION_VARS (
    id int primary key auto_increment,
    active int default 1
);
