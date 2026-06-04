-- Split "주거/통신" into "주거"(housing+utilities) and "통신"(telecom).
-- Existing transactions stay attached (category_id unchanged) — only the name changes to 주거.

-- 1) rename existing 주거/통신 -> 주거 (keeps past transactions under 주거)
update public.categories set name = '주거' where name = '주거/통신';

-- 2) add 통신 for existing users (if missing)
insert into public.categories (user_id, name, sort_order)
select p.id, '통신', 9
from public.profiles p
where not exists (
  select 1 from public.categories c where c.user_id = p.id and c.name = '통신'
);

-- 3) update signup trigger: seed 주거 + 통신 separately
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
    ('기타지출', 13), ('수입', 14)
  ) as c(name, ord);
  return new;
end;
$$;
