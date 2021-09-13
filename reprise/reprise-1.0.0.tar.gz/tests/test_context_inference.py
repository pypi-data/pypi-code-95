import torch

from reprise.context_inference import ContextInference

from .model import LSTM


criterion = torch.nn.MSELoss()


def ci_loss(outputs, targets):
    return criterion(torch.cat(outputs, dim=0),
                     torch.cat(targets, dim=0))


def test_context_inference_zeros():
    torch.manual_seed(123)

    model = LSTM()
    with torch.no_grad():
        model.lstm.weight_ih_l0 = torch.nn.Parameter(
            torch.zeros_like(model.lstm.weight_ih_l0))
        model.lstm.weight_hh_l0 = torch.nn.Parameter(
            torch.zeros_like(model.lstm.weight_hh_l0))
        model.fc.weight = torch.nn.Parameter(torch.zeros_like(model.fc.weight))
        model.fc.bias = torch.nn.Parameter(torch.zeros_like(model.fc.bias))
    lstm_h = torch.zeros(2, 5, 10)
    lstm_c = torch.zeros(2, 5, 10)
    lstm_state = (lstm_h, lstm_c)

    context = torch.zeros([1, 5, 2])
    def opt_accessor(state): return [state[0]]
    params = [{'params': [context], 'lr': 0.1},
              {'params': opt_accessor(lstm_state)}]
    optimizer = torch.optim.Adam(params)
    ci = ContextInference(
        model=model,
        initial_model_state=lstm_state,
        opt_accessor=opt_accessor,
        context=context,
        optimizer=optimizer,
        inference_length=2,
        inference_cycles=2,
        criterion=ci_loss,
        reset_optimizer=True,
        context_handler=lambda x: torch.clamp(x, -1, 1))

    x_t = torch.zeros([1, 5, 2])
    delta = torch.zeros([1, 5, 2])

    context, outputs, states = ci.infer_contexts(x_t, delta)

    assert torch.eq(context, torch.zeros([1, 5, 2])).all()
    assert torch.eq(outputs[0], torch.zeros([1, 5, 2])).all()
    assert torch.eq(states[0][0], torch.zeros([2, 5, 10])).all()
    assert torch.eq(states[0][1], torch.zeros([2, 5, 10])).all()


def test_context_inference():
    torch.manual_seed(123)

    model = LSTM()
    lstm_h = torch.rand(2, 5, 10)
    lstm_c = torch.rand(2, 5, 10)
    lstm_state = (lstm_h, lstm_c)

    context = torch.rand([1, 5, 2])
    def opt_accessor(state): return [state[0]]
    params = [{'params': [context], 'lr': 0.1},
              {'params': opt_accessor(lstm_state)}]
    optimizer = torch.optim.Adam(params)
    ci = ContextInference(
        model=model,
        initial_model_state=lstm_state,
        opt_accessor=opt_accessor,
        context=context,
        optimizer=optimizer,
        inference_length=2,
        inference_cycles=2,
        criterion=ci_loss,
        reset_optimizer=True,
        context_handler=lambda x: torch.clamp(x, -1, 1))

    x_t = torch.rand([1, 5, 2])
    delta = torch.rand([1, 5, 2])

    context, outputs, states = ci.infer_contexts(x_t, delta)

    assert torch.allclose(
        context, torch.Tensor([[[0.3695391119,  0.7943273783],
                                [0.1154637635,  0.6450493336],
                                [0.2445835173,  0.6829689145],
                                [-0.0227577165,  0.8091154099],
                                [0.4548792541,  0.7143015265]]]))

    assert torch.allclose(
        outputs[0], torch.Tensor([[[-0.1674475521,  0.3211223483],
                                   [-0.1067506149,  0.1984867156],
                                   [-0.1947517097,  0.2740014791],
                                   [-0.1711761653,  0.2326730788],
                                   [-0.1178287417,  0.1454539597]]]))
