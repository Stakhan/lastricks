def gen_synthetic_las_dataset(nb_tiles=3, points_per_tile=10):
    "Synthetically generates a set of LAS/LAZ representations."
    
    # Arbitrary starting point
    X0, Y0 = 443_000, 6_659_000

    lases = []
    for n in nb_tiles:
        allX, allY, allZ = ( X0 + random_sample(size=(length,))*1e3,
                            Y0 + random_sample(size=(length,))*1e3,
                            random_sample(size=(length,))*100 )

        Xmin, Ymin, Zmin = ( np.floor(np.min(allX)),
                            np.floor(np.min(allY)),
                            np.floor(np.min(allZ)) )

        Xmax, Ymax, Zmax = ( np.ceil(np.max(allX)),
                            np.ceil(np.max(allY)),
                            np.ceil(np.max(allZ)) )

        mock_hdr = laspy.LasHeader(version="1.4", point_format=6)
        mock_hdr.offsets, mock_hdr.scales = [0.0,0.0,0.0],[0.001,0.001,0.001]
        mock_hdr.mins, mock_hdr.maxs = [Xmin,Ymin,Zmin], [Xmax,Ymax,Zmax]

        mock_las = laspy.LasData(mock_hdr)
        mock_las.X, mock_las.Y, mock_las.Z = allX, allY, allZ
        
        lases.append(mock_las)
        X0 += 1000
        Y0 += 1000

    return lases


def gen_synthetic_vect_ref(
        lases,
        ratio_total_changes=0.1,
        ratio_change=0.7,
        ratio_no_change=0.3
        ):
    """Generate a synthetic set of reference vectors.

    Args:
        lases (list(LasData)): set of LAS/LAZ representations
        ratio_total_changes (float, optional): ratio of points to emphasize in
            set of vectors. Defaults to 0.1.
        ratio_change (float, optional): ratio of points that should
    """
    assert ratio_change + ratio_no_change == 1
    # generate buffers around 30% of points
    pass


@pytest.fixture
def deliveries(tmp_path):
    path_deliv1 = tmp_path / 'deliv1'
    path_deliv1.mkdir(exist_ok=True)
    path_deliv2 = tmp_path / 'deliv2'
    path_deliv2.mkdir(exist_ok=True)

    pptile=10
    lases = gen_synthetic_las_dataset(points_per_tile=pptile)
    for las in lases:
        # deliv 1
        las.classification = np.ones(pptile)
        las.write(path_deliv1 / f'{las.mins[0]}_{las.maxs[1]}.laz')

        # deliv 2
        las.classification = [1 + int(np.random_sample()>0.5) for i in range(pptile)]
        las.write(path_deliv2 / f'{las.mins[0]}_{las.maxs[1]}.laz')
    vect_ref_path = gen_synthetic_vect_ref(lases)
