# CodeforcesSpider

## Crawl Source Code

Please first refer to https://github.com/jhao104/proxy_pool, 
start redis service, schedule (`python proxyPool.py schedule`) 
and server (`python proxyPool.py server`). Please make sure that 
the above two commands are running in the background.

Then start crawling using

```shell
python crawl_code.py Java 0-9
```

where the first argument refers to the language, chosen from 
"C++", "Java", "Python" and "Rust". The second argument denotes 
the split range, valid format: "1" or "2-8".

### Crawl status

|           | C++  | Java | Python | Rust |
|-----------|------|------|--------|------|
| Total     | 0-94 | 0-16 | 0-14   | 0    |
| Working   |      | 0-16 | 0-9    | 0    |
| Available | 0-94 | N.A. | 10-14  | N.A. |
| Done      |      |      |        |      |
