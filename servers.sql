BEGIN;

INSERT INTO servers 
    (host, port, login, password, sni, pbk, sid, inbound_id)
VALUES (
    '127.0.0.1',
    2053,
    'admin',
    'admin',
    'www.google.com',
    'QI8sqtscSTUqJQtrDmrhuULkpBPTlcJ8Gg3wqG6rdQs',
    'aa560e160f',
    4
);

COMMIT;