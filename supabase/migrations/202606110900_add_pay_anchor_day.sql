-- Pay-cycle budgeting: a user's payday (1~31). When set, the summary's budget
-- window shifts to [payday ~ next payday) instead of the calendar month, so
-- "오늘 쓸 수 있어요" doesn't reset on the 1st mid-cycle. NULL = calendar month
-- (current behavior, opt-in). 31 clamps to each month's last day at read time.

alter table public.profiles
  add column if not exists pay_anchor_day smallint
  check (pay_anchor_day is null or (pay_anchor_day between 1 and 31));
