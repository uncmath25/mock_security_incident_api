# Mock Security Incident API

### Description:
This project demonstrates a mock security incident API, as part of a take home exam.  It's Dockerized using a Flask web server.  It aggregates employee security incidents from a mock api: https://incident-api.use1stag.elevatesecurity.io/identities/ and exposes this aggregated employee incidents data at a GET API endpoint `/incidents`.

### Local Run Instructions:
1. Run ` make ` to build, flake and test the dev Flask web server Docker image
1. Run the dev container locally with ` make start `
1. Stop the container with ` make stop `

A production Docker image can also be built, which is based off the dev image.  This production image installs nginx and is ready to be run in production.
The environment variables (including sensitive information like passwords) are stored in the `.env` files (one for dev and on for prod).  Typically these files would not be excluded by the ".gitignore" file, but are included here to ensure that everything runs properly.

### Approach Summary:
About 4 hours was spend on this project (more than the target 3 hours).  But the additional time was mostly spent to "polish" and cleanup the project.  The project implementation essentially followed these steps:
1. Project review and exploration
  * TIME BUDGET ~ 30 min
  * Some time was taken to carefully review the project, understanding the problem and exploring the endpoints (never a good idea to rush this step).
1. Dockerized repo setup
  * TIME BUDGET ~ 30 min
  * An existing Dockerized Flask skeleton was repurposed: https://github.com/uncmath25/flask_docker_template and updated to provide a clean starting shell.  This ensured that an actual Flask api could be run locally before proceeding with any implementation.
1. Addressing the polling approach
  * TIME BUDGET ~ 60 min
  * Python is very useful for quickly developing APIs, but is weaker at handling asynchronous processing (as opposed to say JavaScript).  So this potential pain point was addressed first to determine whether this would be a blocker for development.  It was eventually solved, but took longer than necessary due to inexperience with this approach in Python.
1. Solving the actual problem
  * TIME BUDGET ~ 90 min
  * Once the previous steps were solved, the "actual work" could begin.  A sort of MVC pattern was utilized (although no "view" resource were necessary).  The raw data retrieval was abstracted into a "utility class", a polling manager was built to coordinate the process and implement the polling approach and a "static" aggregator class (functional in nature) was built to implement the real business logic.  This business logic took the majority of the time, as the necessary data aggregation was determined following additional api exploration and local python debugging sessions.  Additionally a "health" endpoint was built along the way, which proved very useful in diagnosing the polling update behavior.   This endpoint helped motivate the retry and update failure logic, which increased the stability of this api's long running polling process.
1. Cleanup and Documentation
  * TIME BUDGET ~ 45 min
  * Some time was taken to refactor the code, add code comments, clean the repo structure and thoughtfully construct a README file.

### Production Improvements:
As mentioned above, a production image is actually ready to be built.  The next step would be rigorous integration testing to ensure the stability and integrity of this api.  In particular, its performance should be evaluated as it runs over a long time, to diagnose memory or threading issues.  Additionally, the GET endpoint `/incidents` returns an increasingly large JSON payload, so API pagination or some other limiting capability would need to be added, so the GET endpoint can still serve a reasonable sized payload as the aggregated incidents data grows.
