#!/usr/bin/env python3
# coding: utf-8
import os
import collections
import sys
from uuid import getnode

import influxdb

# see setup at the end of the file
from influxdb.exceptions import InfluxDBClientError

Measurement = collections.namedtuple('Measurement', ['database', 'measurement', 'field', 'nm_metric_type'])


def send_measurements(measurements, influxdb_client, time_range, narodmon_host='narodmon.ru', narodmon_port=8283):

    results = {}
    for measurement in measurements:
        query = 'select mean("{f}") as "value" from "{m}" where time > now() - {r}'.format(
            f=_quote_itentifier(measurement.field),
            m=_quote_itentifier(measurement.measurement),
            r=time_range
        )
        query_result = influxdb_client.query(query, database=measurement.database)
        row = next(query_result.get_points(), None)
        if row is not None:
            results[measurement] = row['value']
        else:
            sys.stderr.write('No value for {}\n'.format(measurement))
    print('\n'.join('{}: {}'.format(k, v) for k, v in results.items()))

    # TODO: send data to narodmon
    return True


def _quote_itentifier(value):
    return value.replace('"', '\\"')

if __name__ == '__main__':
    # mac - some uniq sequince of a-z 0-9
    mac = os.getenv('MAC', '{:012x}'.format(getnode())[0:12])

    # measurements to send
    measurements = [
        Measurement(database='weather', measurement='weather', field='humidity', nm_metric_type='H1'),
        Measurement(database='weather', measurement='weather', field='pressure', nm_metric_type='P1'),
        Measurement(database='weather', measurement='unknown', field='unknown', nm_metric_type='P1'),
    ]

    time_range = '5m'

    # influxdb connection settings
    host = os.getenv('INFLUXDB_HOST', 'localhost')
    port = int(os.getenv('INFLUXDB_PORT', 8086))
    user = os.getenv('INFLUXDB_USER', 'root')
    password = os.getenv('INFLUXDB_PASSWORD')
    try:
        client = influxdb.InfluxDBClient(host, port, user, password)
        client.query('show databases')
    except Exception as e:
        sys.stderr.write('Unable to connect to influxdb\n{}\n'.format(e))
        sys.exit(2)
    result = send_measurements(measurements, client, time_range)
    sys.exit(0 if result else 1)
