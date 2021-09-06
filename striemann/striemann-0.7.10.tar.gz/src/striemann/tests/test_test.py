from expects import expect, have_len, be_empty
from striemann.test import fakes
from striemann.test.expectsmatcher import contain_metric


class TestExpectsMatcher:
    def test(self):
        metrics = fakes.FakeMetrics()
        metrics.incrementCounter("Burgers sold")
        metrics.recordGauge("Hunger level", 10)
        expect(metrics).to(contain_metric("Hunger level"))


class TestFakeMetrics:
    def test_flush(self):
        metrics = fakes.FakeMetrics()
        metrics.incrementCounter("Fake Service 1")
        metrics.incrementCounter("Fake Service 2")

        expect(metrics).to(have_len(2))

        metrics.flush()

        expect(metrics).to(be_empty)
