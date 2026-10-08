// Jenkins BUILD & Quality Gate for ACEest Fitness & Gym
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
    }

    triggers {
        // GitHub webhooks cannot reach a lab VM, so poll GitHub every 5 minutes
        pollSCM('H/5 * * * *')
    }

    environment {
        IMAGE_NAME = 'aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
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

        stage('Unit Tests') {
            steps {
                sh '''
                    set +e
                    docker run --name aceest-tests-$IMAGE_TAG $IMAGE_NAME:test-$IMAGE_TAG
                    status=$?
                    mkdir -p reports
                    docker cp aceest-tests-$IMAGE_TAG:/tmp/reports/junit.xml reports/junit.xml
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

        stage('Build Runtime Image') {
            steps {
                sh 'docker build --target runtime -t $IMAGE_NAME:$IMAGE_TAG -t $IMAGE_NAME:latest .'
                sh 'docker images $IMAGE_NAME'
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
    }

    post {
        always {
            sh 'docker rm -f aceest-smoke-$IMAGE_TAG aceest-tests-$IMAGE_TAG || true'
            sh 'docker rmi $IMAGE_NAME:test-$IMAGE_TAG || true'
        }
        success {
            echo "BUILD SUCCESS: ${IMAGE_NAME}:${IMAGE_TAG} built, linted and tested."
        }
        failure {
            echo 'BUILD FAILED: check the stage logs above.'
        }
    }
}
