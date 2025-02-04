-- +goose Up
-- +goose StatementBegin

CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY,
);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
-- +goose StatementEnd
