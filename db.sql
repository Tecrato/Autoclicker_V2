BEGIN TRANSACTION;
DROP TABLE IF EXISTS "perfiles";
CREATE TABLE IF NOT EXISTS "perfiles" (
	"id"	INTEGER UNIQUE,
	"nombre"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "clicks";
CREATE TABLE IF NOT EXISTS "clicks" (
	"id"	INTEGER,
	"id_perfil"	INTEGER NOT NULL,
	"x"	INTEGER NOT NULL,
	"y"	INTEGER NOT NULL,
	"tiempo"	REAL DEFAULT 0,
	"boton"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_perfil") REFERENCES "perfiles"("id") ON DELETE CASCADE
);
COMMIT;