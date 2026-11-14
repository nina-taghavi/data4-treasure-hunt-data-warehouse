-- Update the city for a specific user
SELECT *
FROM city
order by postal_code
limit 5;
-- 07ae7a98-986a-48c0-b6ca-a588df00248c,
-- Palanga

SELECT *
FROM user_table
WHERE id = decode('00001cbfa8e546c1baa621de39f4e2d4', 'hex');
-- 00001cbf-a8e5-46c1-baa6-21de39f4e2d4,
-- Yanis,Andre,Yanis.Andre@girard.com,223,"Allée, Voie du Bac",
-- 3dbb2210-e9d3-4b4f-a9e5-2e13fc709d6c


UPDATE user_table
SET city_city_id = decode('07ae7a98986a48c0b6caa588df00248c', 'hex')  -- Palanga
WHERE id = decode('00001cbfa8e546c1baa621de39f4e2d4', 'hex');
