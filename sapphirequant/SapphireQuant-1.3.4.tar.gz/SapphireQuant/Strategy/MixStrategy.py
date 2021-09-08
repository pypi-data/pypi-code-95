from abc import ABC

from SapphireQuant.Strategy.BaseStrategy import BaseStrategy


class MixStrategy(BaseStrategy, ABC):
    """
    混合策略基类
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.strategy_series = []

    def add_strategy(self, strategy):
        """

        :param strategy:
        """
        self.strategy_series.append(strategy)
        key = 'ID_{0}_{1}'.format(strategy.product_code, strategy.strategy_id)
        if key in self.kwargs.keys():
            print('开始初始化策略:{0}, {1}'.format(strategy.product_code, strategy.strategy_id))
            strategy.__init__(self.kwargs[key])

    def on_start(self):
        """
        开始
        """
        for strategy in self.strategy_series:
            strategy.on_start()

    def on_bar(self, bar):
        """

        :param bar:
        """
        for strategy in self.strategy_series:
            strategy.on_bar(bar)

    def on_tick(self, tick):
        """

        :param tick:
        """
        for strategy in self.strategy_series:
            strategy.on_tick(tick)

    def on_exit(self):
        """
        策略结束
        """
        for strategy in self.strategy_series:
            strategy.on_exit()
