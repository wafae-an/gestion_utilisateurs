pipeline {
    agent any

    environment {
        IMAGE_NAME = "service_users"
        IMAGE_TAG = "latest"
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

        stage('Build Docker Image') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DOCKERHUB_USERNAME', variable: 'DOCKER_USER')
                    ]) {
                        echo "Building Docker image as ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
                        
                        bat """
                            echo ===== BUILDING DOCKER IMAGE =====
                            docker build -t %DOCKER_USER%/${IMAGE_NAME}:${IMAGE_TAG} ./service_users
                            echo Docker images after build:
                            docker images | findstr "%DOCKER_USER%"
                        """
                    }
                }
            }
        }

        stage('Login Docker Hub') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DOCKERHUB_USERNAME', variable: 'DOCKER_USER'),
                        string(credentialsId: 'DOCKERHUB_TOKEN', variable: 'DOCKER_PASS')
                    ]) {
                        echo "Logging into Docker Hub as ${DOCKER_USER}"
                        
                        bat """
                            echo ===== LOGGING INTO DOCKER HUB =====
                            echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                            
                            if %errorlevel% neq 0 (
                                echo ERROR: Docker login failed!
                                exit 1
                            )
                            
                            echo Docker Hub login successful!
                        """
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DOCKERHUB_USERNAME', variable: 'DOCKER_USER')
                    ]) {
                        echo "Pushing image to Docker Hub..."
                        
                        bat """
                            echo ===== PUSHING DOCKER IMAGE =====
                            docker push %DOCKER_USER%/${IMAGE_NAME}:${IMAGE_TAG}
                            
                            if %errorlevel% neq 0 (
                                echo ERROR: Docker push failed!
                                exit 1
                            )
                            
                            echo Image pushed successfully to Docker Hub!
                        """
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withCredentials([
                        file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG_FILE')
                    ]) {
                        echo "Deploying to Kubernetes..."
                        
                        bat """
                            echo ===== DEPLOYING TO KUBERNETES =====
                            echo Kubeconfig file: %KUBECONFIG_FILE%
                            
                            set KUBECONFIG=%KUBECONFIG_FILE%
                            
                            echo Kubernetes cluster info:
                            kubectl cluster-info
                            
                            echo Applying deployment...
                            kubectl apply -f ./service_users/k8s/deploy.yml --dry-run=client
                            kubectl apply -f ./service_users/k8s/deploy.yml
                            
                            echo Applying service...
                            kubectl apply -f ./service_users/k8s/service.yml --dry-run=client
                            kubectl apply -f ./service_users/k8s/service.yml
                            
                            echo Current deployments:
                            kubectl get deployments -o wide
                            
                            echo Current services:
                            kubectl get services -o wide
                            
                            echo Deployment completed successfully!
                        """
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    withCredentials([
                        file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG_FILE')
                    ]) {
                        bat """
                            set KUBECONFIG=%KUBECONFIG_FILE%
                            
                            echo ===== VERIFYING DEPLOYMENT =====
                            echo Waiting for pods to be ready...
                            
                            timeout /t 30 /nobreak
                            
                            echo Pods status:
                            kubectl get pods -o wide
                            
                            echo Pods details:
                            kubectl describe pods --selector=app=service-users
                            
                            echo Service details:
                            kubectl describe service service-users
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline execution completed"
            
            bat """
                echo ===== CLEANUP =====
                docker logout 2>nul || echo "Already logged out or login failed"
                echo Cleanup done.
            """
        }
        success {
            echo "✅ Pipeline succeeded!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
