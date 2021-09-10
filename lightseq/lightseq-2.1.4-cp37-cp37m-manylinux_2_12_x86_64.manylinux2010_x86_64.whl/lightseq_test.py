import numpy as np
import lightseq.inference as lsi


def test_diverse_beam_search():
    model = lsi.Transformer(
        "query_bidword_cuda_v2/query_bidword_transformer_cuda.0.0.1/transformer.pb", 8
    )

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    test_input = np.array([[52, 49998, 49998]])

    res = model.infer(test_input, multiple_output=True)
    print(res)


def test_math():
    model = lsi.Transformer("lightseq_math.pb", 32)

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    test_input = np.array([[2, 448, 40, 32, 205, 5, 112] for _ in range(32)])

    res = model.infer(test_input)
    print(res)


def test_xlmr():
    model = lsi.XLMR(
        "/data00/home/xiongying.taka/projects/Multilingual_Ad_Title_Generation/multilingual_title_de.hdf5",
        4,
    )
    test_input = np.array(
        [
            [1, 382, 5179, 252, 1, 2],
            [1, 41092, 3093, 1, 2, 2],
            [1, 2068, 14229, 15728, 12323, 1],
        ]
    )
    src_lang_ids = [21, 21, 21]
    trg_lang_ids = [21, 21, 21]
    res = model.infer(test_input, src_lang_ids, trg_lang_ids)
    print(res)

def test_24e6d():
    import pickle

    with open("inp.pkl", "rb")as f:
        data = pickle.load(f)

    test_input = data[:8]
    model = lsi.Transformer("transformer.hdf5", 8)

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    # test_input = np.array([[2, 448, 40, 32, 205, 5, 112] for _ in range(4)])

    res = model.infer(test_input)
    print(res)
    with open("outp.pkl", "rb")as f:
        test_out = pickle.load(f)
    print(test_out[:8])
    np.testing.assert_allclose(res[0], test_out[:8].numpy())


if __name__ == "__main__":
    # test_diverse_beam_search()
    # test_math()
    # test_xlmr()
    test_24e6d()
