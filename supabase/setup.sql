-- Swatchwork Minis: database setup for Supabase.
-- Paste all of this into Supabase -> SQL Editor -> New query, then Run.
-- Safe to run again: it only creates what's missing.

-- ---------- tables ----------

-- One row per mini. "data" holds the same entry as data/minis.json
-- (name, game, photo, paints with their colours and mask files, ...).
create table if not exists public.minis (
  id          text primary key,
  name        text not null,
  game        text,
  date        text,
  data        jsonb not null,
  updated_at  timestamptz not null default now()
);

-- Optional extra details per board game (data/games.json).
create table if not exists public.games (
  name  text primary key,
  data  jsonb not null
);

-- Lasso edits saved from the paint editor, waiting to be applied.
create table if not exists public.edits (
  id          bigint generated always as identity primary key,
  mini_id     text not null references public.minis(id) on delete cascade,
  doc         jsonb not null,
  status      text not null default 'pending',   -- pending | applied | skipped
  note        text,
  created_by  uuid default auth.uid(),
  created_at  timestamptz not null default now(),
  applied_at  timestamptz
);

-- Who may save edits. Logging in alone isn't enough; the email must be here.
create table if not exists public.admins (
  email  text primary key
);

create or replace function public.is_admin()
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (select 1 from public.admins where lower(email) = lower(auth.jwt() ->> 'email'));
$$;

-- ---------- access rules ----------
-- Everyone can view the gallery. Only admins can save edits.
-- Minis, games and photos are written only by the sync script (secret key).

alter table public.minis  enable row level security;
alter table public.games  enable row level security;
alter table public.edits  enable row level security;
alter table public.admins enable row level security;

drop policy if exists "anyone can view minis" on public.minis;
create policy "anyone can view minis" on public.minis for select using (true);

drop policy if exists "anyone can view games" on public.games;
create policy "anyone can view games" on public.games for select using (true);

drop policy if exists "admins save edits" on public.edits;
create policy "admins save edits" on public.edits for insert to authenticated
  with check (public.is_admin());

drop policy if exists "admins view edits" on public.edits;
create policy "admins view edits" on public.edits for select to authenticated
  using (public.is_admin());

-- ---------- photo storage ----------
-- Public bucket: anyone can view photos and masks; only the sync script uploads.
insert into storage.buckets (id, name, public)
values ('gallery', 'gallery', true)
on conflict (id) do update set public = true;

-- ---------- you ----------
-- Replace the address with the one you'll log in with, then run.
insert into public.admins (email) values ('YOUR-EMAIL@example.com')
on conflict do nothing;
