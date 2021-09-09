from ..models.base import TClient, TFornecedor
from .soap import BaseSoapWrapper


class FortesWrapper(BaseSoapWrapper):

    # def trata_retorno(self, data):
    #     mensagem_retorno = data.find("Retorno")
    #     mensagem_erro = data.find("Erro")
    #
    #     mensagem_retorno = data[mensagem_retorno:mensagem_erro]
    #     mensagem_erro = data[mensagem_erro:]
    #
    #     return mensagem_retorno, mensagem_erro

    def incluir_cliente(self, cliente):
        data = TClient(**cliente)
        r = self.get_client().service.IncluirClienteComJSON(data.json())
        return r

    def incluir_fornecedor(self, fornecedor):
        data = TFornecedor(**fornecedor)
        r = self.get_client().service.IncluirFornecedorComJSON(data.json())
        return r

    def excluir_cliente(self, document):
        r = self.get_client().service.ExcluiClienteWithCNPJCPF(document)
        return r

    def excluir_fornecedor_com_json(self, fornecedor):
        data = TFornecedor(**fornecedor)
        r = self.get_client().service.ExcluirFornecedorComJSON(data.json())
        return r
