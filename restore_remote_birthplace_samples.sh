#!/bin/bash


psql -h localhost -p 54321 -U sentimantic -d sentimantic  < ./samples.backup

psql -h localhost -p 54321 -U sentimantic -d sentimantic < ./sample_birthplace_person_gpe.backup

