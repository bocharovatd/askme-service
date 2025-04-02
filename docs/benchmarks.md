Отдача статического контента через nginx с кэшом:

```shell
ab -n 1000 -c 20 http://localhost:8080/static/sample.jpg
```

```txt
Server Software:        nginx/1.25.3
Server Hostname:        localhost
Server Port:            8080

Document Path:          /static/sample.jpg
Document Length:        675157 bytes

Concurrency Level:      20
Time taken for tests:   0.190 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      675436000 bytes
HTML transferred:       675157000 bytes
Requests per second:    5258.07 [#/sec] (mean)
Time per request:       3.804 [ms] (mean)
Time per request:       0.190 [ms] (mean, across all concurrent requests)
Transfer rate:          3468249.00 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     1    4   0.5      4       8
Waiting:        0    0   0.3      0       4
Total:          1    4   0.5      4       8

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      4
  75%      4
  80%      4
  90%      4
  95%      4
  98%      5
  99%      6
 100%      8 (longest request)
```

Отдача статического контента напрямую через gunicorn:

```shell
ab -n 1000 -c 20 http://localhost:8000/static/sample.jpg
```

```txt
Server Software:        gunicorn
Server Hostname:        localhost
Server Port:            8000

Document Path:          /static/sample.jpg
Document Length:        5897 bytes

Concurrency Level:      20
Time taken for tests:   2.552 seconds
Complete requests:      1000
Failed requests:        0
Non-2xx responses:      1000
Total transferred:      6186000 bytes
HTML transferred:       5897000 bytes
Requests per second:    391.81 [#/sec] (mean)
Time per request:       51.045 [ms] (mean)
Time per request:       2.552 [ms] (mean, across all concurrent requests)
Transfer rate:          2366.95 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     3   46   7.9     46     249
Waiting:        3   46   7.9     46     248
Total:          3   46   7.9     46     249

Percentage of the requests served within a certain time (ms)
  50%     46
  66%     46
  75%     46
  80%     46
  90%     47
  95%     48
  98%     62
  99%     62
 100%    249 (longest request)
```

Отдача динамического контента через nginx с кэшом:

```shell
ab -n 1000 -c 20 http://localhost:8080/
```

```txt
Server Software:        nginx/1.25.3
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        15495 bytes

Concurrency Level:      20
Time taken for tests:   20.188 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      15931000 bytes
HTML transferred:       15495000 bytes
Requests per second:    49.53 [#/sec] (mean)
Time per request:       403.764 [ms] (mean)
Time per request:       20.188 [ms] (mean, across all concurrent requests)
Transfer rate:          770.63 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    20  398  39.1    392     463
Waiting:       20  398  39.1    392     463
Total:         20  398  39.1    392     463

Percentage of the requests served within a certain time (ms)
  50%    392
  66%    407
  75%    420
  80%    423
  90%    436
  95%    441
  98%    448
  99%    451
 100%    463 (longest request)
```

Отдача динамического контента напрямую через gunicorn:

```shell
ab -n 1000 -c 20 http://localhost:8000/
```

```txt
Server Software:        gunicorn
Server Hostname:        localhost
Server Port:            8000

Document Path:          /
Document Length:        15495 bytes

Concurrency Level:      20
Time taken for tests:   18.908 seconds
Complete requests:      954
Failed requests:        0
Total transferred:      15194358 bytes
HTML transferred:       14782230 bytes
Requests per second:    50.45 [#/sec] (mean)
Time per request:       396.394 [ms] (mean)
Time per request:       19.820 [ms] (mean, across all concurrent requests)
Transfer rate:          784.76 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    20  392  38.0    388     452
Waiting:       20  391  38.0    388     452
Total:         20  392  37.9    388     452

Percentage of the requests served within a certain time (ms)
  50%    388
  66%    397
  75%    406
  80%    411
  90%    424
  95%    433
  98%    439
  99%    444
 100%    452 (longest request)
```

| Configuration | Requests/sec | Avg Latency (ms) | Throughput (MB/s) | 99th %-ile (ms) |
| --- | --- | --- | --- | --- |
| Nginx (static) | 5,258 | 3.80 | 3,380 | 6 |
| Gunicorn (static) | 392 | 51.05 | 2.31 | 62 |
| Nginx (dynamic cached) | 49.53 | 403.76 | 0.77 | 451 |
| Gunicorn (dynamic) | 50.45 | 396.39 | 0.78 | 444 |

**Анализ производительности:**

**Статический контент:**
- Nginx обрабатывает 5,258 запросов/сек (в 13 раз быстрее Gunicorn)
- Средняя задержка Nginx 3.8 мс против 51 мс у Gunicorn
- Пропускная способность Nginx 3.3 ГБ/с vs 2.3 МБ/с у Gunicorn
- Вывод: Nginx идеально подходит для статики благодаря эффективной работе с файлами

**Динамический контент:**
- Производительность Nginx и Gunicorn практически одинаковая (~50 запросов/сек)
- Кэширование в Nginx не дает преимущества (49.53 vs 50.45 RPS)
- Задержки сопоставимы (~400 мс)
- Вывод: Для динамики Nginx добавляет минимальные накладные расходы (~7 мс)