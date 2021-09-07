import numpy as np
import pytest


def test_float():
    from aermanager.transform import apply_by_channel
    from torchvision.transforms import RandomAffine
    tr = RandomAffine(0.)
    tr = apply_by_channel(tr)

    img = np.random.random((2, 10, 20)).astype(np.float32) - 0.5
    res = tr(img)

    assert np.all(img == res)
    assert img.dtype == res.dtype


def test_uint8():
    from aermanager.transform import apply_by_channel
    from torchvision.transforms import RandomAffine
    tr = RandomAffine(0.)
    tr = apply_by_channel(tr)

    img = np.random.choice(256, size=(2, 10, 20)).astype(np.uint8)
    res = tr(img)

    assert np.all(img == res)
    assert img.dtype == res.dtype


def test_identity_trasform():
    from aermanager.transform import apply_by_channel
    from torchvision.transforms import RandomAffine, ToPILImage
    tr = RandomAffine((10, 10), scale=(0.8, 0.8))
    img = np.random.choice(256, size=(1, 10, 20)).astype(np.uint8)

    res = tr(ToPILImage()(img[0]))
    tr = apply_by_channel(tr)
    res2 = tr(img)[0]

    assert np.all(res2 == res)


def test_transform_consistency():
    # this is useful to check that all channels are transformed equally
    # even if the transformation is not deterministic: important
    from aermanager.transform import apply_by_channel
    from torchvision.transforms import RandomAffine
    tr = RandomAffine(10, scale=(1.1, 1.3))
    img = np.random.choice(256, size=(1, 10, 20)).astype(np.uint8)
    img = np.repeat(img, axis=0, repeats=2)

    # check that the test is correct to start with
    assert np.all(img[0] == img[1])
    assert np.shape(img) == (2, 10, 20)

    tr = apply_by_channel(tr)
    res = tr(img)

    # check that the transformation has acted equally on the inputs
    assert np.all(res[0] == res[1])
    # check that the transformation has actually done something
    assert not np.all(res[0] == img[0])


def test_transform_consistency_4d():
    # this is useful to check that all channels are transformed equally
    # even if the transformation is not deterministic: important
    from aermanager.transform import apply_by_channel
    from torchvision.transforms import RandomAffine
    tr = RandomAffine(10, scale=(1.1, 1.3))
    img = np.random.choice(256, size=(1, 1, 10, 20)).astype(np.uint8)
    img = np.repeat(img, axis=0, repeats=2)
    img = np.repeat(img, axis=1, repeats=2)

    # check that the test is correct to start with
    assert np.all(img[0, 0] == img[1, 1])
    assert np.shape(img) == (2, 2, 10, 20)

    tr = apply_by_channel(tr)
    res = tr(img)

    # check that the transformation has acted equally on the inputs
    assert np.all(res[0, 0] == res[1, 1])
    # check that the transformation has actually done something
    assert not np.all(res[0, 0] == img[0, 0])


def test_transform_randomness():
    # the transform should be consistent on a single image, BUT should
    # change when we use multiple images, calling transform multiple times
    from aermanager.transform import apply_by_channel
    from torchvision.transforms import RandomAffine
    tr = RandomAffine(10, scale=(1.1, 1.3))
    img = np.random.choice(256, size=(1, 10, 20)).astype(np.uint8)
    img2 = img.copy()

    # check that the test is correct to start with
    assert np.all(img == img2)

    tr = apply_by_channel(tr)
    res = tr(img)
    res2 = tr(img2)

    # check that the transformation has acted equally on the inputs
    assert not np.all(res == res2)
    # check that the transformation has actually done something
    assert not np.all(res == img)


def test_event_animation():
    """
    modify the parms show ==True to see the visulized data
    :return:
    """
    from aermanager.aerparser import load_events_from_file
    from aermanager.visualization import events_animation
    from pathlib import Path
    TEST_FILE = Path(__file__).parent / "data" / "class2" / "data_sample.aedat4"
    shape, xytp = load_events_from_file(TEST_FILE)
    timescale = 1e3
    framerate = 24
    anim = events_animation(xytp, framerate = framerate, timescale=timescale, show=False, repeat=False)
    assert anim.save_count <= int(framerate*((xytp["t"][-1] - xytp["t"][0])/1e6))


def test_compose_consistency():
    from torchvision.transforms import RandomAffine, Compose
    from aermanager.transform import AddShotNoiseToFrame, SimpleToTensor
    tr1 = Compose(
        [SimpleToTensor(), RandomAffine(.1), AddShotNoiseToFrame(Hz=3, time_window=10, dt=1, n_dim=3)]
    )
    tr2 = Compose(
        [AddShotNoiseToFrame(Hz=3, time_window=10, dt=1, n_dim=3), SimpleToTensor(), RandomAffine(.1)]
    )
    img = np.random.choice(256, size=(1, 10, 20)).astype(np.uint8)
    res  = tr1(img)
    res2 = tr2(img)

    assert res.sum() > img.sum()
    assert res2.sum() > img.sum()


def test_shot_noise():
    from aermanager.transform import AddShotNoiseToFrame

    Hz = 1
    time_window = 1000
    empty_img_4d = np.zeros((1000, 1, 10, 20)).astype(np.uint8)
    empty_img_3d = np.zeros((1,10,20)).astype(np.uint8) #assume compressed frame with 1000ms time window
    Tr_3d = AddShotNoiseToFrame(Hz=Hz, time_window=time_window, n_dim=3, dt=1)
    Tr_4d = AddShotNoiseToFrame(Hz=Hz, time_window=time_window, n_dim=4, dt=1)
    res_3d = Tr_3d(empty_img_3d)
    res_4d = Tr_4d(empty_img_4d)

    assert round(res_3d.sum()/(res_3d.shape[1]*res_3d.shape[2])) == Hz
    assert round(res_4d.sum()/(res_4d.shape[2]*res_4d.shape[3])) == Hz


@pytest.mark.skip
def test_rasterize_slice_transform():
    raise NotImplementedError


@pytest.mark.skip
def test_collapse_channels_transform():
    raise NotImplementedError


@pytest.mark.skip
def test_crop_events_transform():
    raise NotImplementedError


@pytest.mark.skip
def test_resize_events_transform():
    # Test for shape larger than target
    # Test for shape smaller than target
    # Test for shape equal to target
    raise NotImplementedError
