### Setup Guide

Run playwright container using docker compose first.
```shell
docker compose up -d
```

### Running Test Cases

Run following command to run the test cases.
```shell
# from the root directory
python -m src.services.tests.test_url
```