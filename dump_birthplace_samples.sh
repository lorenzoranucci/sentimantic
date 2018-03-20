#!/bin/bash


pg_dump --host localhost --port 5432 --username sentimantic --format plain --verbose --file "./samples.backup" --table public.sample sentimantic

pg_dump --host localhost --port 5432 --username sentimantic --format plain --verbose --file "./sample_birthplace_person_gpe.backup" --table public.sample_birthplace_person_gpe sentimantic

