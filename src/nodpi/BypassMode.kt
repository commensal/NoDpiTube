package com.liskovsoft.smartyoutubetv2.common.nodpi

/**
 * One bypass is applied to a connection. They are alternatives, not layers.
 *
 * 1. SNI split into 2-byte records, first piece sent with TTL=1. Usually enough.
 * 2. The same split without TTL. Some providers drop TTL=1 itself.
 * 3. Random 1-byte records, closer to the original nodpi script.
 */
enum class BypassMode(val id: Int) {
    SNI_DISORDER(1),
    SNI_ONLY(2),
    BYTE_SPLIT(3);

    companion object {
        fun fromId(id: Int): BypassMode = values().firstOrNull { it.id == id } ?: SNI_DISORDER
    }
}
