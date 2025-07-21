-- +goose Up
-- +goose StatementBegin

CREATE TABLE IF NOT EXISTS tg_user (
  id UUID PRIMARY KEY,
  chat_id BIGINT,
  tg_username VARCHAR(127),
  CONSTRAINT tg_user_chat_id_unique UNIQUE (chat_id),
  CONSTRAINT tg_user_chat_id_notnull CHECK (chat_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS tg_admin (
  id UUID PRIMARY KEY,
  tg_user_id UUID,
  CONSTRAINT tg_admin_user_id_notnull CHECK (tg_user_id IS NOT NULL),
  CONSTRAINT tg_admin_user_id FOREIGN KEY (tg_user_id) REFERENCES tg_user (id)
);

CREATE TABLE IF NOT EXISTS activist (
  id UUID PRIMARY KEY,
  tg_user_id UUID,
  acname VARCHAR(127),
  valid BOOLEAN DEFAULT FALSE, -- In case he was deleted
  CONSTRAINT activist_tg_user_id FOREIGN KEY (tg_user_id) REFERENCES tg_user (id),
  CONSTRAINT activist_tg_user_id_notnull CHECK (tg_user_id IS NOT NULL),
  CONSTRAINT acname_notnull CHECK (acname IS NOT NULL),
  CONSTRAINT valid_notnull CHECK (valid IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS event (
  id UUID PRIMARY KEY,
  evname VARCHAR(255),
  evdate TIMESTAMP,
  place TEXT,
  photo_amount INT,
  video_amount INT,
  created_by UUID,
  created_at TIMESTAMP,
  modified_at TIMESTAMP,
  CONSTRAINT evname_notnull CHECK (evname IS NOT NULL),
  CONSTRAINT evname_uniq UNIQUE (evname),
  CONSTRAINT evdate_notnull CHECK (evdate IS NOT NULL),
  CONSTRAINT place_notnull CHECK (place IS NOT NULL),
  CONSTRAINT photo_amount_notnull CHECK (photo_amount IS NOT NULL),
  CONSTRAINT photo_amount_positive CHECK (photo_amount >= 0),
  CONSTRAINT video_amount_notnull CHECK (video_amount IS NOT NULL),
  CONSTRAINT video_amount_positive CHECK (video_amount >= 0),
  CONSTRAINT created_by_notnull CHECK (created_by IS NOT NULL),
  CONSTRAINT created_by_fkey FOREIGN KEY (created_by) REFERENCES tg_admin (id),
  CONSTRAINT created_at_notnull CHECK (created_at IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS event_member (
  id UUID PRIMARY KEY,
  event_id UUID,
  activist_id UUID,
  is_chief BOOLEAN,
  CONSTRAINT event_id_notnull CHECK (event_id IS NOT NULL),
  CONSTRAINT event_id_fkey FOREIGN KEY (event_id) REFERENCES event (id),
  CONSTRAINT activist_id_notnull CHECK (activist_id IS NOT NULL),
  CONSTRAINT activist_id_fkey FOREIGN KEY (activist_id) REFERENCES activist (id),
  CONSTRAINT is_chief_notnull CHECK (is_chief IS NOT NULL)
);

-- To ensure only one chief per event
CREATE UNIQUE INDEX ON event_member (event_id, is_chief)
WHERE
  is_chief = TRUE;


CREATE TABLE IF NOT EXISTS report (
  id UUID PRIMARY KEY,
  event_member_id UUID,
  url TEXT,
  created_at TIMESTAMP,
  CONSTRAINT event_member_id_notnull CHECK (event_member_id IS NOT NULL),
  CONSTRAINT event_member_id_fkey FOREIGN KEY (event_member_id) REFERENCES event_member (id),
  CONSTRAINT url_notnull CHECK (url IS NOT NULL),
  CONSTRAINT created_at_notnull CHECK (created_at IS NOT NULL)
);

CREATE TABLE canceled_event (
  event_id UUID PRIMARY KEY,
  canceled_by UUID,
  canceled_at TIMESTAMP,
  CONSTRAINT canceled_by_notnull CHECK (canceled_by IS NOT NULL),
  CONSTRAINT canceled_at_notnull CHECK (canceled_at IS NOT NULL),
  CONSTRAINT canceled_by_fkey FOREIGN KEY (canceled_by) REFERENCES tg_admin (id)-- activist (id)
);

CREATE TABLE completed_event (
  event_id UUID PRIMARY KEY,
  completed_by UUID,
  completed_at TIMESTAMP,
  CONSTRAINT completed_by_notnull CHECK (completed_by IS NOT NULL),
  CONSTRAINT completed_at_notnull CHECK (completed_at IS NOT NULL),
  CONSTRAINT completed_by_fkey FOREIGN KEY (completed_by) REFERENCES tg_admin (id)
);

CREATE TYPE NOTIF_TYPE AS ENUM ('event_reminder', 'info', 'assignment', 'event_remove');

CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    extra_text TEXT,
    send_time TIMESTAMP,
    type_notif NOTIF_TYPE,
    done BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP, 
    CONSTRAINT send_time_notnull CHECK (send_time IS NOT NULL),
    CONSTRAINT done_notnull CHECK (done IS NOT NULL),
    CONSTRAINT created_at_notnull CHECK (created_at IS NOT NULL)
);

CREATE TABLE notif_event (
    notif_id UUID UNIQUE,
    event_id UUID,
    PRIMARY KEY (notif_id, event_id),
    CONSTRAINT notif_id_notnull CHECK (notif_id IS NOT NULL),
    CONSTRAINT notif_id_fkey FOREIGN KEY (notif_id) REFERENCES notifications (id),
    CONSTRAINT event_id_notnull CHECK (event_id IS NOT NULL),
    CONSTRAINT event_id_fkey FOREIGN KEY (event_id) REFERENCES event (id)
);

CREATE TABLE notif_tguser (
    notif_id UUID,
    tguser_id UUID,
    PRIMARY KEY (tguser_id, notif_id),
    CONSTRAINT notif_id_notnull CHECK (notif_id IS NOT NULL),
    CONSTRAINT notif_id_fkey FOREIGN KEY (notif_id) REFERENCES notifications (id),
    CONSTRAINT tguser_id_notnull CHECK (tguser_id IS NOT NULL),
    CONSTRAINT tguser_id_fkey FOREIGN KEY (tguser_id) REFERENCES tg_user (id)
);
-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
-- +goose StatementEnd