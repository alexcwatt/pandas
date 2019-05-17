import string

import numpy as np
import pytest

import pandas.util._test_decorators as td

import pandas as pd
import pandas.util.testing as tm


class TestSeriesAccessor:
    # TODO: collect other Series accessor tests
    def test_to_dense(self):
        s = pd.Series([0, 1, 0, 10], dtype='Sparse[int64]')
        result = s.sparse.to_dense()
        expected = pd.Series([0, 1, 0, 10])
        tm.assert_series_equal(result, expected)


class TestFrameAccessor:

    def test_accessor_raises(self):
        df = pd.DataFrame({"A": [0, 1]})
        with pytest.raises(AttributeError, match='sparse'):
            df.sparse

    @pytest.mark.parametrize('format', ['csc', 'csr', 'coo'])
    @pytest.mark.parametrize("labels", [
        None,
        list(string.ascii_letters[:10]),
    ])
    @pytest.mark.parametrize('dtype', ['float64', 'int64'])
    @td.skip_if_no_scipy
    def test_from_spmatrix(self, format, labels, dtype):
        import scipy.sparse

        sp_dtype = pd.SparseDtype(dtype, np.array(0, dtype=dtype).item())

        mat = scipy.sparse.eye(10, format=format, dtype=dtype)
        result = pd.DataFrame.sparse.from_spmatrix(
            mat, index=labels, columns=labels
        )
        expected = pd.DataFrame(
            np.eye(10, dtype=dtype),
            index=labels,
            columns=labels,
        ).astype(sp_dtype)
        tm.assert_frame_equal(result, expected)

    @pytest.mark.parametrize("columns", [
        ['a', 'b'],
        pd.MultiIndex.from_product([['A'], ['a', 'b']]),
        ['a', 'a'],
    ])
    @td.skip_if_no_scipy
    def test_from_spmatrix_columns(self, columns):
        import scipy.sparse

        dtype = pd.SparseDtype('float64', 0.0)

        mat = scipy.sparse.random(10, 2, density=0.5)
        result = pd.DataFrame.sparse.from_spmatrix(mat, columns=columns)
        expected = pd.DataFrame(
            mat.toarray(), columns=columns
        ).astype(dtype)
        tm.assert_frame_equal(result, expected)

    @td.skip_if_no_scipy
    def test_to_coo(self):
        import scipy.sparse

        df = pd.DataFrame({
            "A": [0, 1, 0],
            "B": [1, 0, 0],
        }, dtype='Sparse[int64, 0]')
        result = df.sparse.to_coo()
        expected = scipy.sparse.coo_matrix(np.asarray(df))
        assert (result != expected).nnz == 0

    def test_to_dense(self):
        df = pd.DataFrame({
            "A": pd.SparseArray([1, 0], dtype=pd.SparseDtype('int64', 0)),
            "B": pd.SparseArray([1, 0], dtype=pd.SparseDtype('int64', 1)),
            "C": pd.SparseArray([1., 0.],
                                dtype=pd.SparseDtype('float64', 0.0)),
        }, index=['b', 'a'])
        result = df.sparse.to_dense()
        expected = pd.DataFrame({
            'A': [1, 0],
            'B': [1, 0],
            'C': [1.0, 0.0],
        }, index=['b', 'a'])
        tm.assert_frame_equal(result, expected)

    def test_density(self):
        df = pd.DataFrame({
            'A': pd.SparseArray([1, 0, 2, 1], fill_value=0),
            'B': pd.SparseArray([0, 1, 1, 1], fill_value=0),
        })
        res = df.sparse.density
        expected = 0.75
        assert res == expected
