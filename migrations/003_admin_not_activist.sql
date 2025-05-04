-- +goose Up
-- +goose StatementBegin

ALTER TABLE tg_admin ADD COLUMN adname VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE tg_admin ADD COLUMN valid BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE tg_admin ADD CONSTRAINT tg_admin_user_id_unique UNIQUE (tg_user_id);
ALTER TABLE activist ADD CONSTRAINT activist_tg_user_id_unique UNIQUE (tg_user_id);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin

ALTER TABLE tg_admin DROP COLUMN adname;
ALTER TABLE tg_admin DROP COLUMN valid;

ALTER TABLE tg_admin DROP CONSTRAINT tg_admin_user_id_unique;
ALTER TABLE activist DROP CONSTRAINT activist_tg_user_id_unique;

-- +goose StatementEnd