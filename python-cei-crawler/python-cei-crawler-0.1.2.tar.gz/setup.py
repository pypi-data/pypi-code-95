# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cei_crawler', 'cei_crawler.tests']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.7.4', 'beautifulsoup4==4.10.0']

setup_kwargs = {
    'name': 'python-cei-crawler',
    'version': '0.1.2',
    'description': 'Biblioteca em python para obtenção de seus dados de investimentos na bolsa de valores (B3/CEI).',
    'long_description': '# python-cei-crawler\nBiblioteca em python para obtenção de seus dados de investimentos na bolsa de valores (B3/CEI).\n\nEsse projeto é altamente influenciado por [bolsa](https://github.com/gicornachini/bolsa). De fato, eu apenas simplifiquei, adicionei e estendi algumas funcionalidades.\n\n# Requisitos\n - Python 3.8.x\n\n## Instalação\n```\n$ pip install python-cei-crawler\n```\n\n## Utilização\n```python\nimport asyncio\n\nfrom cei_crawler import CeiCrawler\n\n\nasync def main():\n    crawler = CeiCrawler(username="CPF/CNPJ", password="Sua senha")\n    \n    assets_extract = await crawler.get_assets_extract()\n    print(assets_extract) # seus ativos negociados no CEI\n\n    passive_income_extract = await crawler.get_passive_incomes_extract()\n    print(passive_income_extract) # seus proventos registrados no CEI\n\n    await crawler.close()\n\n\nif __name__ == "__main__":\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(main())\n\n```\n\n## Funções disponíveis\n\nAtravés da classe de client `CeiCrawler`, você terá acesso as seguintes funções:\n\n### `get_brokers`\nObtém os brokers disponíveis para aquela conta. Retorna uma lista de `Broker` (Ex: XP Inc, Clear, Easynvest...) com uma lista de `BrokerAccount`.\n\n### `get_assets_extract`\nObtém uma lista de ativos filtrados pelo parâmetros passados à função. Retorna uma lista de `AssetExtract`.\n\n#### Parâmetros\n| Atributo | Tipo | Descrição |\n| :-------------: |:-------------:| -----|\n| `brokers` | `Optional[List[Broker]]` | Retorna apenas os ativos destes brokers |\n| `start_date` | `Optional[date]` | Retorna apenas os ativos com data posterior ou igual a esta. Por favor, note que o CEI aceita datas dentro de um *range* específico. Se a data passada à função estiver fora, será usado o respectivo valor do *range* inferior. |\n| `end_date` | `Optional[date]` | Retorna apenas os ativos com data inferior ou igual a esta. Por favor, note que o CEI aceita datas dentro de um *range* específico. Se a data passada à função estiver fora, será usado o respectivo valor do *range* superior. |\n| `as_dict` | `bool` | Retorna os ativos como dicionários ao invés de objetos `AssetExtract`. Default: `False` |\n\n### `get_passive_incomes_extract`\nObtém uma lista de rendimentos passivos filtrados pelo parâmetros passados à função. Retorna uma lista de `PassiveIncome`.\n\n#### Parâmetros\n| Atributo | Tipo | Descrição |\n| :-------------: |:-------------:| -----|\n| `date` | `Optional[date]` | Retorna apenas os ativos com data posterior ou igual a esta. Por favor, note que o CEI só aceita datas iguais ou 5 dias anteriores ao dia de hoje. Se uma data fora desse intervalo for passado, a consulta será feita com a data de hoje. |\n| `as_dict` | `bool` | Retorna os ativos como dicionários ao invés de objetos `PassiveIncome`. Default: `False` |\n\n## Models\n\n#### Broker\nModel responsável pelos dados do broker.\n\n| Atributo        | Tipo           | Descrição  |\n| :-------------: |:-------------:| -----|\n| `value`      | `str` | Identificador da corretora na B3. |\n| `name`      | `str`      |   Nome do broker na B3. |\n| `accounts` | `List[BrokerAccount]`      |    Lista de contas no broker. |\n\n\n#### BrokerAccount\nModel responsável pelos dados da conta no broker.\n\n| Atributo        | Tipo           | Descrição  |\n| :-------------: |:-------------:| -----|\n| `id`      | `str` | Número da conta no broker. |\n\n\n#### AssetExtract\nModel responsável pelos dados do ativo.\n\n| Atributo        | Tipo           | Descrição  |\n| :-------------: |:-------------:| -----|\n| `operation_date`      | `datetime` | Data de operação do ativo. |\n| `action`      | `AssetExtractAction`      |   Identificador do tipo de operação compra/venda. |\n| `market_type` | `AssetExtractMarketType`      |   Tipo de mercado. |\n| `raw_negotiation_code` | `str`      |    Código de negociação. |\n| `asset_specification` | `str`      |    Especificação do ativo no CEI. |\n| `unit_amount` | `int`      |    Quantidade de ativo. |\n| `unit_price` | `Decimal`      |    Valor unitário do ativo. |\n| `total_price` | `Decimal`      |    Valor total do ativo. |\n| `quotation_factor` | `int`      |    Fator de cotação. |\n\n#### PassiveIncome\nModel responsável pelos dados de rendimento passivo.\n\n| Atributo        | Tipo           | Descrição  |\n| :-------------: |:-------------:| -----|\n| `operation_date`      | `datetime` | Data do evento. |\n| `income_type`      | `PassiveIncomeType`      |   Tipo de provento (Dividendo, JCP...). |\n| `event_type`      | `PassiveIncomeEventType`      |   Tipo de evento do provento (provisionado, creditado...). |\n| `raw_negotiation_name` | `str`      |    Nome do ativo. |\n| `raw_negotiation_code` | `str`      |    Código de negociação. |\n| `asset_specification` | `str`      |    Especificação do ativo no CEI. |\n| `unit_amount` | `int`      |    Quantidade de ativo. |\n| `gross_value` | `Decimal`      |    Valor bruto do provento. |\n| `net_value` | `Decimal`      |    Valor líquido do provendo. |\n| `quotation_factor` | `int`      |    Fator de cotação. |',
    'author': 'MuriloScarpaSitonio',
    'author_email': 'muriloscarpa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MuriloScarpaSitonio/python-cei-crawler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
