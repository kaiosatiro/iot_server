-- CREATE TABLE permissions (
--   id SERIAL PRIMARY KEY,
--   permission_name VARCHAR NOT NULL UNIQUE,
--   description VARCHAR,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- );

-- CREATE TABLE roles (
--   id SERIAL PRIMARY KEY,
--   role_name VARCHAR UNIQUE NOT NULL,
--   description VARCHAR,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- );

-- CREATE TABLE role_permissions (
--   role_id INTEGER,
--   permission_id INTEGER,
  
--   PRIMARY KEY (role_id, permission_id),
--   FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
--   FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
-- );
-- CREATE TABLE user_roles (
--   user_id INTEGER,
--   role_id INTEGER,
  
--   PRIMARY KEY (user_id, role_id),
--   FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
--   FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
-- );

-- CREATE TABLE users (
--   id SERIAL PRIMARY KEY,
--   user_name VARCHAR UNIQUE,
--   password_hash VARCHAR NOT NULL,
--   email VARCHAR NOT NULL,
--   role VARCHAR,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- );


-- CREATE TABLE sites (
--   id SERIAL PRIMARY KEY,
--   user_id INTEGER NOT NULL,
--   name VARCHAR NOT NULL,
--   description VARCHAR,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  
--   FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE CASCADE
-- );

-- CREATE TABLE devices (
--   id SERIAL PRIMARY KEY,
--   user_id INTEGER NOT NULL,
--   site_id INTEGER NOT NULL,
--   name VARCHAR NOT NULL,
--   model VARCHAR,
--   description VARCHAR,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

--   FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
--   FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
-- );

-- CREATE TABLE messages (
--   id SERIAL PRIMARY KEY,
--   device_id INTEGER,
--   message JSONB NOT NULL,
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   FOREIGN KEY (device_id) REFERENCES devices(id)
-- );



CREATE TABLE users (
  id SERIAL PRIMARY KEY,
);


CREATE TABLE sites (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  
  FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE CASCADE
);

CREATE TABLE devices (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  site_id INTEGER NOT NULL,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);/home/css/Downloads/Untitled.png

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  device_id INTEGER,

  FOREIGN KEY (device_id) REFERENCES devices(id)
);





-- Table permissions {
--   id integer [primary key]
--   permission_name varchar [not null, unique]
--   description varchar
--   created_at timestamp
--   update_at timestamp
-- }

-- Ref: role_permissions.role_id > roles.id
-- Ref: role_permissions.permission_id > permissions.id

-- Table role_permissions {
--   role_id integer [primary key]
--   permission_id integer [primary key]
-- }

-- Table roles {
--   id integer [primary key]
--   role_name varchar [unique, not null]
--   description varchar
--   created_at timestamp
--   update_at timestamp
-- }

-- Ref: user_roles.user_id > users.id
-- Ref: user_roles.role_id > roles.id

-- Table user_roles {
--   user_id integer [primary key]
--   role_id integer [primary key]
-- }

-- Table users {
--   id integer [primary key]
--   user_name varchar [unique]
--   password_hash varchar [not null]
--   email email [not null]
--   role varchar
--   created_at timestamp
--   update_at timestamp
-- }
-- Ref: sites.user_id > users.id 
-- Ref: devices.user_id > users.id  

-- Table sites {
--   id integer [primary key]
--   user_id integer [not null]  
--   name varchar [not null]
--   description varchar
--   created_at timestamp 
--   update_at timestamp
-- }

-- Ref: sites.id < devices.site_id 

-- Table devices {
--   id integer [primary key]
--   user_id integer [not null]
--   site_id integer [not null]
--   name varchar [not null]
--   type varchar [not null]
--   description varchar 
--   created_at timestamp 
--   update_at timestamp
-- }

-- Table messages {
--   id integer [primary key]
--   device_id integer [primary key]
--   message JsonB [not null]
--   created_at timestamp
-- }

-- Ref: messages.device_id > devices.id

