# rate-limiter-test

This example test shows how to implement a rate limiter with Flask and redis.

### How to set up the project
* First make sure you have python 3 installed on your computer, preferably python 3.6+ and above.
* Then proceed to installing [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/). docker-compose will help manage multiple images to be run.
* Then clone this project ```git clone https://github.com/Frost199/rate-limiter-test.git```
* cd into the base directory.

### Build the project
After installation, you will build the project with the __*build*__ command in docker-compose
```shell
docker-compose build
```

### Run the project
When your build is done, you can run the project with the __*up*__ command in docker-compose
```shell
docker-compose up
```

### Manual testing of the application
When our build is up, you can test the endpoints found in ``app.py``

```shell
curl http://127.0.0.1:8000/
```

```shell
curl http://127.0.0.1:8000/second-page
```


## Response

The response object from each endpoint returns either a 200 OK, or a 403 unauthorized status code 

#### Success

```json
{
  "data": "Hello User", 
  "success": "200"
}
```

#### Error

```json
{
  "data": "Too many requests, You hit the rate limit", 
  "error": "403"
}
```

