-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.chats (
  id bigint NOT NULL,
  username character varying,
  first_name character varying,
  last_name character varying,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT chats_pkey PRIMARY KEY (id)
);
CREATE TABLE public.messages (
  chat_id bigint,
  is_bot boolean,
  text text,
  update_obj json,
  CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id)
);
CREATE TABLE public.settings (
  key character varying NOT NULL,
  value text,
  CONSTRAINT settings_pkey PRIMARY KEY (key)
);
CREATE TABLE public.subscriptions (
  chat_id bigint,
  panel_client_id character varying,
  url text,
  is_active boolean DEFAULT true,
  expity_time numeric,
  email text,
  CONSTRAINT subscriptions_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id)
);
CREATE TABLE public.payments (
  id serial PRIMARY KEY,
  amount integer NOT NULL,
  currency_code character varying NOT NULL,
  chat_id bigint REFERENCES public.chats(id),
  comment text,
  transaction_id character varying,
  created_at timestamp without time zone DEFAULT now()
);