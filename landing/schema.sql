-- Tabla de contactos de la landing de ServiSync.
-- Ejecutar en Supabase > SQL Editor.
-- La clave pública (anon / publishable) solo puede INSERTAR: no puede leer, modificar ni borrar.

create table if not exists public.contactos (
  id                bigint generated always as identity primary key,
  created_at        timestamptz not null default now(),
  nombre            text not null check (char_length(nombre) between 2 and 100),
  email             text not null check (char_length(email) <= 200 and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  telefono          text check (char_length(telefono) <= 30),
  empresa           text check (char_length(empresa) <= 120),
  sector            text check (char_length(sector) <= 60),
  mensaje           text check (char_length(mensaje) <= 2000),
  acepta_privacidad boolean not null check (acepta_privacidad),
  origen            text not null default 'landing' check (char_length(origen) <= 40)
);

alter table public.contactos enable row level security;

-- Sin políticas de SELECT/UPDATE/DELETE: RLS bloquea esas operaciones para anon.
drop policy if exists "landing inserta contactos" on public.contactos;
create policy "landing inserta contactos" on public.contactos
  for insert to anon
  with check (true);

grant insert on public.contactos to anon;
