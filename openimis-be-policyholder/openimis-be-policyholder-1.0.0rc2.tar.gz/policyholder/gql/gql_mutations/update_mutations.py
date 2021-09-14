from core.gql.gql_mutations.base_mutation import BaseMutation, BaseHistoryModelUpdateMutationMixin
from core.models import InteractiveUser
from policyholder.models import PolicyHolder, PolicyHolderInsuree, PolicyHolderContributionPlan, PolicyHolderUser
from policyholder.gql.gql_mutations import PolicyHolderInsureeUpdateInputType, \
    PolicyHolderContributionPlanUpdateInputType, PolicyHolderUserUpdateInputType, PolicyHolderUpdateInputType
from policyholder.validation import PolicyHolderValidation


class UpdatePolicyHolderMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "PolicyHolderMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolder

    class Input(PolicyHolderUpdateInputType):
        pass

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        PolicyHolderValidation.validate_update(user, **data)


class UpdatePolicyHolderInsureeMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "PolicyHolderInsureeMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolderInsuree

    class Input(PolicyHolderInsureeUpdateInputType):
        pass


class UpdatePolicyHolderContributionPlanMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "PolicyHolderContributionPlanMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolderContributionPlan

    class Input(PolicyHolderContributionPlanUpdateInputType):
        pass


class UpdatePolicyHolderUserMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "PolicyHolderUserMutation"
    _mutation_module = "policyholder"
    _model = PolicyHolderUser

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')
        updated_object = cls._model.objects.filter(id=data['id']).first()
        [setattr(updated_object, key, data[key]) for key in data]
        cls.update_policy_holder_user(user=user, object_to_update=updated_object)

    @classmethod
    def update_policy_holder_user(cls, user, object_to_update):
        object_to_update.save(username=user.username)
        return object_to_update

    class Input(PolicyHolderUserUpdateInputType):
        pass

