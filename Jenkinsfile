pipeline {
    agent any
    environment {
        APP_GIT_URL = "https://github.com/pornpasok/demo-python-app.git"
        APP_TAG = "latest"
        APP_NAME = "demo-python-app"
        APP_PORT = "5000"
        DEV_PROJECT = "default"
        NEXUS_SERVER = "https://index.docker.io/v1/"
        DOCKER_USER = "pornpasok"

    }
    
    stages {
        stage('Clean') {
            steps {
                echo 'Clean Workspace'
                sh '''
                    rm -rf *
                '''
                echo 'Clean Demo App'
                sh '''
                    if kubectl get deployment ${APP_NAME} -n ${DEV_PROJECT}; then echo exists && kubectl delete deployment ${APP_NAME} -n ${DEV_PROJECT} && kubectl delete svc ${APP_NAME} -n ${DEV_PROJECT}; else echo no deployment; fi
                '''
            }
        }

        stage('SCM') {
            steps {
                echo 'Pull code from SCM'
                git(
                    url: "${APP_GIT_URL}",
                    //credentialsId: 'github-cicd',
                    branch: "main"
                )
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Build Docker Images'
                sh '''
                    #docker build -t ${DOCKER_USER}/${APP_NAME} .
                    docker build -t ${DOCKER_USER}/${APP_NAME} --network container:\$(docker ps | grep \$(hostname) | grep k8s_POD | cut -d\" \" -f1) .
                '''
            }
        }

        stage('Push Images to Artifactory') {
            steps {
                echo 'Push Images to Artifactory'
                script {
                    withCredentials([usernamePassword(credentialsId: 'nexus', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
                        echo "docker login to ${NEXUS_SERVER}"
                        sh '''
                            export GIT_COMMIT_HASH=$(git log -n 1 --pretty=format:'%h')
                            echo $GIT_COMMIT_HASH
                            export IMAGE_VERSION=${BUILD_NUMBER}-${GIT_COMMIT_HASH}
                            echo "${IMAGE_VERSION}" > version.txt
                        

                            docker login ${NEXUS_SERVER} -u $DOCKER_USER -p $DOCKER_PASSWORD 
                            #docker tag ${DOCKER_USER}/${APP_NAME}:latest ${DOCKER_USER}/${APP_NAME}:${IMAGE_VERSION}
                            docker tag ${DOCKER_USER}/${APP_NAME}:latest ${DOCKER_USER}/${APP_NAME}:latest
                            #docker push ${DOCKER_USER}/${APP_NAME}:${IMAGE_VERSION}
                            docker push ${DOCKER_USER}/${APP_NAME}:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Dev ENV') {
            steps {
                echo 'Deploy to Dev ENV'
                sh '''
                    kubectl create deployment ${APP_NAME} -n ${DEV_PROJECT} --image=${DOCKER_USER}/${APP_NAME}
                '''

            }
        }

        stage('Link Variables to Deployment') {
            steps {
                echo 'Link Variables to Deployment'
                sh '''
                    kubectl set env --from=secret/${APP_NAME} deployment/${APP_NAME} -n ${DEV_PROJECT}
                '''

            }
        }

        stage('Expose Service to Dev ENV') {
            steps {
                echo 'Expose Service to Dev ENV'
                sh '''
                    kubectl expose deployment ${APP_NAME} -n ${DEV_PROJECT} --type=LoadBalancer --port=80 --target-port=${APP_PORT}
                '''

            }
        }

        stage('Scale Demo App') {
            steps {
                echo 'Scale App'
                sh '''
                    kubectl scale deployment ${APP_NAME} -n ${DEV_PROJECT} --replicas=1
                '''
            }
        }

        stage('Get App Endpoint') {
            steps {
                echo 'Get App Endpoint'
                sh '''
                    sleep 30
                    kubectl get service ${APP_NAME} -n ${DEV_PROJECT} | tail -n +2 | awk '{print $4}'
                    ELB_ENDPOINT=$(kubectl get service ${APP_NAME} -n ${DEV_PROJECT} | tail -n +2 | awk '{print $4}')
                    echo "ELB_ENDPOINT: http://$ELB_ENDPOINT"
                '''
            }
        }

        stage('Check Demo App') {
            steps {
                echo 'Check Demo App'
                sh '''
                    sleep 60
                    # ELB
                    ELB_ENDPOINT=$(kubectl get service ${APP_NAME} -n ${DEV_PROJECT} | tail -n +2 | awk '{print $4}')
                    STATUSCODE=$(curl -s -o /dev/null -I -w "%{http_code}" http://$ELB_ENDPOINT)

                    # Service
                    #STATUSCODE=$(curl -s -o /dev/null -I -w "%{http_code}" http://${APP_NAME})
                    if test $STATUSCODE -ne 200; then echo ERROR:$STATUSCODE && exit 1; else echo SUCCESS; fi;
                '''
            }
        }

    }
}