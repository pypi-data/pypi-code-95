from policyholder.gql.gql_mutations import PolicyHolderInsureeReplaceInputType, \
    PolicyHolderContributionPlanReplaceInputType, PolicyHolderUserReplaceInputType
from core.gql.gql_mutations.base_mutation import BaseReplaceMutation, BaseHistoryModelReplaceMutationMixin
from core.models import InteractiveUser
from policyholder.models import PolicyHolder, PolicyHolderInsuree, PolicyHolderContributionPlan, PolicyHolderUser


class ReplacePolicyHolderInsureeMutation(BaseHistoryModelReplaceMutationMixin, BaseReplaceMutation):
    _mutation_class = "PolicyHolderInsureeMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolderInsuree

    class Input(PolicyHolderInsureeReplaceInputType):
        pass


class ReplacePolicyHolderContributionPlanMutation(BaseHistoryModelReplaceMutationMixin, BaseReplaceMutation):
    _mutation_class = "PolicyHolderContributionPlanMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolderContributionPlan

    class Input(PolicyHolderContributionPlanReplaceInputType):
        pass


class ReplacePolicyHolderUserMutation(BaseHistoryModelReplaceMutationMixin, BaseReplaceMutation):
    _mutation_class = "PolicyHolderUserMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolderUser

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')
        object_to_replace = cls._model.objects.filter(id=data['uuid']).first()
        if object_to_replace is None:
            cls._object_not_exist_exception(data['uuid'])
        else:
            object_to_replace.replace_object(data=data, username=user.username)

    class Input(PolicyHolderUserReplaceInputType):
        pass