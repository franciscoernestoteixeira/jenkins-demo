pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    parameters {
        gitParameter branchFilter: '.*', defaultValue: 'main', name: 'BRANCH', type: 'PT_BRANCH_TAG', sortMode: 'DESCENDING_SMART'
        choice(name: 'ENVIRONMENT', choices: ['staging', 'production'], description: 'Environment to run')
    }

    stages {
        stage('Install dependencies and test') {
            agent {
                docker {
                    image 'python:3.13.3-alpine3.21'
                    args '-u root:root'
                }
            }

            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest
                '''
            }
        }

//         stage('Build image') {
//             agent {
//                 docker {
//                     image 'python:3.13.3-alpine3.21'
//                     args '-u root:root'
//                 }
//             }
//
//             steps {
//                 sh 'docker build -t jenkins-demo .'
//             }
//         }

        stage('Upload Build Artifacts to Servers and Deploy') {
            agent {
                docker {
                    image 'python:3.13.3-alpine3.21'
                    args '-u root:root'
                }
            }

            steps {
                script {
                    echo "Installing deployment dependencies..."
                    sh 'apk add --no-cache lftp openssh-client'

                    def artifact = 'release.tar.gz'
                    sh "tar --exclude='.git' --exclude='.venv' --exclude='.idea' --exclude='__pycache__' --exclude='.pytest_cache' -czf ${artifact} ."

                    echo "Environment: ${params.ENVIRONMENT}"

                    if (params.ENVIRONMENT == 'staging')
                    {
                        echo 'TODO send to staging environment'
                    }
                    else if (params.ENVIRONMENT == 'production')
                    {
                        def remoteServers = [
                            [label: "servidor-destino", host: "admin@56.124.12.216", credential: "servidor_destino"]
                        ]

                        remoteServers.each { entry ->
                            sshagent(credentials: [entry.credential]) {
                                echo "Deploying to ${entry.label}..."

                                echo "Uploading to ${entry.host}..."
                                sh "scp -o StrictHostKeyChecking=no ${artifact} ${entry.host}:/tmp/"

                                echo "Stopping API on ${entry.host}..."
                                def isRunning = sh(
                                    script: "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'pgrep -f uvicorn'",
                                    returnStatus: true
                                )

                                if (isRunning == 0) {
                                    echo "Stopping uvicorn..."
                                    sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo pkill -f uvicorn'"
                                } else {
                                    echo "uvicorn is not running."
                                }

                                echo "Cleaning old deployment on ${entry.host}..."
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo rm -rf /opt/jenkins-demo'"

                                echo "Creating final directory on ${entry.host}..."
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo mkdir -p /opt/jenkins-demo'"

                                echo "Extracting package on ${entry.host}..."
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo tar -xzf /tmp/${artifact} -C /opt/jenkins-demo'"

                                echo "Removing remote artifact ${artifact} on ${entry.host}..."
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo rm -f /tmp/${artifact}'"

                                echo "Fixing permissions on ${entry.host}..."
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo chown -R admin:admin /opt/jenkins-demo'"

                                echo "Starting API on ${entry.host}..."
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'cd /opt/jenkins-demo && python3 -m venv .venv'"
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} '. /opt/jenkins-demo/.venv/bin/activate'"
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} '/opt/jenkins-demo/.venv/bin/pip install --upgrade pip'"
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} '/opt/jenkins-demo/.venv/bin/pip install -r /opt/jenkins-demo/requirements.txt'"
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'chmod +x /opt/jenkins-demo/start.sh'"
                                sh "ssh -T -o StrictHostKeyChecking=no ${entry.host} 'sudo bash -c \'/opt/jenkins-demo/start.sh\''"
                            }
                        }
                    }

                    echo "Removing local artifact ${artifact}..."
                    sh "rm -f ${artifact}"
                }
            }
        }

        stage('Cleanup') {
            agent {
                docker {
                    image 'python:3.13.3-alpine3.21'
                    args '-u root:root'
                }
            }

            steps {
                sh 'rm -rf .venv'
            }
        }
    }

    post {
        always {
            deleteDir()
        }
    }
}