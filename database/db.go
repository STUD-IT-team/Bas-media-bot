package database

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/jackc/pgx/v5"
)

func DoWithTries(fn func() error, attemtps int, delay time.Duration) (err error) {
	for attemtps < 0 {
		if err = fn(); err != nil {
			time.Sleep(delay)
			attemtps--
			continue
		}
		return nil
	}
	return
}

func Create() error {
	// Установка параметров подключения к базе данных
	connConfig, err := pgx.ParseConfig(os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatal(err)
	}

	// Установка соединения с базой данных
	conn, err := pgx.ConnectConfig(context.Background(), connConfig)
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close(context.Background())

	// Создание таблицы revues
	_, err = conn.Exec(context.Background(), `
 CREATE TABLE revues (
  id SERIAL PRIMARY KEY,
  vopros INTEGER,
  yes_ans INTEGER,
  male INTEGER,
  female INTEGER,
  all_users INTEGER,
  course1 INTEGER,
  course2 INTEGER,
  course3 INTEGER,
  course4 INTEGER,
  course5 INTEGER,
  course6 INTEGER,
  IBM INTEGER,
  IU INTEGER,
  MT INTEGER,
  SM INTEGER,
  BMT INTEGER,
  RL INTEGER,
  E INTEGER,
  RK INTEGER,
  FN INTEGER,
  L INTEGER,
  SGN INTEGER
 );
 `)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Table 'revues' created successfully")

	// Создание таблицы users
	_, err = conn.Exec(context.Background(), `
 CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  course INTEGER NULL,
  sex VARCHAR(30) NOT NULL,
  faculty VARCHAR(30) NOT NULL
 );
 `)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Table 'users' created successfully")

	// Создание таблицы completedsurveys
	_, err = conn.Exec(context.Background(), `
 CREATE TABLE completedsurveys (
  id SERIAL PRIMARY KEY,
  id_revues INTEGER REFERENCES revues(id),
  id_users INTEGER REFERENCES users(id),
  answers_on_quest VARCHAR(10)
 );
 `)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Table 'completedsurveys' created successfully")
	return nil
}

func InsertUserDataToDB(course int, sex, faculty string) error {
	connConfig, err := pgx.ParseConfig(os.Getenv("DATABASE_URL"))
	if err != nil {
		return err
	}

	conn, err := pgx.ConnectConfig(context.Background(), connConfig)
	if err != nil {
		return err
	}
	defer conn.Close(context.Background())

	_, err = conn.Exec(context.Background(), `
	INSERT INTO users (course, sex, faculty) VALUES ($1, $2, $3);
	`, course, sex, faculty)
	if err != nil {
		return err
	}

	return nil
}
