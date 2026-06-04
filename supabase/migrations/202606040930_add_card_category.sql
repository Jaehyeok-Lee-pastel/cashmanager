-- Add a "카드대금" category for credit-card bill payments (was landing in 기타지출).

-- 1) backfill existing users
insert into public.categories (user_id, name, sort_order)
select p.id, '카드대금', 13
from public.profiles p
where not exists (
  select 1 from public.categories c
  where c.user_id = p.id and c.name = '카드대금'
);

-- 2) include it for new signups
create or replace function public.handle_new_user() returns trigger
  language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email) values (new.id, new.email);
  insert into public.categories (user_id, name, sort_order)
  select new.id, c.name, c.ord
  from (values
    ('식비', 1), ('카페/간식', 2), ('교통', 3), ('생활/마트', 4),
    ('쇼핑', 5), ('문화/여가', 6), ('건강/의료', 7), ('주거/통신', 8),
    ('경조사', 9), ('교육', 10), ('카드대금', 11), ('기타지출', 12), ('수입', 13)
  ) as c(name, ord);
  return new;
end;
$$;
