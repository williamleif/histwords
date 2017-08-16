
import json
import time
import os

import datetime
import helpers
import mimetypes

from urlparse import urlparse, parse_qs
import zlib

from collections import defaultdict

def write_response(handler, code, headers, data=""):
    handler.send_response(200)
    for header in headers:
        i = header.index(":")
        s,e = header[:i], header[i+1:]
        handler.send_header(s,e)

    if data:
        zlib_encode = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        content = zlib_encode.compress(data) + zlib_encode.flush()

        if len(content) < len(data):
            handler.send_header('Content-Encoding', 'gzip')
            handler.send_header('Content-Length', len(content))
        else:
            content = data

        handler.end_headers()

        handler.wfile.write(content)
    else:
        handler.wfile.write(data)

def get_list(query, key, default=None):
    if key in query:
        vals = query[key]
        return vals


    return default or []

def get_value(query, key, default=None):
    if key in query:
        vals = query[key]
        assert(len(vals) == 1)
        return vals[0]

    return default


STATIC = {
    "/" : os.path.join(helpers.VIZ_DIR, "static", "page.html"),
    "/favicon.ico" : os.path.join(helpers.VIZ_DIR, "static", "favicon.ico"),
    "/web/style.css" : os.path.join(helpers.VIZ_DIR, "static", "style.css"),
    "/web/client.js" : os.path.join(helpers.VIZ_DIR, "static", "client.js")
}

import lru
search_cache = lru.cache('search', 100)
term_cache = lru.cache('neighbors', 1000)
def do_search(word1):

    if not word1 in search_cache:
        embeddings = helpers.load_embeddings()
        words = word1.split(":")
        all_lookups = {}
        all_sims = defaultdict(list)
        all_terms = defaultdict(list)
        for word2 in words:
            if not word2 in term_cache:
                term_cache[word2] = helpers.get_time_sims(embeddings, word2)
            else:
                print "USING CACHED NEIGHBORS FOR", word2

            time_sims, lookups, nearests, sims = term_cache[word2]

            for word in lookups:
                all_terms[word].append(word2)

            for word in lookups:
                all_sims[word].append(sims[word])

            all_lookups.update(lookups)

        words = all_lookups.keys()
        values = [ all_lookups[word] for word in words ]
        fitted = helpers.fit_tsne(values)


        # we should stitch the arrays together into objects, i guess
        objs = []
        for i in xrange(len(words)):
            word = words[i]
            ww, decade = word.split("|")
            obj = {
                "word" : ww,
                "query" : all_terms[word],
                "year" : int(decade),
                "similarity" : all_sims[word],
                "avg_similarity" : sum(all_sims[word]) / len(all_sims[word]),
                "sum_similarity" : sum(all_sims[word]),
                "position" : {
                    "x" : round(fitted[i][0], 3),
                    "y" : round(fitted[i][1], 3)
                }
            }

            objs.append(obj)

        search_cache[word1] = objs

    return {
        "term" : word1,
        "results" : search_cache[word1]
    }

def do_get(handler):
    parts = urlparse(handler.path)
    query = parse_qs(parts.query)

    if parts.path in STATIC:
        with open(STATIC[parts.path], "r") as f:
            mt, enc = mimetypes.guess_type(parts.path)
            if not mt:
                mt,enc = mimetypes.guess_type(STATIC[parts.path])

            write_response(handler, 200, ['Content-type: %s' % (mt)], f.read())
    elif parts.path == '/r/':
        cmd = get_value(query, "cmd")
        room = get_value(query, "room")
        prev_ts = float(get_value(query, "since", 0))

        msg_dict = {
            "since": helpers.get_now()
        }

        if cmd == "search":
            term = get_value(query, "term")
            print "DOING SEARCH", term
            if term:
                ret = do_search(term)
            msg_dict.update(ret)

        write_response(handler, 200, ['Content-type: text/json'], json.dumps(msg_dict))


def do_post(handler):
    content_len = int(handler.headers.getheader('content-length', 0))
    post_body = handler.rfile.read(content_len)

    parts = urlparse(handler.path)
    query = parse_qs(post_body)
    prev_ts = float(get_value(query, "since", 0))

    if parts.path == '/r/':
        cmd = get_value(query, "cmd")

    else:
        debug("UNKNOWN URL", parts.path)

    write_response(handler, 200, ['Content-type: text/html'], "OK")
