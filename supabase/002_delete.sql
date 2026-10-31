-- Swatchwork Minis: lets the site's Delete button remove a mini.
-- Paste into Supabase -> SQL Editor -> New query, then Run. Safe to run again.
--
-- Deleting takes the mini off the site straight away and records it here;
-- the sync workflow then removes it from the repo and from photo storage.

create table if not exists public.deletions (
  id          bigint generated always as identity primary key,
  mini_id     text not null,
  name        text,
  status      text not null default 'pending',   -- pending | done
  created_by  uuid default auth.uid(),
  created_at  timestamptz not null default now(),
  done_at     timestamptz
);

alter table public.deletions enable row level security;

drop policy if exists "admins view deletions" on public.deletions;
create policy "admins view deletions" on public.deletions for select to authenticated
  using (public.is_admin());

create or replace function public.delete_mini(mini text)
returns void
language plpgsql security definer set search_path = public
as $$
begin
  if not public.is_admin() then
    raise exception 'not allowed';
  end if;
  insert into public.deletions (mini_id, name)
    select id, name from public.minis where id = mini;
  if not found then
    raise exception 'no such mini';
  end if;
  delete from public.minis where id = mini;
end;
$$;

revoke all on function public.delete_mini(text) from public, anon;
grant execute on function public.delete_mini(text) to authenticated;
