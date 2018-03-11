# influxdb2narodmon

Send metrics from influxdb to [narodmon.ru](narodmon.ru).

## Install requirements

```
python3 -m pip install -r requirements.txt
```

## Usage

```
INFLUXDB_HOST=localhost [INFLUXDB_PORT=8086] [INFLUXDB_USER=root] [INFLUXDB_PASSWORD=pa$$word] \
    python3 influxdb2narodmon.py
```

## License

Apache 2
