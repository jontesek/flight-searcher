# Flight searcher

## Installation and usage

1. Setup your `.env` file: `cp .env.template .env`
2. `docker-compose up`

The service is then accessible on URL `http://127.0.0.1:8080` and you can use two endpoints:

* GET `/top_flights/`: search flights
    * example: `http://127.0.0.1:8080/top_flights/?src_country=BE&dst_country=US&departure_date=2022-10-20`
* GET `/health`: health check
    * example: `http://127.0.0.1:8080/health`

More details are available in the generated [Swagger docs](http://127.0.0.1:8080/docs).

### Without Docker

You can also run the app without Docker (for easier debugging and testing):
1. `poetry shell`
2. `uvicorn flight_searcher.api.app:app --port 8080`

Note: you must have a redis-server installed (`brew install redis`) and running (`brew services start redis`). To disable it, run `redis-cli shutdown`.

## Description

### Architecture

Flow:
1. Input request: src_country, dst_country, date, number of airports
2. Get the most popular airports for both countries
3. Get flights between the airports

Services:
* API: to serve clients: `FastAPI`
* Redis: for caching: `aioredis`

`Flight_searcher` package:
```
/api
    /routers - defined endpoints
    app.py - this creates APP
/clients - redis and http
/providers - handle airports and flights: either get from kiwi or from redis
container.py - dependencies
service.py - main program (core) - uses providers, is called from API router
settings.py
```

### Async

I tried to use `async` where it makes sense - so for methods which contain calls to external services (redis, db, api).

In requests to Kiwi APIs I used [request-session](https://github.com/kiwicom/request-session) package which doesn't support async, but I like it bcs of logging and repeats. Instead could be used e.g. [HTTPX](https://www.python-httpx.org/). But since there is caching I don't think it's such a bottleneck.

### Dependencies

I used [Dependency Injector](https://python-dependency-injector.ets-labs.org/) for solving depedencies. I think it's useful and makes code less magical.

For settings I used [Pydantic](https://pydantic-docs.helpmanual.io/usage/settings/). I could use `DI injector` config functionality instead, but this is probably better and easier to use in code. And you can create DI config from the Pydantic settings.

## TODO

* Tests (unit and for API)
* Use async HTTP client.
* Beware of Redis overflow by chance or by hacker - put some limit how many results can be store in Redis.
* Deployment to production - choose `uvicorn` with one process, `uvicorn` with multiple processes, `gunicorn` with uvicorn workers. It would depend on autoscaling setup in Kubernetes.
