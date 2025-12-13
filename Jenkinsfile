pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "${DOCKERHUB_USERNAME}/service_users:latest"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/wafae-an/gestion_utilisateurs.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $DOCKER_IMAGE ./service_users"
            }
        }

        stage('Login Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USERNAME', passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    sh 'echo $DOCKERHUB_TOKEN | docker login -u $DOCKERHUB_USERNAME --password-stdin'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh "docker push $DOCKER_IMAGE"
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'KUBCONFIG', variable: 'KUBECONFIG')]) {
                    sh "kubectl apply -f ./service_users/k8s/deploy.yml"
                    sh "kubectl apply -f ./service_users/k8s/service.yml"
                }
            }
        }
    }
}
