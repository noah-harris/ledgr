$env:HOST_MACHINE_NAME = $env:COMPUTERNAME
docker compose --profile seed up --build
