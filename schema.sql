-- Im Supabase SQL Editor ausführen. Öffentliche Besucher dürfen nur lesen.
create table if not exists public.offers (
  id text primary key,
  name text not null,
  market text not null,
  city text not null,
  branch text,
  category text not null default 'Sonstiges',
  quantity text,
  price numeric(10,2) not null check (price >= 0),
  old_price numeric(10,2),
  valid_from date not null,
  valid_until date not null,
  source_url text,
  emoji text,
  tint text,
  created_at timestamptz not null default now(),
  constraint valid_period check (valid_until >= valid_from)
);
create index if not exists offers_dates_idx on public.offers(valid_from, valid_until);
alter table public.offers enable row level security;
drop policy if exists "Public read offers" on public.offers;
create policy "Public read offers" on public.offers for select to anon using (true);
-- Kein öffentliches INSERT / UPDATE / DELETE! Nur über Dashboard / sicheren Server.
