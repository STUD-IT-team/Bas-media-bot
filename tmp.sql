-- Active: 1741937199469@@127.0.0.1@5433@bas


SELECT tg_admin.id, chat_id 
FROM tg_admin 
JOIN tg_user ON tg_user.id = tg_admin.tg_user_id 
WHERE chat_id = 1;


select * from tg_user

select * from  activist

update activist
set acname = 'a', valid = FALSE
where id = '534d1a79-dfe6-4780-a7d7-f7b8e75b17dd'

select tu.id, ac.id, tu.chat_id, tu.tg_username, ac.acname, ac.valid, tu.agreed
from tg_user tu join activist ac 
on tu.id = ac.tg_user_id


select ac.id, ac.chat_id, ac.acname, ac.valid
from tg_user tu join activist ac 
on tu.id = ac.tg_user_id
where tu.tg_username = 'X' and ac.valid = true

select tu.id, ac.id, tu.chat_id, tu.tg_username, ac.acname, ac.valid, tu.agreed
from tg_user tu join activist ac 
on tu.id = ac.tg_user_id
where tu.tg_username = 'r' and ac.valid = true

insert into activist (id, tg_user_id, acname, valid)
values (gen_random_uuid(), '846cb09a-aaea-4ec9-9152-9fddf68d0236', 'T', True)

select id, chat_id from tg_user LIMIT 1

insert into tg_admin (id, tg_user_id)
values (gen_random_uuid(), (select id from tg_user where tg_username = 'Purummm'))

insert into activist (id, tg_user_id, acname, valid)
values (gen_random_uuid(), (select id from tg_user where tg_username = 'Purummm'), 'Kate', True)


insert into tg_user (id, chat_id, tg_username, agreed)
values (gen_random_uuid(), 1, 'X', True)

insert into tg_user (id, chat_id, tg_username, agreed)
values (gen_random_uuid(), 2, 'Y', True)

insert into tg_user (id, chat_id, tg_username, agreed)
values (gen_random_uuid(), 3, 'Z', True)

insert into tg_user (id, chat_id, tg_username, agreed)
values (gen_random_uuid(), 4, 'F', True)

select id, chat_id, tg_username, agreed
from tg_user join (
    select tg_user_id
    from activist
    where tg_user_id = '1a86f375-cc02-439b-9fea-7e10927e25dd'
) a on tg_user.id = a.tg_user_id


select activist.id, chat_id, acname, valid
from activist join tg_user
on tg_user.id = activist.tg_user_id
where tg_user_id = '1a86f375-cc02-439b-9fea-7e10927e25dd'



SELECT id, chat_id, tg_username, agreed FROM tg_user WHERE tg_username = 'r'

SELECT activist.id, chat_id, acname, valid 
FROM activist JOIN tg_user 
ON tg_user.id = activist.tg_user_id 
WHERE valid = true;