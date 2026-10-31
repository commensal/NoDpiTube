package com.liskovsoft.smartyoutubetv2.common.nodpi

import android.util.Log
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.EOFException
import java.io.IOException
import java.io.InputStream
import java.io.SequenceInputStream
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Proxy
import java.net.ServerSocket
import java.net.Socket
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.atomic.AtomicInteger

/**
 * Embedded HTTP/HTTPS CONNECT proxy server for SmartTube.
 * Intercepts TLS ClientHello on port 443, detects SNI, fragments the packet,
 * and sends it with disorder (TTL=1 on first chunk) to bypass DPI filters.
 */
class ProxyServer(
    private val config: ProxyConfig = ProxyConfig(),
    private val blacklist: Blacklist = YouTubeBlacklist(),
) {

    private val executor: ExecutorService = Executors.newCachedThreadPool { task ->
        Thread(task, "nodpi-tube-proxy").apply { isDaemon = true }
    }
    private val sockets = ConcurrentHashMap.newKeySet<Socket>()

    @Volatile
    private var serverSocket: ServerSocket? = null

    @Volatile
    private var running = false

    @Volatile
    var actualPort: Int = config.port
        private set

    fun start() {
        if (running) return

        var server: ServerSocket? = null
        var portToTry = config.port

        try {
            server = ServerSocket()
            server.reuseAddress = true
            server.bind(InetSocketAddress(InetAddress.getByName(config.host), portToTry), BACKLOG)
        } catch (e: IOException) {
            Log.w(TAG, "Port $portToTry is busy/unavailable. Binding to dynamic free port 0...")
            runCatching { server?.close() }
            server = ServerSocket()
            server.reuseAddress = true
            server.bind(InetSocketAddress(InetAddress.getByName(config.host), 0), BACKLOG)
            portToTry = server.localPort
        }

        val boundServer = server ?: return
        actualPort = portToTry
        serverSocket = boundServer
        running = true
        Log.i(TAG, "NoDPI proxy successfully started on ${config.host}:$actualPort")
        executor.execute { acceptLoop(boundServer) }
    }

    fun stop() {
        running = false
        runCatching { serverSocket?.close() }
        sockets.forEach { runCatching { it.close() } }
        sockets.clear()
        executor.shutdownNow()
        Log.i(TAG, "NoDPI proxy stopped")
    }

    private fun acceptLoop(server: ServerSocket) {
        while (running && !server.isClosed) {
            val client = try {
                server.accept()
            } catch (_: IOException) {
                continue
            }
            sockets += client
            try {
                executor.execute { handleConnection(client) }
            } catch (_: RejectedExecutionException) {
                close(client)
            }
        }
    }

    private fun handleConnection(client: Socket) {
        var remote: Socket? = null
        try {
            client.tcpNoDelay = true
            client.soTimeout = REQUEST_TIMEOUT_MS
            val clientIn = client.getInputStream()

            val head = readRequestHead(clientIn)
            if (head == null) {
                close(client)
                return
            }
            val request = HttpRequest.parse(head.bytes, head.headerEnd)

            if (request.isConnect) {
                remote = connectRemote(request.host, request.port)

                client.getOutputStream().write(CONNECTION_ESTABLISHED)
                client.getOutputStream().flush()

                val leftover = head.bytes.copyOfRange(head.headerEnd, head.bytes.size)
                val tunnelIn = if (leftover.isEmpty()) clientIn else SequenceInputStream(ByteArrayInputStream(leftover), clientIn)

                client.soTimeout = 0
                if (!sendInitialTlsData(tunnelIn, remote, request.host)) {
                    close(remote)
                    close(client)
                    return
                }
                pipeBothWays(client, tunnelIn, remote)
            } else {
                remote = connectRemote(request.host, request.port)
                remote.getOutputStream().write(head.bytes)
                remote.getOutputStream().flush()

                client.soTimeout = 0
                pipeBothWays(client, clientIn, remote)
            }
        } catch (e: Exception) {
            handleConnectionError(client, remote, e)
        }
    }

    private fun sendInitialTlsData(input: InputStream, remote: Socket, host: String): Boolean {
        val first = input.read()
        if (first < 0) {
            return false
        }

        val header = ByteArray(TlsFragmenter.RECORD_HEADER_SIZE)
        header[0] = first.toByte()
        readFully(input, header, 1, header.size - 1)
        val out = remote.getOutputStream()

        if (header[0] != TlsFragmenter.HANDSHAKE_CONTENT_TYPE) {
            out.write(header)
            out.flush()
            return true
        }

        val length = ((header[3].toInt() and 0xFF) shl 8) or (header[4].toInt() and 0xFF)
        val body = ByteArray(length)
        readFully(input, body, 0, length)

        val blocked = blacklist.isBlocked(host)
        val cloudflare = blocked && CloudflareRanges.contains(remote.inetAddress)

        if (!blocked || cloudflare) {
            val record = header + body
            out.write(record)
            out.flush()
            return true
        }

        val parts = TlsFragmenter.fragment(header, body)
        if (config.disorder && parts.size > 2) {
            Disorder.send(remote, parts[0] + parts[1], parts.subList(2, parts.size).join())
        } else {
            out.write(parts.join())
            out.flush()
        }

        return true
    }

    private fun pipeBothWays(client: Socket, clientIn: InputStream, remote: Socket) {
        val pipes = AtomicInteger(2)
        try {
            executor.execute { pipe(remote.getInputStream(), remote, client, pipes) }
        } catch (e: RejectedExecutionException) {
            close(remote)
            close(client)
            return
        }
        pipe(clientIn, client, remote, pipes)
    }

    private fun pipe(input: InputStream, source: Socket, target: Socket, pipes: AtomicInteger) {
        val buffer = ByteArray(BUFFER_SIZE)
        try {
            val out = target.getOutputStream()
            while (true) {
                val read = input.read(buffer)
                if (read < 0) break
                out.write(buffer, 0, read)
                out.flush()
            }
        } catch (_: IOException) {
        } finally {
            close(target)
            if (pipes.decrementAndGet() == 0) {
                close(source)
            }
        }
    }

    private fun handleConnectionError(client: Socket, remote: Socket?, error: Exception) {
        if (running) {
            try {
                client.getOutputStream().write(INTERNAL_ERROR)
                client.getOutputStream().flush()
            } catch (_: IOException) {
            }
        }
        remote?.let(::close)
        close(client)
    }

    private fun connectRemote(host: String, port: Int): Socket {
        val socket = Socket(Proxy.NO_PROXY)
        sockets += socket
        try {
            socket.tcpNoDelay = true
            socket.connect(InetSocketAddress(host, port), CONNECT_TIMEOUT_MS)
        } catch (e: IOException) {
            close(socket)
            throw e
        }
        return socket
    }

    private fun close(socket: Socket) {
        sockets -= socket
        runCatching { socket.close() }
    }

    private class RequestHead(val bytes: ByteArray, val headerEnd: Int)

    companion object {
        private const val TAG = "NoDpiProxy"
        private const val BACKLOG = 128
        private const val BUFFER_SIZE = 32 * 1024
        private const val MAX_HEAD_SIZE = 64 * 1024
        private const val REQUEST_TIMEOUT_MS = 60_000
        private const val CONNECT_TIMEOUT_MS = 15_000

        private val CONNECTION_ESTABLISHED = "HTTP/1.1 200 Connection Established\r\n\r\n".toByteArray()
        private val INTERNAL_ERROR = "HTTP/1.1 500 Internal Server Error\r\n\r\n".toByteArray()
        private val HEADER_END = "\r\n\r\n".toByteArray()

        private fun readRequestHead(input: InputStream): RequestHead? {
            val buffer = ByteArrayOutputStream()
            val chunk = ByteArray(4096)
            while (buffer.size() < MAX_HEAD_SIZE) {
                val read = input.read(chunk)
                if (read < 0) break
                buffer.write(chunk, 0, read)
                val bytes = buffer.toByteArray()
                val end = indexOf(bytes, HEADER_END)
                if (end >= 0) {
                    return RequestHead(bytes, end + HEADER_END.size)
                }
            }
            val bytes = buffer.toByteArray()
            return if (bytes.isEmpty()) null else RequestHead(bytes, bytes.size)
        }

        private fun readFully(input: InputStream, target: ByteArray, offset: Int, length: Int) {
            var done = 0
            while (done < length) {
                val read = input.read(target, offset + done, length - done)
                if (read < 0) throw EOFException("Connection closed after $done of $length bytes")
                done += read
            }
        }

        private fun indexOf(data: ByteArray, pattern: ByteArray): Int {
            outer@ for (i in 0..data.size - pattern.size) {
                for (j in pattern.indices) {
                    if (data[i + j] != pattern[j]) continue@outer
                }
                return i
            }
            return -1
        }
    }
}

/** First line and headers of a proxy request */
internal class HttpRequest(
    val method: String,
    val host: String,
    val port: Int,
    private val headers: List<String>,
) {
    val isConnect: Boolean get() = method == "CONNECT"

    companion object {
        fun parse(bytes: ByteArray, headerEnd: Int): HttpRequest {
            val lines = String(bytes, 0, headerEnd, Charsets.ISO_8859_1).split("\r\n")
            val first = lines[0].split(' ')
            require(first.size >= 2) { "Malformed request line" }
            val method = first[0]
            val headers = lines.drop(1).filter { it.isNotEmpty() }

            if (method == "CONNECT") {
                val (host, port) = splitHostPort(first[1], 443)
                return HttpRequest(method, host, port, headers)
            }

            val hostHeader = headers.firstOrNull { it.startsWith("host:", ignoreCase = true) }
                ?.substring(5)?.trim()
                ?: throw IllegalArgumentException("Missing Host header")
            val (host, port) = splitHostPort(hostHeader, 80)
            return HttpRequest(method, host, port, headers)
        }

        fun splitHostPort(value: String, defaultPort: Int): Pair<String, Int> {
            if (value.startsWith("[")) {
                val close = value.indexOf(']')
                require(close > 0) { "Malformed host: $value" }
                val host = value.substring(1, close)
                val port = value.substring(close + 1).removePrefix(":").toIntOrNull() ?: defaultPort
                return host to port
            }
            val colon = value.lastIndexOf(':')
            if (colon < 0 || value.indexOf(':') != colon) {
                return value to defaultPort
            }
            return value.substring(0, colon) to (value.substring(colon + 1).toIntOrNull() ?: defaultPort)
        }
    }
}
