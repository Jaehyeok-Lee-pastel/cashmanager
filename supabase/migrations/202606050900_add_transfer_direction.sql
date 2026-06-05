-- Add a 'transfer' direction for money movement that is NOT consumption.
--
-- Rationale: the ledger records spending at purchase time (each card swipe is an
-- expense). The monthly card bill (카드대금) is then a TRANSFER of cash to pay off
-- that spending — recording it as an expense would double-count the individual
-- purchases. Transfers are excluded from expense/income totals, budgets, and
-- insights (the service layer filters direction = 'expense'/'income').
--
-- Also covers future cases: account transfers, savings transfers.

alter table public.transactions
  drop constraint if exists transactions_direction_check;

alter table public.transactions
  add constraint transactions_direction_check
  check (direction in ('expense', 'income', 'transfer'));
