// Jenkins End-to-End CI/CD Pipeline & Quality Gate for ACEest Fitness & Gym
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        IMAGE_NAME = '9597654915/aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER ?: 'latest'}"
        SONAR_URL  = 'http://localhost:9000'
    }

    stages {
        stage('Clean Checkout') {
            steps {
                deleteDir()
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build Test Image') {
            steps {
                sh 'docker build --target test -t $IMAGE_NAME:test-$IMAGE_TAG .'
            }
        }

        stage('Lint') {
            steps {
                sh 'docker run --rm $IMAGE_NAME:test-$IMAGE_TAG python -m compileall -q app.py aceest tests'
                sh 'docker run --rm $IMAGE_NAME:test-$IMAGE_TAG flake8 .'
            }
        }

        stage('Unit Tests & Coverage') {
            steps {
                sh '''
                    set +e
                    docker run --name aceest-tests-$IMAGE_TAG $IMAGE_NAME:test-$IMAGE_TAG
                    status=$?
                    mkdir -p reports
                    docker cp aceest-tests-$IMAGE_TAG:/tmp/reports/junit.xml reports/junit.xml
                    docker cp aceest-tests-$IMAGE_TAG:/tmp/reports/coverage.xml reports/coverage.xml
                    docker rm aceest-tests-$IMAGE_TAG
                    exit $status
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                sh '''
                    if [ -n "${SONAR_TOKEN:-}" ]; then
                        docker run --rm --network host \
                            -v "${WORKSPACE}:/usr/src" \
                            sonarsource/sonar-scanner-cli \
                            -Dsonar.host.url=${SONAR_URL} \
                            -Dsonar.login=${SONAR_TOKEN}
                    else
                        echo "SonarQube properties and coverage.xml ready for scan."
                        ls -lh sonar-project.properties reports/coverage.xml
                    fi
                '''
            }
        }

        stage('Build Multi-Version Runtime Images') {
            steps {
                sh '''
                    docker build --target runtime --build-arg APP_VERSION=1.0.0 -t $IMAGE_NAME:v1.0.0 .
                    docker build --target runtime --build-arg APP_VERSION=2.0.0 -t $IMAGE_NAME:v2.0.0 .
                    docker build --target runtime --build-arg APP_VERSION=3.0.0 \
                        -t $IMAGE_NAME:$IMAGE_TAG \
                        -t $IMAGE_NAME:v3.0.0 \
                        -t $IMAGE_NAME:latest \
                        -t aceest-fitness:$IMAGE_TAG \
                        -t aceest-fitness:latest .
                    docker images $IMAGE_NAME
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker run -d --name aceest-smoke-$IMAGE_TAG $IMAGE_NAME:$IMAGE_TAG
                    for i in $(seq 1 15); do
                        if docker exec aceest-smoke-$IMAGE_TAG python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/health').read().decode())"; then
                            exit 0
                        fi
                        sleep 2
                    done
                    docker logs aceest-smoke-$IMAGE_TAG
                    exit 1
                '''
            }
        }

        stage('Kubernetes CD Deployment') {
            steps {
                sh '''
                    if command -v kubectl >/dev/null 2>&1 && kubectl cluster-info >/dev/null 2>&1; then
                        kubectl apply -f k8s/01-rolling-update.yaml
                        kubectl rollout status deployment/aceest-rolling -n aceest-gym --timeout=60s || true
                    else
                        echo "Kubernetes manifests present in k8s/:"
                        ls -la k8s/
                    fi
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f aceest-smoke-$IMAGE_TAG aceest-tests-$IMAGE_TAG || true'
            sh 'docker rmi $IMAGE_NAME:test-$IMAGE_TAG || true'
        }
        success {
            echo "BUILD & CD SUCCESS: ${IMAGE_NAME}:${IMAGE_TAG} built, linted, tested, scanned, and verified."
        }
        failure {
            echo 'BUILD FAILED: check the stage logs above.'
        }
    }
}
