from pathlib import Path
from aermanager.dataset_generator import gen_dataset_from_folders

HERE = Path(__file__).parent

gen_dataset_from_folders(
    source_path=HERE / "data",
    destination_path=HERE / "dataset_test",
    compression=None,
    crop_size=None,
    hot_pixel_frequency=None,
    time_window=None,
    spike_count=5000,
)


def test_frames():
    from aermanager.datasets import FramesDataset

    ds = FramesDataset(HERE / "dataset_test")
    assert len(ds) > 0
    data, label = ds[0]
    assert data.shape == (2, 240, 320)
    assert label in (b'class1', b'class2')


def test_frames_transforms():
    from aermanager.datasets import FramesDataset

    ds = FramesDataset(HERE / "dataset_test",
                       transform=lambda fr: fr.sum(0, keepdims=True),
                       target_transform=lambda l: "myclass")
    assert len(ds) > 0
    data, label = ds[0]
    assert data.shape == (1, 240, 320)
    assert label == "myclass"


def test_spiketrains():
    from aermanager.datasets import SpikeTrainDataset

    ds = SpikeTrainDataset(HERE / "dataset_test/data_sample_bcac0")
    assert len(ds) > 0
    data, label = ds[0]
    assert data.shape == (5000, )


def test_accum():
    from aermanager.datasets import SpikeTrainDataset

    ds_spk = SpikeTrainDataset(HERE / "dataset_test")
    ds_accum = SpikeTrainDataset(HERE / "dataset_test",
                                 dt=10000)

    assert len(ds_spk) == len(ds_accum)
    for i in range(len(ds_accum)):
        spktrain, label1 = ds_spk[i]
        frame, label2 = ds_accum[i]

        assert label1 == label2
        assert frame.shape[1:] == (2, 240, 320)
        assert len(frame) > 1
        if not (len(spktrain) == frame.sum()):
            breakpoint()
