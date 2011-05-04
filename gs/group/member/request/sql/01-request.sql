SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

CREATE TABLE user_group_member_request (
  request_id          TEXT                      PRIMARY KEY,
  user_id             TEXT                      NOT NULL,
  site_id             TEXT                      NOT NULL,
  group_id            TEXT                      NOT NULL,
  request_date        TIMESTAMP WITH TIME ZONE  NOT NULL,
  responding_user_id  TEXT,
  response_date       TIMESTAMP WITH TIME ZONE  NOT NULL,
  accepted            BOOLEAN
);

