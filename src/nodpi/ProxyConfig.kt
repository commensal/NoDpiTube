package com.liskovsoft.smartyoutubetv2.common.nodpi

/** Configuration of the embedded NoDPI proxy server */
data class ProxyConfig(
    val host: String = DEFAULT_HOST,
    val port: Int = DEFAULT_PORT,
    val disorder: Boolean = true,
) {
    companion object {
        const val DEFAULT_HOST = "127.0.0.1"
        const val DEFAULT_PORT = 8881
    }
}
