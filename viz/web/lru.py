import pylru

CACHES = {}

def cache(name, size):
    if not name in CACHES:
        CACHES[name] = pylru.lrucache(size)

    return CACHES[name]
