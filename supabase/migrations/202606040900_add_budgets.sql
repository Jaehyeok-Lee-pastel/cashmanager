-- Category-level monthly budgets (recurring limit per category).
-- One limit per (user, category); applies to every month until changed.

create table public.category_budgets (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  category_id uuid not null references public.categories(id) on delete cascade,
  limit_minor bigint not null check (limit_minor > 0 and limit_minor <= 1000000000000),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (user_id, category_id)
);
create index idx_budgets_user on public.category_budgets (user_id);
alter table public.category_budgets enable row level security;
create policy budgets_owner on public.category_budgets
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- updated_at auto-touch (reuse touch_updated_at from init_ledger migration)
create trigger trg_budget_updated_at before update on public.category_budgets
  for each row execute function public.touch_updated_at();

-- Defense-in-depth: a budget's category must belong to the same user
-- (service_role bypasses RLS, so guard any write path that forgets the check).
create function public.enforce_budget_category_owner() returns trigger
  language plpgsql as $$
begin
  if not exists (
    select 1 from public.categories
    where id = new.category_id and user_id = new.user_id
  ) then
    raise exception 'category % does not belong to user %', new.category_id, new.user_id;
  end if;
  return new;
end;
$$;
create trigger trg_budget_category_owner
  before insert or update on public.category_budgets
  for each row execute function public.enforce_budget_category_owner();
