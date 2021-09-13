import torch

from reprise.action_inference import ActionInference

from .model import LSTM


criterion = torch.nn.MSELoss()


def ai_loss(outputs, targets):
    return criterion(torch.cumsum(
        torch.cat(outputs, dim=0), dim=0), targets)


def test_action_inference_zeros():
    torch.manual_seed(123)

    model = LSTM()
    with torch.no_grad():
        model.lstm.weight_ih_l0 = torch.nn.Parameter(
            torch.zeros_like(model.lstm.weight_ih_l0))
        model.lstm.weight_hh_l0 = torch.nn.Parameter(
            torch.zeros_like(model.lstm.weight_hh_l0))
        model.fc.weight = torch.nn.Parameter(torch.zeros_like(model.fc.weight))
        model.fc.bias = torch.nn.Parameter(torch.zeros_like(model.fc.bias))
    lstm_h = torch.zeros(2, 1, 10)
    lstm_c = torch.zeros(2, 1, 10)
    lstm_state = (lstm_h, lstm_c)

    policy = torch.zeros([10, 1, 2])
    optimizer = torch.optim.Adam([policy], lr=0.1)
    ai = ActionInference(
        model=model,
        policy=policy,
        optimizer=optimizer,
        inference_cycles=5,
        criterion=ai_loss,
        reset_optimizer=False,
        policy_handler=lambda x: torch.clamp(x, -1, 1))

    delta = torch.zeros([1, 1, 2])
    context = torch.zeros([10, 1, 0])
    targets = torch.zeros([10, 1, 2])
    policy, path, states = ai.infer_actions(
        delta, lstm_state, context, targets)

    assert torch.eq(policy, torch.zeros([1, 10, 2])).all()
    assert torch.eq(torch.cat(path, dim=0), torch.zeros([1, 10, 2])).all()
    for state in states:
        assert torch.eq(state[0], torch.zeros([2, 1, 10])).all()
        assert torch.eq(state[1], torch.zeros([2, 1, 10])).all()


def test_action_inference():
    torch.manual_seed(123)

    model = LSTM()
    lstm_h = torch.rand(2, 1, 10)
    lstm_c = torch.rand(2, 1, 10)
    lstm_state = (lstm_h, lstm_c)

    policy = torch.rand([10, 1, 2])
    optimizer = torch.optim.Adam([policy], lr=0.1)
    ai = ActionInference(
        model=model,
        policy=policy,
        optimizer=optimizer,
        inference_cycles=5,
        criterion=ai_loss,
        reset_optimizer=False,
        policy_handler=lambda x: torch.clamp(x, -1, 1))

    delta = torch.rand([1, 1, 2])
    context = torch.rand([10, 1, 0])
    targets = torch.rand([10, 1, 2])
    offset = torch.rand([2])
    policy, path, states = ai.infer_actions(
        delta, lstm_state, context, targets - offset)

    assert torch.allclose(
        policy, torch.Tensor([[[1.0000000000, -0.2622272968]],
                              [[0.5261428356, -0.0897055641]],
                              [[0.6878218055, -0.1898529232]],
                              [[0.5700316429,  0.4806243777]],
                              [[1.0000000000, -0.3901612461]],
                              [[0.6530221105, -0.0320187584]],
                              [[0.6139146686, -0.1958029568]],
                              [[0.6969076991, -0.1866425574]],
                              [[1.0000000000,  0.4152778983]],
                              [[0.5436700583, -0.4942405224]]]))

    assert torch.allclose(
        torch.cat(path, dim=0),
        torch.Tensor(
            [[[-0.1602207273, 0.2738576829]],
             [[-0.0972151384, 0.2365996093]],
             [[-0.0560891405, 0.2250262052]],
             [[-0.0309798047, 0.2270904928]],
             [[-0.0212426968, 0.2285058200]],
             [[-0.0144851711, 0.2336517274]],
             [[-0.0104313828, 0.2387633622]],
             [[-0.0086893141, 0.2419171929]],
             [[-0.0075556803, 0.2418972552]],
             [[-0.0062273839, 0.2448652685]]]))
