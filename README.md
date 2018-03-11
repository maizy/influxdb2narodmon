# influxdb2narodmon

Send metrics from influxdb to [narodmon.ru](narodmon.ru).

## Install requirements

```
python3 -m pip install [--user] -r requirements.txt
```

## Configuration

_TODO_ (for now see `main` function)


## Usage

Send metrics:

```
INFLUXDB_HOST=localhost INFLUXDB_PORT=8086 INFLUXDB_USER=root INFLUXDB_PASSWORD=pa$$word \
    python3 influxdb2narodmon.py
```

See configuration info:

```
python3 influxdb2narodmon.py info
```

## License

Apache 2
