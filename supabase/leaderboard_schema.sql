create extension if not exists pgcrypto;

create table if not exists public.defender_leaderboard (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 12),
  kills integer not null default 0,
  scene_state jsonb,
  created_at timestamptz not null default now()
);

alter table public.defender_leaderboard
  add column if not exists scene_state jsonb;

alter table public.defender_leaderboard enable row level security;

drop policy if exists "public read leaderboard" on public.defender_leaderboard;
create policy "public read leaderboard"
on public.defender_leaderboard
for select
to anon, authenticated
using (true);

drop policy if exists "public insert leaderboard" on public.defender_leaderboard;
create policy "public insert leaderboard"
on public.defender_leaderboard
for insert
to anon, authenticated
with check (
  char_length(name) between 1 and 12
  and kills >= 0
);
