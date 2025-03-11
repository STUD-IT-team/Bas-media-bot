-- +goose Up
-- +goose StatementBegin

ALTER TABLE tg_user ADD COLUMN agreed BOOLEAN DEFAULT FALSE;
-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin

ALTER TABLE tg_user DROP COLUMN agreed;
-- +goose StatementEnd