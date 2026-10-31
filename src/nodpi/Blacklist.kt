package com.liskovsoft.smartyoutubetv2.common.nodpi

/** Decides whether ClientHello for a domain must be fragmented */
interface Blacklist {
    fun isBlocked(domain: String): Boolean
}

/** Default YouTube & Google CDN blacklist for DPI circumvention */
class YouTubeBlacklist(
    customDomains: Iterable<String> = emptyList()
) : Blacklist {

    private val defaultDomains = setOf(
        "googlevideo.com",
        "youtube.com",
        "ytimg.com",
        "youtu.be",
        "ggpht.com",
        "googleapis.com",
        "gvt1.com",
        "googleusercontent.com",
        "youtube-nocookie.com",
        "youtube-ui.l.google.com",
        "yt3.ggpht.com",
        "yt4.ggpht.com",
        "ytimg.l.google.com",
        "wide-youtube.l.google.com"
    )

    private val blocked: Set<String> = (defaultDomains + customDomains)
        .mapNotNull { normalizeDomain(it) }
        .toSet()

    override fun isBlocked(domain: String): Boolean {
        val name = normalizeDomain(domain) ?: return false

        if (name in blocked) {
            return true
        }

        var dot = name.indexOf('.')
        while (dot >= 0) {
            if (name.substring(dot + 1) in blocked) {
                return true
            }
            dot = name.indexOf('.', dot + 1)
        }

        return false
    }

    private fun normalizeDomain(raw: String): String? {
        var name = raw.trim().lowercase()
        if (name.length < 2 || name.startsWith("#")) {
            return null
        }

        name = name.substringAfter("://")
            .substringBefore('/')
            .substringBefore('?')
            .removePrefix("*.")
            .removePrefix("www.")

        if (!name.startsWith("[") && name.count { it == ':' } == 1) {
            name = name.substringBefore(':')
        }

        name = name.trim('.')

        if (name.length < 2 || name.any { it.isWhitespace() || it == '#' }) {
            return null
        }
        return name
    }
}
