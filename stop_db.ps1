$env:HOST_MACHINE_NAME = $env:COMPUTERNAME
docker compose exec db-init python db-init/save.py
docker compose down