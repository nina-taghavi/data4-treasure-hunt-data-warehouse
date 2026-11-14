SELECT count(*) FROM public.treasure_log; -- 1789438
-- Only add a new record in treasure_log table for testing incremental fact loading
INSERT INTO public.treasure_log (id, description, log_time, log_type, session_start, hunter_id, treasure_id) 
VALUES (
    E'\\x99ADE08F8ECC43B69FFFF974DA2EF8E9', 
    'Incremental test record', 
    '2022-07-02 10:00:00.000000',
    2, 
    '2022-07-02 09:30:00.000000',
    E'\\x00001cbfa8e546c1baa621de39f4e2d4', 
    E'\\x00003e2cb14041b197f00033c097e070'
);

-- i update the log_time and session_start to be sure that these dates have already existed in the dim_date
UPDATE public.treasure_log
SET
    log_time = '2023-09-12 10:00:00.000000',
    session_start = '2023-09-12 09:30:00.000000'
WHERE id = E'\\x99ADE08F8ECC43B69FFFF974DA2EF8E9';

select * from public.treasure_log
where id = E'\\x99ADE08F8ECC43B69FFFF974DA2EF8E9';

SELECT count(*) FROM public.treasure_log; -- 1789439
