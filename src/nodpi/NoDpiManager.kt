package com.liskovsoft.smartyoutubetv2.common.nodpi

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.liskovsoft.smartyoutubetv2.common.proxy.PasswdInetSocketAddress
import com.liskovsoft.smartyoutubetv2.common.proxy.Proxy
import com.liskovsoft.smartyoutubetv2.common.proxy.ProxyManager

/**
 * High-level manager for the built-in NoDPI engine in SmartTube.
 * Responsible for starting the proxy daemon at app launch, selecting a free port,
 * and configuring system properties and Chromium Cronet.
 */
object NoDpiManager {
    private const val TAG = "NoDpiManager"
    const val PROXY_HOST = "127.0.0.1"
    const val DEFAULT_PORT = 8881
    const val PREFS = "nodpitube"
    const val KEY_MODE = "bypass_mode"

    @Volatile
    private var proxyServer: ProxyServer? = null

    @Volatile
    private var isStarted = false

    @Volatile
    var allocatedPort = DEFAULT_PORT
        private set

    @JvmStatic
    fun start(context: Context) {
        if (isStarted) {
            return
        }

        synchronized(this) {
            if (isStarted) return

            try {
                // 1. Start proxy server; dynamically assigns port if 8881 is taken
                val saved = BypassMode.fromId(prefs(context).getInt(KEY_MODE, BypassMode.SNI_DISORDER.id))
                val server = ProxyServer(
                    config = ProxyConfig(
                        host = PROXY_HOST,
                        port = DEFAULT_PORT,
                        mode = saved
                    ),
                    blacklist = YouTubeBlacklist()
                )

                server.start()
                allocatedPort = server.actualPort
                proxyServer = server
                isStarted = true

                // 2. Set global HTTP/HTTPS proxy properties for Java / OkHttp / HttpURLConnection
                System.setProperty("http.proxyHost", PROXY_HOST)
                System.setProperty("http.proxyPort", allocatedPort.toString())
                System.setProperty("https.proxyHost", PROXY_HOST)
                System.setProperty("https.proxyPort", allocatedPort.toString())

                // 3. Configure SmartTube ProxyManager & Chromium Cronet via broadcast
                try {
                    val proxyAddr = PasswdInetSocketAddress.createUnresolved(PROXY_HOST, allocatedPort, null, null)
                    val proxyObj = Proxy(Proxy.Type.HTTP, proxyAddr)
                    val pm = ProxyManager(context)
                    pm.saveProxyInfoToPrefs(proxyObj, true)
                    pm.configureSystemProxy()
                } catch (t: Throwable) {
                    Log.e(TAG, "ProxyManager configuration error", t)
                }

                Log.i(TAG, "NoDPI Engine fully active on $PROXY_HOST:$allocatedPort")
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
    fun getMode(context: Context): BypassMode {
        return proxyServer?.mode ?: BypassMode.fromId(prefs(context).getInt(KEY_MODE, BypassMode.SNI_DISORDER.id))
    }

    /** Applies to the next connection. An already open video has to be started again. */
    @JvmStatic
    fun setMode(context: Context, mode: BypassMode) {
        prefs(context).edit().putInt(KEY_MODE, mode.id).apply()
        proxyServer?.mode = mode
        Log.i(TAG, "Bypass mode set to ${mode.name}")
    }

    private fun prefs(context: Context): SharedPreferences {
        return context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
    }

    @JvmStatic
    fun getProxyHost(): String = PROXY_HOST

    @JvmStatic
    fun getProxyPort(): Int = allocatedPort
}
