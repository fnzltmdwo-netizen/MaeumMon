plugins {
    id("com.android.application")
}

android {
    namespace = "com.seungjae.dangifreepass"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.seungjae.dangifreepass"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    lint {
        abortOnError = true
        checkReleaseBuilds = false
    }
}
