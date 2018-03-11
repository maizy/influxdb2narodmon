#!/usr/bin/env python3
# coding: utf-8
import os
import collections
import sys
from uuid import getnode
import socket
import hashlib

import influxdb

__version__ = '0.1'

# see setup at the end of the file

Metric = collections.namedtuple('Measurement', ['database', 'measurement', 'field', 'nm_metric_type'])


def send_metrics(mac, metrics, influxdb_client, time_range, narodmon_host='narodmon.ru', narodmon_port=8283):

    results = {}
    for metric in metrics:
        query = 'select mean("{f}") as "value" from "{m}" where time > now() - {r}'.format(
            f=_quote_itentifier(metric.field),
            m=_quote_itentifier(metric.measurement),
            r=time_range
        )
        query_result = influxdb_client.query(query, database=metric.database)
        row = next(query_result.get_points(), None)
        if row is not None:
            results[metric] = row['value']
        else:
            sys.stderr.write('No value for {}\n'.format(metric))
    sock = socket.socket()
    try:
        sock.connect((narodmon_host, narodmon_port))

        lines = ['#{}'.format(mac)]
        for metric, value in results.items():
            metric_id = _metric_id(metric)
            if isinstance(value, float):
                value = '{:0.4f}'.format(value)
            else:
                value = str(value)
            lines.append('#{mac}{id}#{value}'.format(mac=mac, id=metric_id, value=value))
        lines.append('##')

        data = '\n'.join(lines)
        sock.send(data.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8').rstrip()
        sock.close()
        if response != 'OK':
            sys.stderr.write('Unseccessfull response: {}\n'.format(response))
            return False
    except socket.error as e:
        sys.stderr.write('Unable to write data to narodmon\n{}\n'.format(e))
        return False
    return True


def _quote_itentifier(value):
    return value.replace('"', '\\"')


def _metric_id(metric):
    hash_ = hashlib.sha1('|'.join((metric.database, metric.measurement, metric.field)).encode('utf-8'))
    return (hash_.hexdigest())[0:4]


def main():
    # mac - some uniq sequince of [a-z0-9]
    mac = os.getenv('MAC', '{:012x}'.format(getnode())[0:12])

    metrics = [
        Metric(database='weather', measurement='weather', field='humidity', nm_metric_type='H1'),
        Metric(database='weather', measurement='weather', field='pressure', nm_metric_type='P1'),
        Metric(database='weather', measurement='weather', field='temperature', nm_metric_type='T1'),
    ]

    time_range = '5m'

    # influxdb connection settings
    host = os.getenv('INFLUXDB_HOST', 'localhost')
    port = int(os.getenv('INFLUXDB_PORT', 8086))
    user = os.getenv('INFLUXDB_USER', 'root')
    password = os.getenv('INFLUXDB_PASSWORD')

    cmd = sys.argv[1] if len(sys.argv) > 0 else 'send'
    if cmd == 'send':
        try:
            client = influxdb.InfluxDBClient(host, port, user, password)
            client.query('show databases')
        except Exception as e:
            sys.stderr.write('Unable to connect to influxdb\n{}\n'.format(e))
            sys.exit(2)
        result = send_metrics(mac, metrics, client, time_range)
        sys.exit(0 if result else 1)
    elif cmd == 'info':
        print('MAC: {}'.format(mac))

        print('Metrics:')
        for metric in metrics:
            id_ = _metric_id(metric)
            print(' * {}: {}'.format(id_, metric))

if __name__ == '__main__':
    main()
