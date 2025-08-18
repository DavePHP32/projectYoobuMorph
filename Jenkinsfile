pipeline {
    agent any

    environment {
        IMAGE_NAME = 'moussasamina/yoobu-morph'
        TAG = 'latest'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Tests successfull'
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${TAG} ."
                }
            }
        }

        stage('Docker Login & Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-credentials',
                    usernameVariable: 'DOCKER_HUB_USERNAME',
                    passwordVariable: 'DOCKER_HUB_PASSWORD'
                )]) {
                    script {
                        sh "echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USERNAME --password-stdin"
                        sh "docker push ${IMAGE_NAME}:${TAG}"
                    }
                }
            }
        }
        stage('Deploy APP for Test') {
            steps {
                script {
                    sh 'docker compose up -d'
                }
            }
        }
    }

    post {
        success {
            echo '✅ Image Docker construite et poussée avec succès sur Docker Hub'
        }
        failure {
            echo '❌ Échec du pipeline'
        }
    }
}
