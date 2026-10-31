package com.liskovsoft.smartyoutubetv2.common.nodpi

import android.content.Context
import android.util.Log

/**
 * High-level manager for the built-in NoDPI engine in SmartTube.
 * Responsible for starting the proxy daemon at app launch and configuring system properties.
 */
object NoDpiManager {
    private const val TAG = "NoDpiManager"
    const val PROXY_HOST = "127.0.0.1"
    const val PROXY_PORT = 8881

    @Volatile
    private var proxyServer: ProxyServer? = null

    @Volatile
    private var isStarted = false

    @JvmStatic
    fun start(context: Context) {
        if (isStarted) {
            return
        }

        synchronized(this) {
            if (isStarted) return

            try {
                // 1. Set global HTTP/HTTPS proxy properties for Java / OkHttp / HttpURLConnection
                System.setProperty("http.proxyHost", PROXY_HOST)
                System.setProperty("http.proxyPort", PROXY_PORT.toString())
                System.setProperty("https.proxyHost", PROXY_HOST)
                System.setProperty("https.proxyPort", PROXY_PORT.toString())

                // 2. Start proxy server on background daemon thread
                val server = ProxyServer(
                    config = ProxyConfig(
                        host = PROXY_HOST,
                        port = PROXY_PORT,
                        disorder = true
                    ),
                    blacklist = YouTubeBlacklist()
                )

                Thread({
                    try {
                        server.start()
                    } catch (e: Exception) {
                        Log.e(TAG, "Failed to start NoDPI proxy server", e)
                    }
                }, "nodpi-launcher-thread").apply {
                    isDaemon = true
                    start()
                }

                proxyServer = server
                isStarted = true
                Log.i(TAG, "NoDPI Engine initialized on $PROXY_HOST:$PROXY_PORT")
            } catch (e: Throwable) {
                Log.e(TAG, "Error initializing NoDPI Engine", e)
            }
        }
    }

    @JvmStatic
    fun stop() {
        synchronized(this) {
            proxyServer?.stop()
            proxyServer = null
            isStarted = false

            System.clearProperty("http.proxyHost")
            System.clearProperty("http.proxyPort")
            System.clearProperty("https.proxyHost")
            System.clearProperty("https.proxyPort")
        }
    }

    @JvmStatic
    fun isRunning(): Boolean = isStarted

    @JvmStatic
    fun getProxyHost(): String = PROXY_HOST

    @JvmStatic
    fun getProxyPort(): Int = PROXY_PORT
}
