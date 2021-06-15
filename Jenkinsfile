pipeline {
    agent any
    environment {
        APP_GIT_URL = "https://github.com/pornpasok/demo-python-app.git"
        APP_BRANCH = "main"
        APP_TAG = "latest"
        APP_NAME = "demo-python-app"
        APP_PORT = "5000"
        DEV_PROJECT = "default"
        SQ_SERVER = "https://sq.7-11.io"
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
                    branch: "${APP_BRANCH}"
                )
            }
        }

        stage('Source Code Scan SonarQube') {
            steps {
                withCredentials([string(credentialsId: 'sq-token', variable: 'SQ_TOKEN')]) {
                    echo 'Source Code Scan SonarQube'
                    sh '''
                        /sonar-scanner-4.6.2.2472-linux/bin/sonar-scanner \
                        -Dsonar.projectKey="${APP_NAME}" \
                        -Dsonar.sources=. \
                        -Dsonar.host.url="${SQ_SERVER}" \
                        -Dsonar.login="$SQ_TOKEN"
                    '''
                }
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
                    # ELB 
                    #kubectl expose deployment ${APP_NAME} -n ${DEV_PROJECT} --type=LoadBalancer --port=80 --target-port=${APP_PORT}

                    # Default Service
                    kubectl expose deployment ${APP_NAME} -n ${DEV_PROJECT} --port=80 --target-port=${APP_PORT}
                '''

            }
        }

        stage('Create Ingress to Service') {
            steps {
                echo 'Create Ingress to Service'
                sh '''
                    cat <<EOF | kubectl apply -f -
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ${APP_NAME}
  namespace: default
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: ${APP_NAME}.7-11.io
      http:
        paths:
          - backend:
              serviceName: ${APP_NAME}
              servicePort: 80
EOF
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
                    #ELB_ENDPOINT=$(kubectl get service ${APP_NAME} -n ${DEV_PROJECT} | tail -n +2 | awk '{print $4}')
                    #STATUSCODE=$(curl -s -o /dev/null -I -w "%{http_code}" http://$ELB_ENDPOINT)

                    # Service
                    STATUSCODE=$(curl -s -o /dev/null -I -w "%{http_code}" http://${APP_NAME}.${DEV_PROJECT}.svc.cluster.local)
                    if test $STATUSCODE -ne 200; then echo ERROR:$STATUSCODE && exit 1; else echo SUCCESS; fi;
                '''
            }
        }

    }
}