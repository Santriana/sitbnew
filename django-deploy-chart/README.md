# Django Deploy Helm Chart
## Configuration
| **Parameter**  | **Description**  |  **Default** |
|---|---|---|
|application.database_url|URL formatted to be passed to app as DATABASE_URL environment   |   |
|service.url   |URL where this app should be accessible   |   |
|image.repository  |image repository without tag   |   |
|image.tag  |image tag   |   |
|imagePullSecrets   |Pull secret name of the gitlab registry   |   |
|gitlab.app   |(Optional) You must pass $CI_PROJECT_PATH_SLUG in order for prometheus metrics to work   |   |
|gitlab.env   |(Optional) You must pass $CI_ENVIRONMENT_SLUG in order for prometheus metrics to work    |   |
|global.postgresql.postgresqlPassword|password for the postgresql database||
|global.postgresql.postgresqlDatabase|database name for the postgresql||

## PostgreSQL
This chart depend on PostgreSQL helm chart by Bitnami (helm chart version: 8.10.14, PostgreSQL: 11.8)

## Using this Chart In Your Project
To use this chart please follow instructions below:

### Clone As Subtree
Pull this repository as subtree in your project's root directory. Here we are pulling it in `django-deploy-chart` directory:

```commandline
git subtree add --prefix django-deploy-chart git@git.erasysconsulting.com:internal/charts/django-deploy-chart.git master --squash
```

### Gitlab CI YAML
Create .gitlab-ci.yml file in your project's root directory.
```yaml
#.gitlab-ci.yml
stages:
  - test
  - build
  - deploy
  - performance
  - sast
  - dast

variables:
  IMAGE_REPOSITORY: ${CI_APPLICATION_REPOSITORY:-$CI_REGISTRY_IMAGE/$CI_COMMIT_REF_SLUG}
  IMAGE_TAG: ${CI_APPLICATION_TAG:-$CI_COMMIT_SHA}
  DB_PASSWORD: "P1np1np1N"
  SECRET_NAME: "gitlab-registry-${CI_PROJECT_PATH_SLUG}"
  GITLAB_FEATURES: "dast"

test:
  variables: 
    POSTGRES_PASSWORD: ${DB_PASSWORD}
    POSTGRES_DB: ${CI_PROJECT_PATH_SLUG}
    DATABASE_URL: "postgres://postgres:${DB_PASSWORD}@postgres:5432/${CI_PROJECT_PATH_SLUG}"
  services: 
    - postgres:latest
  stage: test
  image: python:3.8
  script:
    - pip install -r requirements.txt 
    - python manage.py test --noinput
  except:
    - staging
    - production

deploy_preview:
  stage: deploy
  image: dtzar/helm-kubectl:3.2.4
  tags:
    - kubernetes
  environment:
    name: review/$CI_BUILD_REF_NAME
    url: https://${CI_PROJECT_ID}-${CI_ENVIRONMENT_SLUG}.${KUBE_INGRESS_BASE_DOMAIN}
    on_stop: stop_preview
    auto_stop_in: 1 week
  variables:
    DB_URL: "postgres://postgres:${DB_PASSWORD}@${CI_COMMIT_REF_SLUG}-postgresql:5432/${CI_PROJECT_PATH_SLUG}"
  script:
    - kubectl config set-cluster ErasysDevCluster --server=${KUBE_URL} --certificate-authority=${KUBE_CA_PEM_FILE}
    - kubectl config set-credentials gitlab --token="${KUBE_TOKEN}"
    - kubectl config set-context preview --cluster=ErasysDevCluster --user=gitlab --namespace=${KUBE_NAMESPACE}
    - kubectl config use-context preview
    - kubectl create secret -n "$KUBE_NAMESPACE"
      docker-registry "${SECRET_NAME}"
      --docker-server="$CI_REGISTRY"
      --docker-username="${CI_DEPLOY_USER:-$CI_REGISTRY_USER}"
      --docker-password="${CI_DEPLOY_PASSWORD:-$CI_REGISTRY_PASSWORD}"
      --docker-email="$GITLAB_USER_EMAIL"
      -o yaml --dry-run | kubectl replace -n "$KUBE_NAMESPACE" --force -f - # create secret to pull from registry
    - helm repo add bitnami https://charts.bitnami.com/bitnami # postgresql
    - helm dependency update ./django-deploy-chart
    - helm upgrade
      --install
      --set application.database_url="${DB_URL}"
      --set image.repository="${CI_APPLICATION_REPOSITORY:-$CI_REGISTRY_IMAGE/$CI_COMMIT_REF_SLUG}"
      --set-string image.tag="${CI_APPLICATION_TAG:-$CI_COMMIT_SHA}"
      --set service.url=https://${CI_PROJECT_ID}-${CI_ENVIRONMENT_SLUG}.${KUBE_INGRESS_BASE_DOMAIN}
      --set imagePullSecrets=${SECRET_NAME}
      --set global.postgresql.postgresqlPassword="${DB_PASSWORD}"
      --set global.postgresql.postgresqlDatabase="${CI_PROJECT_PATH_SLUG}"
      --set gitlab.app=$CI_PROJECT_PATH_SLUG
      --set gitlab.env=$CI_ENVIRONMENT_SLUG
      --wait
      ${CI_COMMIT_REF_SLUG}
      ./django-deploy-chart
    - echo $CI_ENVIRONMENT_URL > environment_url.txt
  artifacts:
    paths:
      - environment_url.txt

performance:
  stage: performance
  dependencies:
    - deploy_preview
  variables:
    URL: environment_url.txt
    SITESPEED_OPTIONS: "-d 2"

bandit:
  stage: sast
  allow_failure: true
  image: docker:latest
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
  services:
    - docker:dind
  script:
    - docker run --rm -v ${PWD}:/code opensorcery/bandit -r /code -o bandit_reports.html -f html
  artifacts:
    when: on_failure
    paths:
      - bandit_reports.html

dast:
  stage: dast
  dependencies:
    - deploy_preview
  script:
    - export DAST_WEBSITE=${DAST_WEBSITE:-$(cat environment_url.txt)}
    - if [ -z "$DAST_WEBSITE$DAST_API_SPECIFICATION" ]; then echo "Either DAST_WEBSITE or DAST_API_SPECIFICATION must be set. See https://docs.gitlab.com/ee/user/application_security/dast/#configuration for more details." && exit 1; fi
    - /analyze -r report.html
    - cp /output/report.html .
  artifacts:
    paths:
      - report.html
    when: on_failure

stop_preview:
  stage: deploy
  variables:
    GIT_STRATEGY: none
  image: dtzar/helm-kubectl:3.2.4
  tags:
    - kubernetes
  script:
    - kubectl config set-cluster ErasysDevCluster --server=${KUBE_URL} --certificate-authority=${KUBE_CA_PEM_FILE}
    - kubectl config set-credentials gitlab --token="${KUBE_TOKEN}"
    - kubectl config set-context preview --cluster=ErasysDevCluster --user=gitlab --namespace=${KUBE_NAMESPACE}
    - kubectl config use-context preview
    - helm uninstall ${CI_COMMIT_REF_SLUG}
  when: manual
  environment:
    name: review/$CI_BUILD_REF_NAME
    action: stop


include:
  - template: Security/DAST.gitlab-ci.yml  # https://gitlab.com/gitlab-org/gitlab-foss/-/blob/master/lib/gitlab/ci/templates/Security/DAST.gitlab-ci.yml
  - template: Jobs/Build.gitlab-ci.yml  # https://gitlab.com/gitlab-org/gitlab-foss/blob/master/lib/gitlab/ci/templates/Jobs/Build.gitlab-ci.yml
  - template: Jobs/Browser-Performance-Testing.gitlab-ci.yml  # https://gitlab.com/gitlab-org/gitlab-foss/blob/master/lib/gitlab/ci/templates/Jobs/Browser-Performance-Testing.gitlab-ci.yml
```

### Dockerfile
Create a filename called _Dockerfile_ in your project's root folder.
```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.8
LABEL maintainer="adityaw@erasysconsulting.com"

COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install -r /code/requirements.txt
RUN pip install gunicorn

EXPOSE 8000

# Copy the current directory contents into the container at /code/
COPY . /code/

# Run start.sh
WORKDIR /code/
ENTRYPOINT ["sh", "start.sh"]
```

### Docker Entrypoint Shell Script
Create _start.sh_ (or any other name depending on _Dockerfile_ above) in your project's root folder.
```shell script
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn my_application.wsgi:application --bind 0.0.0.0:8000
```

### Django Project
#### DATABASE_URL
This chart will pass `DATABASE_URL` environment to be consumed by your Django app. You can use [django-environ](https://pypi.org/project/django-environ/) or any other package to read this format.

```python
# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
}
```

#### Gunicorn
You'll also need [Gunicorn](https://pypi.org/project/gunicorn/) in your requirements.txt.

## Sample Project
You can view sample project here: https://git.erasysconsulting.com/internal/dev/django-preview-sample
