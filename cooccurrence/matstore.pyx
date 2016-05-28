from libc.stdio cimport FILE, fopen, fwrite, fclose, feof, fread
import collections
import ioutils
import os
from scipy.sparse import coo_matrix
import numpy as np
cimport numpy as np

"""Fast Cython methods for loading and storing matrices
"""

def reindex(mat, w_map, c_map, max_w, max_c):
    cdef int i
    cdef int new_row
    cdef int new_col
    mat = mat.tocoo()
    size = len(mat.data + 1)
    cdef np.ndarray[np.int32_t, ndim=1] row = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=1] col = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.float64_t, ndim=1] data = np.empty(size, dtype=np.float64)
    for i in xrange(len(mat.data)):
        row[i] = w_map[mat.row[i]]
        col[i] = c_map[mat.col[i]]
        data[i] = mat.data[i]
    row[size - 1] = max_w
    col[size - 1] = max_c
    data[size - 1] = 0
    mat = coo_matrix((data, (row, col)))
    mat = mat.tocsr()
    return mat

def export_mats_from_dicts(year_counts, output_dir):
    cdef FILE* fout
    cdef int word1
    cdef int word2
    cdef double val
    cdef char* fn
    for year, counts in year_counts.iteritems():
        filename = output_dir + str(year) + ".bin"
        fn = filename
        fout = fopen(fn, 'w')
        for (i, c), v in counts.iteritems():
            word1 = i
            word2  = c
            val = v
            fwrite(&word1, sizeof(int), 1, fout) 
            fwrite(&word2, sizeof(int), 1, fout) 
            fwrite(&val, sizeof(double), 1, fout) 
        fclose(fout)

def export_mat_from_dict(counts, year, output_dir):
    cdef FILE* fout
    cdef int word1
    cdef int word2
    cdef double val
    cdef char* fn
    filename = output_dir + str(year) + ".bin"
    fn = filename
    print filename
    fout = fopen(fn, 'w')
    for (i, c), v in counts.iteritems():
        word1 = i
        word2  = c
        val = v
        fwrite(&word1, sizeof(int), 1, fout) 
        fwrite(&word2, sizeof(int), 1, fout) 
        fwrite(&val, sizeof(double), 1, fout) 
    fclose(fout)


def export_mat_eff(row_d, col_d, data_d, year, output_dir):
    cdef FILE* fout
    cdef int word1
    cdef int word2
    cdef double val
    cdef char* fn
    cdef int i
    filename = output_dir + str(year) + ".bin"
    fn = filename
    fout = fopen(fn, 'w')
    for i in xrange(len(row_d)):
        word1 = row_d[i]
        word2  = col_d[i]
        val = data_d[i]
        fwrite(&word1, sizeof(int), 1, fout) 
        fwrite(&word2, sizeof(int), 1, fout) 
        fwrite(&val, sizeof(double), 1, fout) 
    fclose(fout)

def export_mat_shuf(row_d, col_d, data_d, year, output_dir):
    cdef FILE* fout
    cdef int word1
    cdef int word2
    cdef double val
    cdef char* fn
    cdef int i
    filename = output_dir + str(year) + ".bin"
    fn = filename
    fout = fopen(fn, 'w')
    for i in np.random.permutation(len(data_d)):
        word1 = row_d[i]
        word2  = col_d[i]
        val = data_d[i]
        fwrite(&word1, sizeof(int), 1, fout) 
        fwrite(&word2, sizeof(int), 1, fout) 
        fwrite(&val, sizeof(double), 1, fout) 
    fclose(fout)


def retrieve_mat_as_dict(filename):
    cdef FILE* fin
    cdef int word1
    cdef int word2
    cdef double val
    cdef char* fn
    year_count = collections.defaultdict(int)
    fn = filename
    fin = fopen(fn, 'r')
    while not feof(fin):
        fread(&word1, sizeof(int), 1, fin) 
        fread(&word2, sizeof(int), 1, fin) 
        fread(&val, sizeof(double), 1, fin) 
        year_count[(word1, word2)] = val
    fclose(fin)
    return year_count

def retrieve_mat_as_coo(matfn, min_size=None):
    cdef FILE* fin
    cdef int word1, word2, ret
    cdef double val
    cdef char* fn
    fn = matfn
    fin = fopen(fn, 'r')
    cdef int size = (os.path.getsize(matfn) / 16)
    if min_size != None:
        size += 1
    cdef np.ndarray[np.int32_t, ndim=1] row = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=1] col = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.float64_t, ndim=1] data = np.empty(size, dtype=np.float64)
    cdef int i = 0
    while not feof(fin):
        fread(&word1, sizeof(int), 1, fin) 
        fread(&word2, sizeof(int), 1, fin) 
        ret = fread(&val, sizeof(double), 1, fin) 
        if ret != 1:
            break
        row[i] = word1
        col[i] = word2
        data[i] = val
        i += 1
    fclose(fin)
    if min_size != None:
        row[-1] = min_size
        col[-1] = min_size
        data[-1] = 0
    return coo_matrix((data, (row, col)), dtype=np.float64)

def retrieve_mat_as_sym_coo(matfn, minsize=None):
    coo_mat = retrieve_mat_as_coo(matfn, minsize)
    csr_mat = coo_mat.tocsr()
    cdef size_t i
    for i in xrange(len(coo_mat.data)):
        if coo_mat.col[i] < csr_mat.shape[0] and coo_mat.row[i] < csr_mat.shape[1]:
            coo_mat.data[i] = max(coo_mat.data[i], csr_mat[coo_mat.col[i], coo_mat.row[i]])
    return coo_mat

def retrieve_mat_as_coo_thresh(matfn, thresh, min_size=None):
    cdef FILE* fin
    cdef int word1, word2, ret
    cdef double val
    cdef char* fn
    fn = matfn
    fin = fopen(fn, 'r')
    cdef int size = (os.path.getsize(matfn) / 16)
    if min_size != None:
        size += 1
    cdef np.ndarray[np.int32_t, ndim=1] row = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=1] col = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.float64_t, ndim=1] data = np.empty(size, dtype=np.float64)
    cdef int i = 0
    while not feof(fin):
        fread(&word1, sizeof(int), 1, fin) 
        fread(&word2, sizeof(int), 1, fin) 
        ret = fread(&val, sizeof(double), 1, fin) 
        if ret != 1:
            break
        if val < thresh:
            val = 0
        else: 
            val = val - thresh
        row[i] = word1
        col[i] = word2
        data[i] = val
        i += 1
    if min_size != None:
        row[-1] = min_size
        col[-1] = min_size
        data[-1] = 0
    fclose(fin)
    return coo_matrix((data, (row, col)), dtype=np.float64)

def retrieve_mat_as_binary_coo_thresh(matfn, thresh, min_size=None):
    cdef FILE* fin
    cdef int word1, word2, ret
    cdef double val
    cdef char* fn
    fn = matfn
    fin = fopen(fn, 'r')
    cdef int size = (os.path.getsize(matfn) / 16)
    if min_size != None:
        size += 1
    cdef np.ndarray[np.int32_t, ndim=1] row = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=1] col = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.float64_t, ndim=1] data = np.empty(size, dtype=np.float64)
    cdef int i = 0
    while not feof(fin):
        fread(&word1, sizeof(int), 1, fin) 
        fread(&word2, sizeof(int), 1, fin) 
        ret = fread(&val, sizeof(double), 1, fin) 
        if ret != 1:
            break
        if val < thresh:
            val = 0
        else: 
            val = 1.0
        row[i] = word1
        col[i] = word2
        data[i] = val
        i += 1
    if min_size != None:
        row[-1] = min_size
        col[-1] = min_size
        data[-1] = 0
    fclose(fin)
    return coo_matrix((data, (row, col)), dtype=np.float64)


def retrieve_mat_as_coo_percthresh(matfn, thresh, min_size=None):
    cdef FILE* fin
    cdef int word1, word2, ret
    cdef double val
    cdef char* fn
    fn = matfn
    fin = fopen(fn, 'r')
    cdef int size = (os.path.getsize(matfn) / 16) + 1
    if min_size != None:
        size += 1
    cdef np.ndarray[np.int32_t, ndim=1] row = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.int32_t, ndim=1] col = np.empty(size, dtype=np.int32)
    cdef np.ndarray[np.float64_t, ndim=1] data = np.empty(size, dtype=np.float64)
    cdef int i = 0
    while not feof(fin):
        fread(&word1, sizeof(int), 1, fin) 
        fread(&word2, sizeof(int), 1, fin) 
        ret = fread(&val, sizeof(double), 1, fin) 
        if ret != 1:
            break
        row[i] = word1
        col[i] = word2
        data[i] = val
        i += 1
    if min_size != None:
        row[-1] = min_size
        col[-1] = min_size
        data[-1] = 0
    data = data - np.percentile(data, 100 - thresh)
    data[data < 0] = 0
    fclose(fin)
    return coo_matrix((data, (row, col)), dtype=np.float64)
