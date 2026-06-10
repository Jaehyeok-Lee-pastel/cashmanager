-- Add an "투자" category (investment/savings destination). Investments are recorded
-- as transfers (excluded from spending), and this category can hold an optional
-- monthly investment TARGET (budget) tracked in the summary.

-- 1) add 투자 for existing users (skip if they already made one manually)
insert into public.categories (user_id, name, sort_order)
select p.id, '투자', 13
from public.profiles p
where not exists (
  select 1 from public.categories c where c.user_id = p.id and c.name = '투자'
);

-- 2) seed 투자 for new users
create or replace function public.handle_new_user() returns trigger
  language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email) values (new.id, new.email);
  insert into public.categories (user_id, name, sort_order)
  select new.id, c.name, c.ord
  from (values
    ('식비', 1), ('카페/간식', 2), ('교통', 3), ('생활/마트', 4),
    ('쇼핑', 5), ('문화/여가', 6), ('건강/의료', 7), ('주거', 8),
    ('통신', 9), ('경조사', 10), ('교육', 11), ('카드대금', 12),
    ('투자', 13), ('기타지출', 14), ('수입', 15)
  ) as c(name, ord);
  return new;
end;
$$;
