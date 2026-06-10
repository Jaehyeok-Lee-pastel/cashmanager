-- Recurring (fixed) expense/income rules — e.g. 월세 50만 매월 1일, 넷플릭스 13500 매월 15일.
-- Materialized into real transactions each month (past-due ones) and subtracted
-- from Safe-to-Spend (upcoming ones) so the "오늘 쓸 수 있는 돈" isn't optimistic.

create table public.recurring_rules (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  category_id  uuid references public.categories(id) on delete set null,
  amount_minor bigint not null check (amount_minor > 0 and amount_minor <= 1000000000000),
  direction    text not null default 'expense' check (direction in ('expense', 'income', 'transfer')),
  day_of_month int not null check (day_of_month between 1 and 31),
  memo         text,
  active       boolean not null default true,
  created_at   timestamptz not null default now()
);
create index idx_recurring_user on public.recurring_rules (user_id);
alter table public.recurring_rules enable row level security;
create policy recurring_owner on public.recurring_rules
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- Defense-in-depth: a rule's category must belong to the same user (service_role
-- bypasses RLS). Null category is allowed (uncategorized fixed cost).
create function public.enforce_recurring_category_owner() returns trigger
  language plpgsql
  set search_path = public as $$
begin
  if new.category_id is not null and not exists (
    select 1 from public.categories
    where id = new.category_id and user_id = new.user_id
  ) then
    raise exception 'category % does not belong to user %', new.category_id, new.user_id;
  end if;
  return new;
end;
$$;
create trigger trg_recurring_category_owner
  before insert or update on public.recurring_rules
  for each row execute function public.enforce_recurring_category_owner();
