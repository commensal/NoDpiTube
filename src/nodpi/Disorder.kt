package com.liskovsoft.smartyoutubetv2.common.nodpi

import android.os.Build
import android.os.ParcelFileDescriptor
import android.system.Os
import android.system.OsConstants
import java.io.FileDescriptor
import java.net.Socket

/**
 * Disorder: the first segment is sent with TTL = 1, so it dies on the first hop before
 * reaching DPI/TSPU, then the rest is sent normally. The kernel retransmits the first segment
 * later with the restored TTL, so DPI sees the stream out of order and fails to match SNI.
 */
object Disorder {

    private const val LOW_TTL = 1
    private const val DEFAULT_TTL = -1
    private const val SETTLE_MS = 15L

    fun send(socket: Socket, first: ByteArray, rest: ByteArray) {
        val out = socket.getOutputStream()
        socket.tcpNoDelay = true

        // setsockopt via ParcelFileDescriptor requires Android 5.0+ (API 21+)
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            out.write(first)
            out.write(rest)
            out.flush()
            return
        }

        val dup = runCatching { ParcelFileDescriptor.fromSocket(socket) }.getOrNull()
        if (dup == null) {
            out.write(first)
            out.write(rest)
            out.flush()
            return
        }

        dup.use {
            val fd = it.fileDescriptor
            setTtl(fd, LOW_TTL)
            try {
                out.write(first)
                out.flush()
                Thread.sleep(SETTLE_MS)
            } finally {
                // -1 restores the system default TTL / hop limit
                setTtl(fd, DEFAULT_TTL)
            }
        }

        out.write(rest)
        out.flush()
    }

    private fun setTtl(fd: FileDescriptor, value: Int) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            runCatching {
                Os.setsockoptInt(fd, OsConstants.IPPROTO_IP, OsConstants.IP_TTL, value)
            }
            runCatching {
                Os.setsockoptInt(fd, OsConstants.IPPROTO_IPV6, OsConstants.IPV6_UNICAST_HOPS, value)
            }
        }
    }
}
