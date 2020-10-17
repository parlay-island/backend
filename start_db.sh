#!/bin/bash
docker pull postgres
docker run --name parlay-island-db -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
