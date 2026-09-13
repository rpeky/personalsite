pipeline {
    agent {
        label 'pekyserver'
    }

    options {
        timestamps()
        disableConcurrentBuilds()

        buildDiscarder(
            logRotator(
                numToKeepStr: '20',
                artifactNumToKeepStr: '5'
            )
        )
    }

    environment {
        SITE_HOST = '10.10.70.100'
        SITE_ROOT = '/var/www/ryanpek'

        CADDY_HOST = '10.10.70.200'
        PUBLIC_DOMAIN = 'ryanpek.com'
    }

    stages {
        // --------------------------------------------------------------------
        // Source
        // --------------------------------------------------------------------

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // --------------------------------------------------------------------
        // Build
        // --------------------------------------------------------------------

        stage('Build') {
            steps {
                sh '''
                    set -eu

                    make clean
                    make build
                '''
            }
        }

        // --------------------------------------------------------------------
        // Validate generated site
        // --------------------------------------------------------------------

        stage('Validate') {
            steps {
                sh '''
                    set -eu

                    test -d site
                    test -s site/index.html
                    test -s site/about.html
                    test -s site/projects.html

                    if find site -xtype l | grep -q .; then
                        echo "Broken symlinks found:"
                        find site -xtype l
                        exit 1
                    fi

                    echo "Generated site:"
                    du -sh site
                    find site -type f | sort
                '''
            }
        }

        // --------------------------------------------------------------------
        // Archive generated site
        // --------------------------------------------------------------------

        stage('Archive') {
            steps {
                sh '''
                    set -eu

                    tar -czf personalsite.tar.gz -C site .
                '''

                archiveArtifacts(
                    artifacts: 'personalsite.tar.gz',
                    fingerprint: true
                )
            }
        }

        // --------------------------------------------------------------------
        // Deploy to personalsite-01
        // --------------------------------------------------------------------

        stage('Deploy') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'personalsite-deploy-ssh',
                        keyFileVariable: 'SITE_SSH_KEY',
                        usernameVariable: 'SITE_SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu

                        mkdir -p .jenkins-ssh
                        chmod 700 .jenkins-ssh

                        ssh-keyscan -H "$SITE_HOST" \
                            > .jenkins-ssh/known_hosts

                        chmod 600 .jenkins-ssh/known_hosts

                        rsync \
                            --archive \
                            --compress \
                            --delete \
                            --itemize-changes \
                            -e "ssh \
                                -i $SITE_SSH_KEY \
                                -o IdentitiesOnly=yes \
                                -o StrictHostKeyChecking=yes \
                                -o UserKnownHostsFile=$WORKSPACE/.jenkins-ssh/known_hosts" \
                            site/ \
                            "$SITE_SSH_USER@$SITE_HOST:$SITE_ROOT/"
                    '''
                }
            }
        }

        // --------------------------------------------------------------------
        // Verify nginx directly
        // --------------------------------------------------------------------

        stage('Verify Backend') {
            steps {
                sh '''
                    set -eu

                    curl \
                        --fail \
                        --silent \
                        --show-error \
                        --output /dev/null \
                        "http://$SITE_HOST/"
                '''
            }
        }

        // --------------------------------------------------------------------
        // Verify Caddy -> nginx
        //
        // This bypasses public DNS and the VPS while still using ryanpek.com
        // as the TLS SNI/HTTP Host.
        // --------------------------------------------------------------------

        stage('Verify Caddy') {
            steps {
                sh '''
                    set -eu

                    curl \
                        --fail \
                        --silent \
                        --show-error \
                        --resolve "$PUBLIC_DOMAIN:443:$CADDY_HOST" \
                        --output /dev/null \
                        "https://$PUBLIC_DOMAIN/"
                '''
            }
        }

        // --------------------------------------------------------------------
        // Enable after ryanpek.com points to the VPS
        // --------------------------------------------------------------------

        /*
        stage('Verify Public') {
            steps {
                sh '''
                    set -eu

                    curl \
                        --fail \
                        --silent \
                        --show-error \
                        --output /dev/null \
                        "https://$PUBLIC_DOMAIN/"
                '''
            }
        }
        */
    }

    post {
        success {
            echo 'Personal site deployed successfully.'
        }

        failure {
            echo 'Personal site deployment failed.'
        }

        always {
            sh '''
                rm -rf .jenkins-ssh || true
            '''
        }
    }
}
