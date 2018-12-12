pipeline {
  agent any

  // using the Timestamper plugin we can add timestamps to the console log
  options {
    timestamps()
  }

  environment {
    //Use Pipeline Utility Steps plugin to read information from pom.xml into env variables
    IMAGE = readMavenPom().getArtifactId()
    VERSION = readMavenPom().getVersion()
  }

  stages {
    stage('Wait for copy completion') {
      options { timeout(time: 30, unit: 'MINUTES') }
      steps {
        echo 'Waiting done'
      }
    }

    stage('Test raw files') {
      steps {
        echo 'Files tested'
      }
    }

    stage('Organize files by takes') {
      steps {
        echo 'Files made read-only'
        echo 'Symlinks created'
      }
    }

    stage('Rough stitch') {
      steps {
        echo 'Rough stitched'
      } 
    }

    stage('Add timecodes') {
      steps {
        echo 'Timecode burnt in'
      } 
    }

    stage('Generate WonderStitch batch') {
      steps {
        echo 'WS batch file generated'
      } 
    }
  }
  
}