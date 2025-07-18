--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);




CREATE TABLE public.games (
    id integer NOT NULL,
    result character varying,
    status character varying NOT NULL,
    comments character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);



CREATE SEQUENCE public.games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.games_id_seq OWNER TO test_user;

--
--

ALTER SEQUENCE public.games_id_seq OWNED BY public.games.id;



CREATE TABLE public.players (
    id integer NOT NULL,
    fio character varying,
    nickname character varying,
    avatar_path character varying
);


ALTER TABLE public.players OWNER TO test_user;


CREATE TABLE public.players_games (
    player_id integer NOT NULL,
    game_id integer NOT NULL,
    role character varying NOT NULL,
    number integer NOT NULL,
    in_best_move boolean DEFAULT false NOT NULL,
    is_first_killed boolean DEFAULT false NOT NULL
);


ALTER TABLE public.players_games OWNER TO test_user;


CREATE TABLE public.users (
    telegram_id bigint NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying,
    username character varying
);


ALTER TABLE public.users OWNER TO test_user;

--
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO test_user;

--
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.players.id;


--
--

CREATE SEQUENCE public.users_telegram_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_telegram_id_seq OWNER TO test_user;


ALTER SEQUENCE public.users_telegram_id_seq OWNED BY public.users.telegram_id;


--
--

ALTER TABLE ONLY public.games ALTER COLUMN id SET DEFAULT nextval('public.games_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.players ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
--

ALTER TABLE ONLY public.users ALTER COLUMN telegram_id SET DEFAULT nextval('public.users_telegram_id_seq'::regclass);


--
--

COPY public.alembic_version (version_num) FROM stdin;
7e7f6f73932e
\.


--
--

COPY public.games (id, result, status, comments, created_at) FROM stdin;
1	civilians_won	ended		2024-11-16 01:25:00.218999
2	mafia_won	ended		2024-11-16 01:26:45.398117
3	mafia_won	ended		2024-11-16 01:29:57.74338
4	civilians_won	ended		2024-11-16 01:31:05.105505
5	mafia_won	ended		2024-11-16 01:32:09.215113
6	mafia_won	ended		2024-11-16 01:33:23.902796
7	civilians_won	ended		2024-11-16 01:36:23.95905
8	civilians_won	ended		2024-11-16 01:37:43.838156
9	mafia_won	ended		2024-11-18 19:37:33.621902
10	mafia_won	ended		2024-11-18 19:45:23.641645
11	mafia_won	ended		2024-11-25 18:37:38.031519
12	civilians_won	ended		2024-11-25 20:05:24.556659
13	mafia_won	ended		2024-12-05 00:57:12.858511
14	civilians_won	ended		2024-12-05 01:02:25.304167
15	civilians_won	ended		2024-12-05 01:03:32.052293
16	civilians_won	ended		2024-12-09 18:37:28.79627
18	mafia_won	ended		2024-12-09 20:39:50.049068
17	civilians_won	ended		2024-12-09 19:52:17.200878
19	mafia_won	ended		2024-12-16 18:40:08.892024
20	civilians_won	ended		2024-12-16 19:41:15.815474
21	civilians_won	ended		2024-12-16 20:41:32.88208
22	mafia_won	ended		2024-12-23 18:36:54.392134
23	civilians_won	ended		2024-12-23 19:47:08.571274
24	mafia_won	ended		2024-12-23 20:47:27.868861
25	civilians_won	ended		2025-01-13 18:36:29.636519
26	civilians_won	ended		2025-01-13 19:37:58.151569
27	mafia_won	ended		2025-01-20 18:35:43.628519
28	civilians_won	ended		2025-01-20 19:49:25.886049
29	civilians_won	ended		2025-01-27 19:25:00.461717
30	civilians_won	ended		2025-01-27 20:26:22.399464
31	mafia_won	ended		2025-02-10 18:36:59.489187
32	mafia_won	ended		2025-02-10 19:41:51.59159
33	mafia_won	ended		2025-02-10 20:51:52.651523
34	mafia_won	ended		2025-02-24 18:38:56.000626
35	mafia_won	ended		2025-02-24 20:03:33.423024
36	\N	draft		2025-07-11 13:00:57.198032
37	\N	draft		2025-07-11 13:00:57.316316
38	\N	draft		2025-07-11 13:00:57.95083
39	\N	draft		2025-07-11 13:00:58.06529
\.


--
--

COPY public.players (id, fio, nickname, avatar_path) FROM stdin;
34	Саша	Гюнтер	\N
35	Лёша	Штурмовик	\N
36	Дима	Пицца	\N
37	Вова	Ребус	\N
38	Маша	Дежавю	\N
39	Денис	Ковальский	\N
40	Витя	Черный принц	\N
41	Костя	Розовый	\N
42	Саша	Плиза	\N
43	Ксюша	Одиссея	\N
45	Сергей	Козырь	\N
47	Игорь	Борода	\N
48	Александр	Конь	\N
49	Миша	Лао-Ши	\N
46	Саня	2.5	\N
50	Егор	Флойд	\N
51	Ростислав	Манул	\N
52	Антон	Новенький	\N
53	Настя	Виннерка	\N
44	Миша	Эчо	img/avatars/floyd.png
\.


--
--

COPY public.players_games (player_id, game_id, role, number, in_best_move, is_first_killed) FROM stdin;
35	1	civilian	3	f	f
38	1	civilian	4	f	f
44	1	civilian	7	f	f
40	1	don	9	f	f
36	2	civilian	2	f	f
34	2	mafia	3	f	f
41	2	mafia	4	f	f
43	2	civilian	7	f	f
37	2	civilian	9	f	f
42	2	don	10	f	f
43	3	civilian	1	f	f
40	3	mafia	2	f	f
44	3	sheriff	3	f	f
42	3	don	7	f	f
37	3	mafia	8	f	f
41	3	civilian	9	f	f
45	4	mafia	1	f	f
37	4	civilian	2	f	f
44	4	mafia	3	f	f
40	4	civilian	4	f	f
43	4	sheriff	5	f	f
35	4	civilian	6	f	f
42	4	civilian	7	f	f
38	4	civilian	8	f	f
36	4	civilian	9	f	f
34	4	don	10	f	f
44	5	civilian	1	f	f
37	5	civilian	2	f	f
41	5	don	3	f	f
43	5	civilian	4	f	f
38	5	civilian	5	f	f
36	5	civilian	6	f	f
40	5	civilian	7	f	f
45	5	sheriff	8	f	f
34	5	mafia	9	f	f
35	5	mafia	10	f	f
34	6	don	1	f	f
38	6	civilian	2	f	f
40	6	civilian	3	f	f
37	6	civilian	4	f	f
44	6	civilian	5	f	f
43	6	mafia	6	f	f
41	6	civilian	7	f	f
36	6	sheriff	8	f	f
45	6	civilian	9	f	f
35	6	mafia	10	f	f
38	7	civilian	1	f	f
34	7	mafia	3	f	f
39	7	civilian	5	f	f
44	7	civilian	6	f	f
37	7	mafia	8	f	f
43	7	don	9	f	f
47	8	mafia	1	f	f
46	8	civilian	2	f	f
42	8	civilian	3	f	f
36	8	civilian	4	f	f
44	8	sheriff	5	f	f
43	8	civilian	6	f	f
43	9	civilian	1	f	f
48	9	civilian	2	f	f
34	9	civilian	3	f	f
36	9	civilian	4	f	f
42	9	don	5	f	f
44	9	mafia	6	f	f
37	9	mafia	7	f	f
40	9	sheriff	8	f	f
35	9	civilian	9	f	f
34	10	civilian	1	f	f
42	10	civilian	2	f	f
48	10	mafia	3	f	f
37	10	mafia	4	f	f
36	10	civilian	5	f	f
35	10	civilian	6	f	f
40	10	civilian	8	f	f
43	10	don	9	f	f
44	10	sheriff	10	f	f
49	10	civilian	7	f	f
48	11	civilian	1	f	f
49	11	mafia	2	f	f
34	11	civilian	3	f	f
43	11	civilian	4	f	f
42	11	don	5	f	f
37	11	civilian	6	f	f
40	11	civilian	7	f	f
36	11	sheriff	8	f	f
44	11	civilian	9	f	f
35	11	mafia	10	f	f
44	12	mafia	1	f	f
35	12	civilian	2	f	f
36	12	civilian	3	f	f
43	12	civilian	4	f	f
40	12	mafia	5	f	f
49	12	civilian	6	f	f
42	12	don	7	f	f
48	12	civilian	8	f	f
37	12	civilian	9	f	f
34	12	sheriff	10	f	f
49	13	sheriff	1	f	f
42	13	civilian	2	f	f
41	13	don	3	f	f
40	13	civilian	4	f	f
38	13	mafia	5	f	f
48	13	civilian	6	f	f
34	13	civilian	7	f	f
37	13	mafia	8	f	f
44	13	civilian	9	f	f
38	14	civilian	1	f	f
44	14	civilian	2	f	f
48	14	don	3	f	f
41	14	civilian	4	f	f
42	14	mafia	5	f	f
37	14	civilian	6	f	f
40	14	civilian	7	f	f
34	14	sheriff	8	f	f
49	14	mafia	9	f	f
41	15	don	1	f	f
34	15	civilian	2	f	f
48	15	mafia	3	f	f
42	15	sheriff	4	f	f
38	15	civilian	5	f	f
44	15	civilian	6	f	f
49	15	civilian	7	f	f
40	15	mafia	8	f	f
37	15	civilian	9	f	f
49	16	don	1	f	f
44	16	mafia	3	f	f
34	16	sheriff	2	f	f
42	16	civilian	4	f	f
43	16	civilian	5	f	f
46	16	civilian	6	f	f
40	16	civilian	7	f	f
37	16	civilian	8	f	f
35	16	mafia	9	f	f
50	16	civilian	10	f	f
41	17	civilian	1	f	f
42	17	civilian	2	f	f
50	17	don	3	f	f
40	8	civilian	8	t	f
41	7	sheriff	2	t	f
36	7	civilian	7	t	f
35	7	civilian	4	f	t
38	3	civilian	4	t	f
35	3	civilian	5	t	f
36	3	civilian	10	f	t
45	2	civilian	1	t	f
44	2	sheriff	5	t	f
40	2	civilian	6	t	f
41	1	mafia	2	t	f
36	1	civilian	1	t	f
43	1	civilian	6	t	f
34	1	civilian	8	t	f
45	1	mafia	10	t	f
35	2	civilian	8	f	t
44	17	civilian	4	f	f
35	17	mafia	8	f	f
40	17	sheriff	9	f	f
49	17	mafia	5	f	f
35	18	civilian	6	f	f
41	18	sheriff	5	f	f
49	18	civilian	4	f	f
42	18	don	7	f	f
46	18	civilian	10	f	f
37	17	civilian	6	f	f
34	17	civilian	7	f	f
43	17	civilian	10	f	f
43	18	mafia	1	f	f
34	18	civilian	2	f	f
37	18	civilian	3	f	f
44	18	mafia	8	f	f
40	18	civilian	9	f	f
37	19	sheriff	9	f	f
46	19	mafia	1	f	f
34	19	mafia	4	f	f
44	19	don	7	f	f
49	19	civilian	2	f	f
40	19	civilian	3	f	f
47	19	civilian	5	f	f
43	19	civilian	6	f	f
41	19	civilian	8	f	f
35	19	civilian	10	f	f
44	20	don	9	f	f
41	20	mafia	8	f	f
40	20	sheriff	6	f	f
49	20	mafia	7	f	f
37	20	civilian	1	f	f
46	20	civilian	2	f	f
47	20	civilian	3	f	f
35	20	civilian	5	f	f
34	20	civilian	4	f	f
43	20	civilian	10	f	f
47	21	mafia	1	f	f
41	21	mafia	9	f	f
49	21	don	10	f	f
46	21	sheriff	3	f	f
37	21	civilian	2	f	f
43	21	civilian	4	f	f
34	21	civilian	6	f	f
40	21	civilian	5	f	f
44	21	civilian	7	f	f
35	21	civilian	8	f	f
44	22	mafia	2	f	f
34	22	mafia	6	f	f
42	22	civilian	3	f	f
40	22	civilian	4	f	f
36	22	civilian	5	f	f
43	22	civilian	8	f	f
40	23	don	7	f	f
41	23	mafia	2	f	f
42	23	civilian	4	f	f
46	23	civilian	8	f	f
44	23	civilian	5	f	f
37	23	civilian	6	f	f
40	24	mafia	3	f	f
43	24	mafia	6	f	f
36	24	civilian	1	f	f
37	24	civilian	2	f	f
39	24	civilian	5	f	f
46	24	civilian	7	f	f
34	25	mafia	10	f	f
46	25	civilian	1	f	f
37	25	civilian	2	f	f
41	25	civilian	3	f	f
51	25	civilian	6	f	f
40	25	civilian	7	f	f
51	26	mafia	1	f	f
44	26	mafia	4	f	f
37	26	sheriff	2	f	f
34	26	civilian	9	f	f
36	26	civilian	3	f	f
43	26	civilian	6	f	f
40	27	mafia	7	f	f
36	27	sheriff	3	f	f
42	27	civilian	1	f	f
37	27	civilian	5	f	f
35	27	civilian	9	f	f
44	27	civilian	10	f	f
42	28	mafia	2	f	f
51	28	sheriff	3	f	f
37	28	civilian	4	f	f
40	28	civilian	5	f	f
43	28	civilian	8	f	f
34	28	civilian	10	f	f
34	29	don	5	f	f
44	29	mafia	6	f	f
36	29	mafia	7	f	f
40	29	sheriff	10	f	f
48	29	civilian	1	f	f
42	29	civilian	2	f	f
52	29	civilian	3	f	f
35	29	civilian	4	f	f
41	29	civilian	8	f	f
43	29	civilian	9	f	f
43	30	don	3	f	f
34	30	mafia	7	f	f
42	30	mafia	10	f	f
36	30	sheriff	6	f	f
41	30	civilian	1	f	f
35	30	civilian	2	f	f
44	30	civilian	4	f	f
52	30	civilian	5	f	f
48	30	civilian	8	f	f
40	30	civilian	9	f	f
44	31	civilian	2	f	f
42	31	civilian	3	f	f
38	31	mafia	8	f	f
40	31	mafia	6	f	f
53	31	civilian	5	f	f
34	31	don	10	f	f
36	32	civilian	2	f	f
44	32	civilian	5	f	f
35	32	civilian	6	f	f
53	32	civilian	8	f	f
34	32	mafia	9	f	f
38	32	civilian	10	f	f
44	33	civilian	1	f	f
38	33	sheriff	2	f	f
36	33	mafia	5	f	f
35	33	civilian	8	f	f
41	33	don	7	t	f
40	32	sheriff	3	f	t
42	33	civilian	10	t	t
41	32	civilian	7	t	f
42	32	mafia	1	t	f
43	32	don	4	t	f
43	31	civilian	4	t	f
36	31	civilian	7	t	f
35	31	sheriff	1	f	t
44	28	civilian	7	f	t
41	28	don	9	t	f
35	28	civilian	6	t	f
36	28	mafia	1	t	f
51	27	mafia	2	t	f
43	27	don	6	t	f
41	27	civilian	4	f	t
40	26	civilian	5	f	t
41	26	don	8	t	f
35	26	civilian	10	t	f
36	25	civilian	4	f	t
43	25	mafia	9	t	f
44	25	don	5	t	f
35	25	sheriff	8	t	f
44	24	civilian	8	f	t
42	24	don	9	t	f
41	24	sheriff	10	t	f
34	23	civilian	3	f	t
36	23	mafia	10	t	f
43	23	sheriff	9	t	f
37	22	sheriff	10	f	t
41	22	don	7	t	f
39	22	civilian	1	t	f
46	22	civilian	9	t	f
43	33	mafia	6	t	f
34	33	civilian	4	t	f
40	33	civilian	3	t	f
53	33	civilian	9	t	f
41	31	civilian	9	t	f
34	27	civilian	8	t	f
46	26	civilian	7	t	f
34	24	civilian	4	t	f
39	23	civilian	1	t	f
35	8	civilian	7	f	t
37	8	mafia	9	t	f
41	8	don	10	t	f
45	7	civilian	10	t	f
45	3	civilian	6	t	f
42	1	sheriff	5	t	t
52	34	mafia	1	f	f
41	34	civilian	2	f	f
43	34	civilian	4	f	f
36	34	civilian	6	f	f
44	34	civilian	8	f	f
46	34	mafia	10	f	f
34	34	sheriff	7	f	t
40	34	civilian	3	t	f
35	34	don	5	t	f
37	34	civilian	9	t	f
44	35	mafia	1	f	f
40	35	civilian	2	f	f
41	35	civilian	3	f	f
43	35	civilian	4	f	f
36	35	mafia	5	f	f
52	35	sheriff	6	f	f
37	35	don	7	f	f
34	35	civilian	8	f	f
35	35	civilian	9	f	f
46	35	civilian	10	f	f
44	39	civilian	1	f	t
36	39	civilian	10	t	f
35	39	civilian	8	t	f
46	39	civilian	9	t	f
40	39	civilian	6	f	f
43	39	civilian	7	f	f
34	39	civilian	5	f	f
37	39	civilian	2	f	f
42	39	civilian	4	f	f
41	39	civilian	3	f	f
\.


--
--

COPY public.users (telegram_id, first_name, last_name, username) FROM stdin;
466508667	Vladimir	Stepanov	tovarischduraley
\.

--
--

SELECT pg_catalog.setval('public.games_id_seq', 39, true);


--
--

SELECT pg_catalog.setval('public.users_id_seq', 106, true);


--
--

SELECT pg_catalog.setval('public.users_telegram_id_seq', 1, false);


--
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
--

ALTER TABLE ONLY public.players_games
    ADD CONSTRAINT users_games_pkey PRIMARY KEY (player_id, game_id);


--
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);



ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey1 PRIMARY KEY (telegram_id);



ALTER TABLE ONLY public.players_games
    ADD CONSTRAINT players_games_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id);



ALTER TABLE ONLY public.players_games
    ADD CONSTRAINT players_games_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(id);
