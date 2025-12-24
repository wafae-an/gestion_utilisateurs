pipeline {
    agent any

    environment {
        IMAGE_NAME = "service_users"
        IMAGE_TAG  = "latest"
        NAMESPACE  = "dev"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: 'main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/wafae-an/gestion_utilisateurs.git'
                    ]]
                ])
                bat 'dir /s /b *.yml *.yaml Dockerfile'
            }
        }

        stage('Prepare Namespace') {
            steps {
                withCredentials([file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG_FILE')]) {
                    bat """
                        set KUBECONFIG=%KUBECONFIG_FILE%
                        kubectl create namespace %NAMESPACE% --dry-run=client -o yaml ^| kubectl apply -f -
                        kubectl get namespaces
                    """
                }
            }
        }

        stage('Deploy MySQL Database') {
            steps {
                withCredentials([file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG_FILE')]) {
                    bat """
                        set KUBECONFIG=%KUBECONFIG_FILE%

                        echo Deploying MySQL...
                        kubectl apply -n %NAMESPACE% -f deploiementSQL/deploy_sql.yml
                        kubectl apply -n %NAMESPACE% -f deploiementSQL/service_sql.yml

                        echo Waiting for MySQL to be READY...
                        kubectl wait --for=condition=Ready pod -l app=mysql -n %NAMESPACE% --timeout=180s

                        kubectl get pods -n %NAMESPACE% -l app=mysql
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                withCredentials([string(credentialsId: 'DOCKERHUB_USERNAME', variable: 'DOCKER_USER')]) {
                    bat """
                        echo BUILDING IMAGE
                        docker build -t %DOCKER_USER%/%IMAGE_NAME%:%IMAGE_TAG% ./service_users
                        docker images | findstr "%DOCKER_USER%"
                    """
                }
            }
        }

        stage('Login Docker Hub') {
            steps {
                withCredentials([
                    string(credentialsId: 'DOCKERHUB_USERNAME', variable: 'DOCKER_USER'),
                    string(credentialsId: 'DOCKERHUB_TOKEN', variable: 'DOCKER_PASS')
                ]) {
                    bat """
                        echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([string(credentialsId: 'DOCKERHUB_USERNAME', variable: 'DOCKER_USER')]) {
                    bat """
                        docker push %DOCKER_USER%/%IMAGE_NAME%:%IMAGE_TAG%
                    """
                }
            }
        }

        stage('Deploy Application to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG_FILE')]) {
                    bat """
                        set KUBECONFIG=%KUBECONFIG_FILE%

                        echo Deploying application...
                        kubectl apply -n %NAMESPACE% -f ./service_users/k8s/deploy.yml
                        kubectl apply -n %NAMESPACE% -f ./service_users/k8s/service.yml

                        kubectl get deployments -n %NAMESPACE%
                        kubectl get services -n %NAMESPACE%
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withCredentials([file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG_FILE')]) {
                    bat """
                        set KUBECONFIG=%KUBECONFIG_FILE%

                        echo Verifying pods...
                        kubectl wait --for=condition=Ready pod -l app=fastapi -n %NAMESPACE% --timeout=120s

                        kubectl get pods -n %NAMESPACE% -o wide
                        kubectl describe service service-users -n %NAMESPACE%
                    """
                }
            }
        }
    }

    post {
        always {
            bat 'docker logout || echo Already logged out'
        }
        success {
            echo "Pipeline completed successfully"
        }
        failure {
            echo "Pipeline failed — check logs"
        }
    }
}
