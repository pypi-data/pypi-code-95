import pandas as pd

from assistants.compliance.util import fields
from assistants.compliance.util.input_data_utility import completed_to_due_vector

dt_new_mogl = pd.Timestamp(2020, 9, 15)  # September 2020 MOGL changes


def fix_some_dates(data: pd.DataFrame) -> pd.DataFrame:
    """Fix Some Dates.

    Make sure if we have old M1 / M1EX then we also have Safety and Safeguarding
    Make sure M1, M1EX, Trustee Intro, GDPR, First Aid, Safety & Safeguarding are applied as appropriate

    We use pandas (vector) operations - slower but easier to understand!

    """
    m1_m1ex_min = "min_mod_1"

    data[m1_m1ex_min] = data[[fields.MOD_01, fields.MOD_01_EX]].min(axis=1)
    g = data.groupby(fields.MEMBERSHIP_NUMBER)

    # Given M01Ex validates M01, check that both are blank
    m_01_and_m01_ex_unset = data[fields.MOD_01].isna() & data[fields.MOD_01_EX].isna()
    # Where a given role has a blank for M01 or M01Ex and that member has a valid value for that
    # training type, fill it in
    # rolling_exclude is a crude attempt at an elif/switch chain in boolean logic
    rolling_exclude = pd.Series(False, index=data.index)
    for column in (fields.MOD_01, fields.MOD_01_EX):
        earliest_training_by_member = g[column].transform("min")
        mask = m_01_and_m01_ex_unset & earliest_training_by_member.notna() & ~rolling_exclude
        data.loc[mask, column] = earliest_training_by_member

        rolling_exclude = rolling_exclude | earliest_training_by_member.notna()

        # TODO implied M01 from VBA...

    # For Safety & Safeguarding, before 2020-09-15 these were automatically validated by Module 1
    # and Module 1EX. Automatic validation of SFTY & SAFE was only valid for the first validation
    # of M01/M01EX, so we find the oldest (min value), and a boolean mask for before/after the
    # September 2020 MOGL changes. For both SFTY & SAFE we then get the latest training date by
    # member, find the relevant date for auto-validation, and apply both to blanks
    min_m01_member = g[m1_m1ex_min].transform("min")
    pre_new_mogl = min_m01_member < dt_new_mogl
    for column, renewal in (
            (fields.SAFETY, fields.SAFETY_RENEWAL),
            (fields.SAFEGUARDING, fields.SAFEGUARDING_RENEWAL),
    ):
        latest_training_by_member = g[column].transform("max")
        # make sure Safety / Safeguarding set (if possible)
        # if M01/M01EX is set, before the 09/20 MOGL changes, and SFTY/SAFE isn't set
        auto_validated_date = min_m01_member[pre_new_mogl & latest_training_by_member.isna()]
        # Fills blanks with auto validated dates
        latest_training_with_auto_validated = latest_training_by_member.fillna(auto_validated_date)
        # Applies max value to blanks for that member
        data[column] = data[column].fillna(latest_training_with_auto_validated)

        # Given we have changed Safety/Safeguarding dates, we need to update renewal dates
        data[renewal] = completed_to_due_vector(data[column])

    # Finds max value for each member, and applies that value to nulls for that member
    for column in (
            fields.TRUSTEE_INTRO,
            fields.GDPR,
            # "safety" above
            fields.SAFETY_RENEWAL,
            # "safeguarding" above
            fields.SAFEGUARDING_RENEWAL,
            fields.FIRST_AID,
            fields.FIRST_AID_RENEWAL,
    ):
        data[column] = data[column].fillna(g[column].transform("max"))

    # Clean up
    del data[m1_m1ex_min]
    return data
