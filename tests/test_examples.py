from __future__ import print_function
import unittest
import os


class TestDenseBindings(unittest.TestCase):
    def setUp(self):
        self.test_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "..", "data")

    def test_mesh_sampling(self):
        import point_cloud_utils as pcu
        import numpy as np

        # v is a nv by 3 NumPy array of vertices
        # f is an nf by 3 NumPy array of face indexes into v
        # n is a nv by 3 NumPy array of vertex normals if they are specified, otherwise an empty array
        v, f, n = pcu.load_mesh_vfn(os.path.join(self.test_path, "cube_twist.obj"))
        bbox = np.max(v, axis=0) - np.min(v, axis=0)
        bbox_diag = np.linalg.norm(bbox)

        f_idx1, bc1 = pcu.sample_mesh_random(v, f, num_samples=1000, random_seed=1234567)
        f_idx2, bc2 = pcu.sample_mesh_random(v, f, num_samples=1000, random_seed=1234567)
        f_idx3, bc3 = pcu.sample_mesh_random(v, f, num_samples=1000, random_seed=7654321)
        self.assertTrue(np.all(f_idx1 == f_idx2))
        self.assertTrue(np.all(bc1 == bc2))
        self.assertFalse(np.all(f_idx1 == f_idx3))
        self.assertFalse(np.all(bc1 == bc3))

        # Generate very dense  random samples on the mesh (v, f)
        f_idx, bc = pcu.sample_mesh_random(v, f, num_samples=v.shape[0] * 4)
        v_dense = (v[f[f_idx]] * bc[:, np.newaxis]).sum(1)

        s_idx = pcu.downsample_point_cloud_poisson_disk(v_dense, 0, 0.1*bbox_diag, random_seed=1234567)
        s_idx2 = pcu.downsample_point_cloud_poisson_disk(v_dense, 0, 0.1*bbox_diag, random_seed=1234567)
        s_idx3 = pcu.downsample_point_cloud_poisson_disk(v_dense, 0, 0.1 * bbox_diag, random_seed=7654321)
        self.assertTrue(np.all(s_idx == s_idx2))
        if s_idx3.shape == s_idx.shape:
            self.assertFalse(np.all(s_idx == s_idx3))
        else:
            self.assertFalse(s_idx.shape == s_idx3.shape)

        # Ensure we can request more samples than vertices and get something reasonable
        s_idx_0 = pcu.downsample_point_cloud_poisson_disk(v_dense, 2*v_dense.shape[0], random_seed=1234567)

        s_idx = pcu.downsample_point_cloud_poisson_disk(v_dense, 1000, random_seed=1234567)
        s_idx2 = pcu.downsample_point_cloud_poisson_disk(v_dense, 1000, random_seed=1234567)
        s_idx3 = pcu.downsample_point_cloud_poisson_disk(v_dense, 1000, random_seed=7654321)
        self.assertTrue(np.all(s_idx == s_idx2))
        if s_idx3.shape == s_idx.shape:
            self.assertFalse(np.all(s_idx == s_idx3))
        else:
            self.assertFalse(s_idx.shape == s_idx3.shape)

        f_idx1, bc1 = pcu.sample_mesh_poisson_disk(v, f, num_samples=1000,
                                                   random_seed=1234567, use_geodesic_distance=True,
                                                   oversampling_factor=5.0)
        f_idx2, bc2 = pcu.sample_mesh_poisson_disk(v, f, num_samples=1000,
                                                   random_seed=1234567, use_geodesic_distance=True,
                                                   oversampling_factor=5.0)
        f_idx3, bc3 = pcu.sample_mesh_poisson_disk(v, f, num_samples=1000,
                                                   random_seed=7654321, use_geodesic_distance=True,
                                                   oversampling_factor=5.0)
        self.assertTrue(np.all(f_idx1 == f_idx2))
        self.assertTrue(np.all(bc1 == bc2))
        if f_idx1.shape == f_idx3.shape:
            self.assertFalse(np.all(f_idx1 == f_idx3))
        if bc1.shape == bc3.shape:
            self.assertFalse(np.all(bc1 == bc3))

        f_idx1, bc1 = pcu.sample_mesh_poisson_disk(v, f, num_samples=-1, radius=0.01*bbox_diag,
                                                   random_seed=1234567, oversampling_factor=5.0)
        f_idx2, bc2 = pcu.sample_mesh_poisson_disk(v, f, num_samples=-1, radius=0.01*bbox_diag,
                                                   random_seed=1234567, oversampling_factor=5.0)
        f_idx3, bc3 = pcu.sample_mesh_poisson_disk(v, f, num_samples=-1, radius=0.01*bbox_diag,
                                                   random_seed=7654321, oversampling_factor=5.0)
        self.assertTrue(np.all(f_idx1 == f_idx2))
        self.assertTrue(np.all(bc1 == bc2))
        if f_idx1.shape == f_idx3.shape:
            self.assertFalse(np.all(f_idx1 == f_idx3))
        if bc1.shape == bc3.shape:
            self.assertFalse(np.all(bc1 == bc3))

    def test_downsample_point_cloud_voxel_grid(self):
        import point_cloud_utils as pcu
        import numpy as np

        # v is a nv by 3 NumPy array of vertices
        # f is an nf by 3 NumPy array of face indexes into v
        # n is a nv by 3 NumPy array of vertex normals if they are specified, otherwise an empty array
        v, f, n = pcu.load_mesh_vfn(os.path.join(self.test_path, "cube_twist.obj"))
        bbox = np.max(v, axis=0) - np.min(v, axis=0)
        bbox_diag = np.linalg.norm(bbox)
        vox_grid_size = 1.0 / 128.0

        # Make sure we have normals
        self.assertEqual(n.shape, v.shape)

        # Vanilla case
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v)
        self.assertIsNone(nms)
        self.assertIsNone(clr)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With normals
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n)
        self.assertIsNone(clr)
        self.assertEqual(nms.shape, pts.shape)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With RBG colors
        c = np.random.rand(v.shape[0], 3)
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, None, c)
        self.assertIsNone(nms)
        self.assertEqual(clr.shape, pts.shape)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With RBGA colors
        c = np.random.rand(v.shape[0], 4)
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, None, c)
        self.assertIsNone(nms)
        self.assertEqual(clr.shape[0], pts.shape[0])
        self.assertEqual(clr.shape[1], 4)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With normals and RGB colors
        c = np.random.rand(v.shape[0], 3)
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)
        self.assertEqual(nms.shape, pts.shape)
        self.assertEqual(clr.shape, pts.shape)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With normals and RBGA colors
        c = np.random.rand(v.shape[0], 4)
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)
        self.assertEqual(nms.shape, pts.shape)
        self.assertEqual(clr.shape[0], pts.shape[0])
        self.assertEqual(clr.shape[1], 4)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With different voxel size per axis
        vox_grid_size = [1.0/128.0, 1.0/99.0, 1.0/222.0]
        c = np.random.rand(v.shape[0], 4)
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)
        self.assertEqual(nms.shape, pts.shape)
        self.assertEqual(clr.shape[0], pts.shape[0])
        self.assertEqual(clr.shape[1], 4)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # With bounding box dimensions
        vox_grid_size = np.array([1.0/128.0, 1.0/99.0, 1.0/222.0])
        min_bound = np.min(v, axis=0) - 0.5 * np.array(vox_grid_size)
        max_bound = np.max(v, axis=0) + 0.5 * np.array(vox_grid_size)
        c = np.random.rand(v.shape[0], 4)
        pts, nms, clr = pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c,
                                                              min_bound=min_bound, max_bound=max_bound)
        self.assertEqual(nms.shape, pts.shape)
        self.assertEqual(clr.shape[0], pts.shape[0])
        self.assertEqual(clr.shape[1], 4)
        self.assertGreater(pts.shape[0], 0)
        self.assertEqual(pts.shape[1], 3)

        # Should raise if the voxel size is too small
        with self.assertRaises(ValueError):
            vox_grid_size = [1e-16, 1.0/99.0, 1.0/222.0]
            c = np.random.rand(v.shape[0], 4)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)

        # Should raise if the voxel size is negative
        with self.assertRaises(ValueError):
            vox_grid_size = [1.0/100.0, -1.0/99.0, 1.0/222.0]
            c = np.random.rand(v.shape[0], 4)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)

        # Invalid color dimension
        with self.assertRaises(ValueError):
            c = np.random.rand(v.shape[0], 2)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)

        # Invalid normal dimension
        with self.assertRaises(ValueError):
            c = np.random.rand(v.shape[0], 2)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n[:, :1], c)

        # Invalid number of normals
        with self.assertRaises(ValueError):
            c = np.random.rand(v.shape[0], 3)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n[1:, :], c)

        # Invalid number of colors
        with self.assertRaises(ValueError):
            c = np.random.rand(v.shape[0]//2, 3)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c)

        # Negative bounding box
        with self.assertRaises(ValueError):
            min_bound = np.min(v, axis=0) - 0.5 * np.array(vox_grid_size)
            max_bound = np.max(v, axis=0) + 0.5 * np.array(vox_grid_size)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c, max_bound=min_bound, min_bound=max_bound)

        # Badly shaped grid size
        with self.assertRaises(ValueError):
            vox_grid_size = [1.0/100.0, 1.0/99.0]
            min_bound = np.min(v, axis=0) - 0.5 * np.array(vox_grid_size)
            max_bound = np.max(v, axis=0) + 0.5 * np.array(vox_grid_size)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c, max_bound=max_bound, min_bound=min_bound)

        # Badly shaped max bound
        with self.assertRaises(ValueError):
            vox_grid_size = [1.0/100.0, 1.0/99.0, 1.0/77.0]
            min_bound = np.min(v, axis=0) - 0.5 * np.array(vox_grid_size)
            max_bound = np.max(v, axis=0) + 0.5 * np.array(vox_grid_size)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c, max_bound=max_bound[:1], min_bound=min_bound)

        # Badly shaped max bound
        with self.assertRaises(ValueError):
            vox_grid_size = [1.0/100.0, 1.0/99.0, 1.0/77.0]
            min_bound = np.min(v, axis=0) - 0.5 * np.array(vox_grid_size)
            max_bound = np.max(v, axis=0) + 0.5 * np.array(vox_grid_size)
            pcu.downsample_point_cloud_voxel_grid(vox_grid_size, v, n, c, max_bound=max_bound[:1], min_bound=(1.0, 1.0))

    def test_lloyd_relaxation(self):
        import point_cloud_utils as pcu

        # v is a nv by 3 NumPy array of vertices
        # f is an nf by 3 NumPy array of face indexes into v
        v, f, n = pcu.load_mesh_vfn(os.path.join(self.test_path, "cube_twist.obj"))

        # Generate 1000 points on the mesh with Lloyd's algorithm
        samples = pcu.sample_mesh_lloyd(v, f, 1000)

        # Generate 100 points on the unit square with Lloyd's algorithm
        samples_2d = pcu.lloyd_2d(100)

        # Generate 100 points on the unit cube with Lloyd's algorithm
        samples_3d = pcu.lloyd_3d(100)

    def test_sinkhorn(self):
        import point_cloud_utils as pcu
        import numpy as np

        # a and b are arrays where each row contains a point
        # Note that the point sets can have different sizes (e.g [100, 3], [111, 3])
        a = np.random.rand(100, 3)
        b = np.random.rand(100, 3)

        # M is a 100x100 array where each entry  (i, j) is the squared distance between point a[i, :] and b[j, :]
        M = pcu.pairwise_distances(a, b)

        # w_a and w_b are masses assigned to each point. In this case each point is weighted equally.
        w_a = np.ones(a.shape[0])
        w_b = np.ones(b.shape[0])

        # P is the transport matrix between a and b, eps is a regularization parameter, smaller epsilons lead to
        # better approximation of the true Wasserstein distance at the expense of slower convergence
        P = pcu.sinkhorn(w_a, w_b, M, eps=1e-3)

        # To get the distance as a number just compute the frobenius inner product <M, P>
        sinkhorn_dist = (M * P).sum()

    def test_batched_sinkhorn(self):
        import point_cloud_utils as pcu
        import numpy as np

        # a and b are each contain 10 batches each of which contain 100 points  of dimension 3
        # i.e. a[i, :, :] is the i^th point set which contains 100 points
        # Note that the point sets can have different sizes (e.g [10, 100, 3], [10, 111, 3])
        a = np.random.rand(10, 100, 3)
        b = np.random.rand(10, 100, 3)

        # M is a 10x100x100 array where each entry (k, i, j) is the squared distance between point a[k, i, :]
        # and b[k, j, :]
        M = pcu.pairwise_distances(a, b)

        # w_a and w_b are masses assigned to each point. In this case each point is weighted equally.
        w_a = np.ones(a.shape[:2])
        w_b = np.ones(b.shape[:2])

        # P is the transport matrix between a and b, eps is a regularization parameter, smaller epsilons lead to
        # better approximation of the true Wasserstein distance at the expense of slower convergence
        P = pcu.sinkhorn(w_a, w_b, M, eps=1e-3)

        # To get the distance as a number just compute the frobenius inner product <M, P>
        sinkhorn_dist = (M * P).sum()

    def test_chamfer(self):
        import point_cloud_utils as pcu
        import numpy as np

        # a and b are arrays where each row contains a point
        # Note that the point sets can have different sizes (e.g [100, 3], [111, 3])
        a = np.random.rand(100, 3)
        b = np.random.rand(100, 3)

        chamfer_dist = pcu.chamfer_distance(a, b)
        chamfer_dist, c_a_to_b, c_b_to_a = pcu.chamfer_distance(a, b, return_index=True)

    def test_knn(self):
        import point_cloud_utils as pcu
        import numpy as np

        for i in range(3):
            # Generate two random point sets
            a = np.random.rand(1000, 3)
            b = np.random.rand(500, 3)
            # dists_a_to_b is of shape (a.shape[0],) and contains the shortest squared distance
            # between each point in a and the points in b
            # corrs_a_to_b is of shape (a.shape[0],) and contains the index into b of the
            # closest point for each point in a
            k = np.random.randint(10) + 1
            dists_a_to_b, corrs_a_to_b = pcu.k_nearest_neighbors(a, b, k)
            if k > 1:
                self.assertEqual(dists_a_to_b.shape, (a.shape[0], k))
                self.assertEqual(corrs_a_to_b.shape, (a.shape[0], k))
            else:
                self.assertEqual(dists_a_to_b.shape, (a.shape[0],))
                self.assertEqual(corrs_a_to_b.shape, (a.shape[0],))

            if k == 1:
                dists_a_to_b = dists_a_to_b[:, np.newaxis]
                corrs_a_to_b = corrs_a_to_b[:, np.newaxis]

            for i in range(dists_a_to_b.shape[1]):
                b_map = b[corrs_a_to_b[:, i]]
                dists = np.linalg.norm(a - b_map, axis=-1)
                diff_dists = dists - dists_a_to_b[:, i]
                self.assertTrue(np.all(np.abs(diff_dists) < 1e-5))

            b_map = b[corrs_a_to_b]
            dists = np.linalg.norm(a[:, np.newaxis, :] - b_map, axis=-1)
            diff_dists = dists - dists_a_to_b
            self.assertTrue(np.all(np.abs(diff_dists) < 1e-5))

        with self.assertRaises(ValueError):
            a = np.random.rand(1000, 3)
            b = np.random.rand(500, 3)
            dists_a_to_b, corrs_a_to_b = pcu.k_nearest_neighbors(a, b, 0)

        a = np.random.rand(100, 3)
        b = np.random.rand(50, 3)
        dists_a_to_b, corrs_a_to_b = pcu.k_nearest_neighbors(a, b, 3)
        dists_a_to_b2, corrs_a_to_b2 = pcu.k_nearest_neighbors(a, b, 3, squared_distances=True)

        self.assertTrue(np.all(corrs_a_to_b == corrs_a_to_b2))
        self.assertTrue(np.all(np.abs(dists_a_to_b ** 2.0 - dists_a_to_b2) < 1e-5))

    def test_hausdorff(self):
        import point_cloud_utils as pcu
        import numpy as np

        # Generate two random point sets
        a = np.random.rand(1000, 3)
        b = np.random.rand(500, 3)

        # Compute each one sided squared Hausdorff distances
        hausdorff_a_to_b, idx_a1, idx_b1 = pcu.one_sided_hausdorff_distance(a, b, return_index=True)
        hausdorff_b_to_a, idx_b2, idx_a2 = pcu.one_sided_hausdorff_distance(b, a, return_index=True)

        # Take a max of the one sided squared  distances to get the two sided Hausdorff distance
        hausdorff_a_b = max(hausdorff_a_to_b, hausdorff_b_to_a)
        hausdorff_a_b_pcu, i1, i2 = pcu.hausdorff_distance(a, b, return_index=True)
        self.assertAlmostEqual(hausdorff_a_b, hausdorff_a_b_pcu)
        self.assertAlmostEqual(hausdorff_a_b, np.linalg.norm(a[i1] - b[i2]))
        self.assertAlmostEqual(hausdorff_a_b_pcu, np.linalg.norm(a[i1] - b[i2]))
        if hausdorff_a_to_b > hausdorff_b_to_a:
            self.assertEqual(i1, idx_a1)
            self.assertEqual(i2, idx_b1)
        else:
            self.assertEqual(i1, idx_a2)
            self.assertEqual(i2, idx_b2)

        # Find the index pairs of the two points with maximum shortest distancce
        hausdorff_b_to_a, idx_b, idx_a = pcu.one_sided_hausdorff_distance(b, a, return_index=True)
        self.assertAlmostEqual(np.linalg.norm(a[idx_a] - b[idx_b]), hausdorff_b_to_a)

    def test_estimate_point_cloud_normals(self):
        import point_cloud_utils as pcu
        import numpy as np

        # v is a nv by 3 NumPy array of vertices
        # f is an nf by 3 NumPy array of face indexes into v
        # n is a nv by 3 NumPy array of vertex normals if they are specified, otherwise an empty array
        v, f, n = pcu.load_mesh_vfn(os.path.join(self.test_path, "cube_twist.obj"))

        # Estimate normals for the point set, v using 12 nearest neighbors per point
        n = pcu.estimate_point_cloud_normals(v, k=12)
        self.assertEqual(n.shape, v.shape)

    def skip_test_morton_coding_big_data(self):
        import point_cloud_utils as pcu
        import numpy as np
        import os
        if os.name == 'nt':
            num_pts = 1000
            num_qpts = 10
        else:
            num_pts = 1000000
            num_qpts = 10000
        div = 1.0 / 1000.0
        pts = np.random.rand(num_pts, 3) / div
        pts_int = pts.astype(np.int32)

        qpts = np.random.rand(num_qpts, 3) / div
        qpts_int = qpts.astype(np.int32)

        codes = pcu.morton_encode(pts_int)
        codes_sort_idx = np.argsort(codes)
        codes_sorted = codes[codes_sort_idx]

        qcodes = pcu.morton_encode(qpts_int)

        nn_idx = pcu.morton_knn(codes_sorted, qcodes, 7)
        codes_sorted[nn_idx]
        self.assertEqual(nn_idx.shape, (num_qpts, 7))

    def skip_test_morton_coding_small_data(self):
        import point_cloud_utils as pcu
        import numpy as np
        div = 1.0 / 1000.0
        pts = np.random.rand(10, 3) / div
        pts_int = pts.astype(np.int32)

        qpts = np.random.rand(10000, 3) / div
        qpts_int = qpts.astype(np.int32)

        codes = pcu.morton_encode(pts_int)
        codes_sort_idx = np.argsort(codes)
        codes_sorted = codes[codes_sort_idx]

        qcodes = pcu.morton_encode(qpts_int)

        nn_idx = pcu.morton_knn(codes_sorted, qcodes, 7)
        codes_sorted[nn_idx]
        self.assertEqual(nn_idx.shape, (10000, 7))

    def skip_test_morton_coding_tiny_data(self):
        import point_cloud_utils as pcu
        import numpy as np
        div = 1.0 / 1000.0
        pts = np.random.rand(10, 3) / div
        pts_int = pts.astype(np.int32)

        qpts = np.random.rand(10000, 3) / div
        qpts_int = qpts.astype(np.int32)

        codes = pcu.morton_encode(pts_int)
        codes_sort_idx = np.argsort(codes)
        codes_sorted = codes[codes_sort_idx]

        qcodes = pcu.morton_encode(qpts_int)

        nn_idx = pcu.morton_knn(codes_sorted, qcodes, 15)
        codes_sorted[nn_idx]
        self.assertEqual(nn_idx.shape, (10000, 10))

    def test_remove_duplicate_points(self):
        import point_cloud_utils as pcu
        import numpy as np

        # v is a nv by 3 NumPy array of vertices
        v = pcu.load_mesh_v(os.path.join(self.test_path, "duplicated_pcloud.ply"))

        v2, idx_v_to_v2, idx_v2_to_v = pcu.remove_duplicate_points(v, 1e-11, return_index=True)
        self.assertLess(v2.shape[0], v.shape[0])
        self.assertTrue(np.all(np.equal(v2[idx_v2_to_v], v)))
        self.assertTrue(np.all(np.equal(v[idx_v_to_v2], v2)))

    def test_downsample_mesh_voxel_grid(self):
        import point_cloud_utils as pcu
        import numpy as np

        # v is a nv by 3 NumPy array of vertices
        v = pcu.load_mesh_v(os.path.join(self.test_path, "duplicated_pcloud.ply"))

        bbmin, bbmax = v.min(0), v.max(0)
        bbsize = bbmax - bbmin

        vdown, _, _ = pcu.downsample_point_cloud_voxel_grid(bbsize/128.0, v)

        self.assertLess(vdown.shape[0], v.shape[0])

    def test_closest_points_on_mesh(self):
        import point_cloud_utils as pcu
        import numpy as np

        v, f = pcu.load_mesh_vf(os.path.join(self.test_path, "cube_twist.obj"))

        v -= v.min(0)
        v /= v.max(0)
        v -= 0.5
        v *= 2.0

        p = np.random.rand(1000, 3)

        d, fi, bc = pcu.closest_points_on_mesh(p, v, f)

        closest_points = (v[f[fi]] * bc[:, :, np.newaxis]).sum(1)
        d2 = np.linalg.norm(p - closest_points, axis=-1)

        self.assertAlmostEqual(np.max(d - d2), 0.0)



if __name__ == '__main__':
    unittest.main()
