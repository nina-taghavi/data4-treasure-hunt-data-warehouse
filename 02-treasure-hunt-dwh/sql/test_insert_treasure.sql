INSERT INTO public.treasure (id, difficulty, terrain, city_city_id, owner_id)
VALUES (
    E'\\x9f2c3d4e5a6b7c8d9e0f1a2b3c4d5e6f',  -- new unique treasure id
    1,                                       -- difficulty
    2,                                       -- terrain
    E'\\x279E9E639EAE4C0FAB9ACFA42C373027', -- city id
    E'\\x1861405461394EAF9186AB14E965D950'  -- owner id
);


INSERT INTO public.treasure (id, difficulty, terrain, city_city_id, owner_id)
VALUES (
    E'\\x9f2c3d4e5a6b7c8d9e0f1a2b3c4d5e6fff',  -- new unique treasure id
    1,                                       -- difficulty
    2,                                       -- terrain
    E'\\x279E9E639EAE4C0FAB9ACFA42C373027', -- city id
    E'\\x1861405461394EAF9186AB14E965D950'  -- owner id
);


INSERT INTO public.treasure (id, difficulty, terrain, city_city_id, owner_id) VALUES (E'\\x0008A9BFBE4B4F22868B2A56E5BDB055', 3, 2, E'\\x59B1A528DDCC4298AE20E3A01CF444C3', E'\\x1CE47F2B5F244CFC9A8D0CD6B6A6E56D');


INSERT INTO public.treasure_log (id, description, log_time, log_type, session_start, hunter_id, treasure_id) VALUES (E'\\xE3ADE08F8ECC43B69FFFF974DA2EF8E2', 'Cupiditate debitis exercitationem id molestias omnis enim culpa doloribus sint quia cum quaerat reiciendis perspiciatis atque iure voluptatem.', '2022-07-01 21:18:45.740000', 2, '2022-07-01 17:52:45.740000', E'\\x18DCB248462C414FB5F555CA331773AC', E'\\xF7B55A1EC5104D4596771B87C2C7F64F');


SELECT count(*)
FROM treasure_log;

INSERT INTO public.treasure_log (id, description, log_time, log_type, session_start, hunter_id, treasure_id) VALUES (E'\\xE3ADE08F8ECC43B69FFFF974DA2EF8E3', 'Cupiditate debitis exercitationem id molestias omnis enim culpa doloribus sint quia cum quaerat reiciendis perspiciatis atque iure voluptatem.', '2022-07-01 21:18:45.740000', 2, '2022-07-01 17:52:45.740000', E'\\x18DCB248462C414FB5F555CA331773AC', E'\\xF7B55A1EC5104D4596771B87C2C7F64F');
