-- +goose Up
-- +goose StatementBegin

CREATE TYPE report_type AS ENUM('photo', 'video');

ALTER TABLE report ADD COLUMN report_type report_type DEFAULT 'photo';
ALTER TABLE report ADD CONSTRAINT report_type_notnull CHECK (report_type IS NOT NULL);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

ALTER TABLE report DROP COLUMN report_type;
ALTER TABLE report DROP CONSTRAINT report_type_notnull;

DROP TYPE report_type;

-- +goose StatementEnd