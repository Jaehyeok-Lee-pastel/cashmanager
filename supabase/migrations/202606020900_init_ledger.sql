-- Init ledger schema for the AI natural-language budget app (MVP).
--
-- Design: "Source-Tagged Ledger" (single transactions table + source enum).
-- All tables: RLS ON, tenant key = user_id (= auth.uid()).
-- Backend uses service_role (bypasses RLS) -> service layer MUST re-verify ownership.
-- Money is stored as bigint KRW integer won (amount_minor); sign is carried by `direction`.

-- Input channel enum (v2 values pre-reserved: receipt / voice / import).
create type public.tx_source as enum ('nl_text', 'manual', 'receipt', 'voice', 'import');

-- 1) profiles : 1:1 mirror of auth.users (auto-created by signup trigger).
--    `email` included to stay consistent with supabase/seed.sql (profiles(id, email)).
create table public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  email        text not null,
  display_name text,
  created_at   timestamptz not null default now()
);
alter table public.profiles enable row level security;
create policy profiles_self on public.profiles
  for all using (id = auth.uid()) with check (id = auth.uid());

-- 2) categories : per-user; default Korean set seeded on signup.
create table public.categories (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  name        text not null,
  emoji       text,
  sort_order  int  not null default 100,
  archived_at timestamptz,                       -- soft delete (preserve past-tx FK)
  created_at  timestamptz not null default now(),
  unique (user_id, name)
);
create index idx_categories_user on public.categories (user_id, sort_order)
  where archived_at is null;
alter table public.categories enable row level security;
create policy categories_owner on public.categories
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- 3) transactions : single ledger; input source kept as metadata.
create table public.transactions (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  category_id  uuid references public.categories(id) on delete set null,  -- allow uncategorized
  amount_minor bigint not null check (amount_minor > 0),   -- KRW integer won
  direction    text not null default 'expense'
               check (direction in ('expense', 'income')),
  memo         text,
  occurred_on  date not null default current_date,
  source       public.tx_source not null default 'manual',
  raw_input    text,                              -- original NL line (re-parse / debug / few-shot)
  parse_meta   jsonb,                             -- {confidence, model, latency_ms, parsed_category_name, corrected}
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);
create index idx_tx_user_date     on public.transactions (user_id, occurred_on desc);
create index idx_tx_user_cat_date on public.transactions (user_id, category_id, occurred_on);
alter table public.transactions enable row level security;
create policy tx_owner on public.transactions
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- 4) merchant_category_map : RESERVED for v2 learning loop.
--    MVP code never reads/writes this. Created empty so v2 starts "with data".
create table public.merchant_category_map (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  keyword     text not null,                      -- normalized merchant / keyword
  category_id uuid not null references public.categories(id) on delete cascade,
  hit_count   int  not null default 1,
  updated_at  timestamptz not null default now(),
  unique (user_id, keyword)
);
create index idx_mcm_user on public.merchant_category_map (user_id);
alter table public.merchant_category_map enable row level security;
create policy mcm_owner on public.merchant_category_map
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- updated_at auto-touch on transactions.
create function public.touch_updated_at() returns trigger
  language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;
create trigger trg_tx_updated_at before update on public.transactions
  for each row execute function public.touch_updated_at();

-- Defense-in-depth: a transaction's category must belong to the same user.
-- (service_role bypasses RLS, so this guards any future write path that forgets
--  the service-layer ownership check.)
create function public.enforce_category_owner() returns trigger
  language plpgsql as $$
begin
  if new.category_id is not null
     and not exists (
       select 1 from public.categories
       where id = new.category_id and user_id = new.user_id
     ) then
    raise exception 'category % does not belong to user %', new.category_id, new.user_id;
  end if;
  return new;
end;
$$;
create trigger trg_tx_category_owner
  before insert or update on public.transactions
  for each row execute function public.enforce_category_owner();

-- Signup trigger: create profile + seed default Korean categories.
create function public.handle_new_user() returns trigger
  language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email) values (new.id, new.email);
  insert into public.categories (user_id, name, sort_order)
  select new.id, c.name, c.ord
  from (values
    ('식비', 1), ('카페/간식', 2), ('교통', 3), ('생활/마트', 4),
    ('쇼핑', 5), ('문화/여가', 6), ('건강/의료', 7), ('주거/통신', 8),
    ('경조사', 9), ('교육', 10), ('기타지출', 11), ('수입', 12)
  ) as c(name, ord);
  return new;
end;
$$;
create trigger on_auth_user_created
  after insert on auth.users for each row execute function public.handle_new_user();
