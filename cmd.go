package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"github.com/jackc/pgconn"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/jackc/pgx/v5"
	"github.com/joho/godotenv"
)

const (
	EmojiStart        = "\U000025B6"
	EmojiEnd          = "\U000025C0"
	EmojiBrain        = "\U0001F9E0"
	EmojiEye          = "\U0001F441"
	EmojiManShrugging = "\U0001F937"
	EmojiSpeakingHead = "\U0001F5E3"

	ButtAnswerQuestion  = EmojiEnd + "Ответить на вопрос" + EmojiStart
	ButtAddYourQuestion = EmojiEnd + "Добавить свой вопрос" + EmojiStart
	ButtAnswerCategory1 = EmojiBrain + "Образовательные"
	ButtAnswerCategory2 = EmojiEye + "Психологические"
	ButtAnswerCategory3 = EmojiManShrugging + "Другое"
	ButtPeopleCategory1 = EmojiEnd + "По возрасту" + EmojiStart
	ButtPeopleCategory2 = EmojiEnd + "По курсу" + EmojiStart
	ButtPeopleCategory3 = EmojiEnd + "По полу" + EmojiStart
	ButtPeopleCategory4 = EmojiEnd + "По факультету" + EmojiStart

	ButtCodeAnswerQuestion  = "answerQuestion"
	ButtCodeAddYourQuestion = "addQuestion"
	ButtCodeAnswerCategory1 = "answerCategory1"
	ButtCodeAnswerCategory2 = "answerCategory2"
	ButtCodeAnswerCategory3 = "answerCategory3"
	ButtCodePeopleCategory1 = "peopleCategory1"
	ButtCodePeopleCategory2 = "peopleCategory2"
	ButtCodePeopleCategory3 = "peopleCategory3"
	ButtCodePeopleCategory4 = "peopleCategory4"
	delayDuration           = 2 * time.Second
)

var bot *tgbotapi.BotAPI
var chatId int64

func connectionToTg() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Panic(err)
	}
	TOKEN := os.Getenv("BOT_TOKEN")
	if bot, err = tgbotapi.NewBotAPI(TOKEN); err != nil {
		fmt.Println(fmt.Errorf("сonnection to tg failed: %v", err))
	}
}

func sendMessage(msg string) {
	msgConfig := tgbotapi.NewMessage(chatId, msg)
	bot.Send(msgConfig)
}

func isMessageForMrOnion(update *tgbotapi.Update) bool {
	onionName := [6]string{"лук", "луковица", "мистер лук", "mr лук", "onion", "mr onion"}
	if update.Message == nil || update.Message.Text == "" {
		return false
	}
	msgInLowerCase := strings.ToLower(update.Message.Text)
	for _, name := range onionName {
		if strings.Contains(msgInLowerCase, string(name)) {
			return true
		}
	}
	return false
}

func insertUserDataToDB(age, course int, sex, faculty string) error {
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
        INSERT INTO users (user_age, course, sex, faculty) VALUES ($1, $2, $3, $4);
    `, age, course, sex, faculty)
	if err != nil {
		return err
	}

	return nil
}

func extractName(text string) string {
	index := strings.Index(text, "Меня зовут ")
	if index != -1 {
		name := strings.TrimSpace(text[index+len("Меня зовут "):])
		return name
	}
	return ""
}

func sendGreeting(update *tgbotapi.Update) {
	if update.Message != nil && update.Message.Text != "" {
		if isMessageForMrOnion(update) {
			name := extractName(update.Message.Text)
			greetingMessage := fmt.Sprintf("Привет, %s. Меня зовут Mr Лук.", name)
			sendMessage(greetingMessage)

			sendMessage("Пожалуйста, введите данные в формате: [ваш возраст(число)], [ваш курс(число)], [ваш пол(M/Ж)], [ваш факультет]")
		}
	}
}

type Client interface {
	Exec(ctx context.Context, sql string, arguments ...any) (pgconn.CommandTag, error)
	Query(ctx context.Context, sql string, args ...any) (pgx.Rows, error)
	QueryRow(ctx context.Context, sql string, args ...any) pgx.Row
	Begin(ctx context.Context) (pgx.Tx, error)
}

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

func NewClient(ctx context.Context, maxAttempts int, username, password, host, port, database string) (pool *pgxpool.Pool, err error) {
	dsn := fmt.Sprintf("postgres://%s:%s@%s:%s/%s", username, password, host, port, database)
	err = DoWithTries(func() error {
		ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
		defer cancel()
		pool, err = pgxpool.Connect(ctx, dsn)
		if err != nil {
			return err
		}
		return nil

	}, maxAttempts, 5*time.Second)
	if err != nil {
		log.Fatal("err do with tries postgresql")
	}
	return pool, nil
}

func parseUserInput(input string) (int, int, string, string, error) {
	values := strings.Split(input, ",")

	if len(values) != 4 {
		return 0, 0, "", "", errors.New("Неверный формат ввода. Введите значения в формате: age,course,sex,faculty")
	}

	for i := range values {
		values[i] = strings.TrimSpace(values[i])
	}

	age, err := strconv.Atoi(values[0])
	if err != nil {
		return 0, 0, "", "", err
	}

	course, err := strconv.Atoi(values[1])
	if err != nil {
		return 0, 0, "", "", err
	}

	sex := values[2]
	faculty := values[3]

	return age, course, sex, faculty, nil
}

func getKeyBoardRow(buttText, buttCode string) []tgbotapi.InlineKeyboardButton {
	return tgbotapi.NewInlineKeyboardRow(tgbotapi.NewInlineKeyboardButtonData(buttText, buttCode))
}

func askToAnswerOrAdd() {
	msg := tgbotapi.NewMessage(chatId, "Вы можете ответить на уже существующий вопрос/самому добавить интересующий вопрос и узнать мнение других людей")
	msg.ReplyMarkup = tgbotapi.NewInlineKeyboardMarkup(
		getKeyBoardRow(ButtAnswerQuestion, ButtCodeAnswerQuestion),
		getKeyBoardRow(ButtAddYourQuestion, ButtCodeAddYourQuestion),
	)
	bot.Send(msg)
}

func isCallbackQuery(update *tgbotapi.Update) bool {
	return update.CallbackQuery != nil && update.CallbackQuery.Data != ""
}

func showMenuAnswer(update *tgbotapi.Update) {
	msg := tgbotapi.NewMessage(chatId, "Выбери категорию вопроса:")
	msg.ReplyMarkup = tgbotapi.NewInlineKeyboardMarkup(
		getKeyBoardRow(ButtAnswerCategory1, ButtCodeAnswerCategory1),
		getKeyBoardRow(ButtAnswerCategory2, ButtCodeAnswerCategory2),
		getKeyBoardRow(ButtAnswerCategory3, ButtCodeAnswerCategory3),
	)
	bot.Send(msg)
}

func showMenuAdd(update *tgbotapi.Update) {
	msg := tgbotapi.NewMessage(chatId, "Выбери категорию людей, мнение которых Вас интересует:")
	msg.ReplyMarkup = tgbotapi.NewInlineKeyboardMarkup(
		getKeyBoardRow(ButtPeopleCategory1, ButtCodePeopleCategory1),
		getKeyBoardRow(ButtPeopleCategory2, ButtCodePeopleCategory2),
		getKeyBoardRow(ButtPeopleCategory3, ButtCodePeopleCategory3),
		getKeyBoardRow(ButtPeopleCategory4, ButtCodePeopleCategory4),
	)
	bot.Send(msg)
}

func handleUserAnswer(update *tgbotapi.Update, questionID int) {
	answer := strings.ToLower(update.Message.Text)

	validAnswers := []string{"да", "нет", "не знаю", "какой чил гай скоро январская сессия"}
	validAnswer := false
	for _, ans := range validAnswers {
		if answer == ans {
			validAnswer = true
			break
		}
	}

	if !validAnswer {
		sendMessage("Пожалуйста, выберите один из предложенных вариантов ответа.")
		return
	}

	connConfig, err := pgx.ParseConfig(os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Println("Error parsing database URL:", err)
		return
	}

	conn, err := pgx.ConnectConfig(context.Background(), connConfig)
	if err != nil {
		log.Println("Error connecting to database:", err)
		return
	}
	defer conn.Close(context.Background())

	_, err = conn.Exec(context.Background(), `
	  INSERT INTO completedsurveys (id_revues, answers_on_quest) VALUES ($1, $2);
	`, questionID, answer)
	if err != nil {
		log.Println("Error inserting user answer:", err)
		return
	}

	sendMessage("Спасибо за ваш ответ! Он успешно сохранен.")
}

func handleEducationalQuestion(update *tgbotapi.Update) {
	connConfig, err := pgx.ParseConfig(os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Println("Error parsing database URL:", err)
		return
	}

	conn, err := pgx.ConnectConfig(context.Background(), connConfig)
	if err != nil {
		log.Println("Error connecting to database:", err)
		return
	}
	defer conn.Close(context.Background())

	var questionID int
	var question string
	err = conn.QueryRow(context.Background(), "SELECT id, vopros FROM revues WHERE topic = 'образовательные'").Scan(&questionID, &question)
	if err != nil {
		log.Println("Error querying educational question:", err)
		return
	}

	sendMessage(question)

	for update := range bot.GetUpdatesChan(tgbotapi.NewUpdate(0)) {
		if update.Message != nil && update.Message.Chat.ID == chatId {
			handleUserAnswer(&update, questionID)
			break
		}
	}
}

func updateProcessing(update *tgbotapi.Update) {
	choiceCode := update.CallbackQuery.Data
	log.Printf("[%T] %s", time.Now(), choiceCode)

	switch choiceCode {
	case ButtCodeAnswerCategory1:
		handleEducationalQuestion(update)
	case ButtCodeAnswerQuestion:
		showMenuAnswer(update)
	case ButtCodeAddYourQuestion:
		showMenuAdd(update)
	}
}

func main() {
	connectionToTg()
	log.Printf("Authorized on account %s", bot.Self.UserName)
	updateConfig := tgbotapi.NewUpdate(0)
	for update := range bot.GetUpdatesChan(updateConfig) {
		if isCallbackQuery(&update) {
			updateProcessing(&update)
		} else if update.Message != nil && update.Message.Text == "/start" {
			chatId = update.Message.Chat.ID
			sendMessage("Дарова, братишка. Можешь меня звать \"Лук\", \"Луковица\",\"Мистер Лук\". Как тебя зовут?(Напишите своё имя в формате: Меня зовут [ваше имя])) ")
		} else if isMessageForMrOnion(&update) {
			log.Printf("[%s] %s", update.Message.From.UserName, update.Message.Text)
			sendGreeting(&update)
		} else if update.Message != nil {
			age, course, sex, faculty, err := parseUserInput(update.Message.Text)

			if err != nil {
				log.Println("Error parsing user input:", err)
			} else {
				if age != 0 && course != 0 && sex != "" && faculty != "" {
					err := insertUserDataToDB(age, course, sex, faculty)
					if err != nil {
						log.Println("Error inserting user data to DB:", err)
					} else {
						sendMessage("Данные успешно добавлены в базу данных!")
						askToAnswerOrAdd()
					}
				}
			}
		}
	}
}
