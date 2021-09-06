"""
    binalyzer_core.extension
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module supports the creation of Binalyzer extensions.
"""
from binalyzer_core import (
    BinalyzerExtension,
    TemplateFactory,
    ValueProviderBase,
    value_cache,
)


class UtilityExtension(BinalyzerExtension):
    def __init__(self, binalyzer=None):
        super(UtilityExtension, self).__init__(binalyzer, "utils")

    def init_extension(self):
        super(UtilityExtension, self).init_extension()

    def count(self, property):
        return CountValueProvider(property)


class CountValueProvider(ValueProviderBase):
    def __init__(self, property):
        super(CountValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        template = TemplateFactory().clone(self.property.template)
        template.binding_context = self.property.template.binding_context
        total_data_size = self.property.template.binding_context.data.seek(0, 2)
        packet_record_address = self.property.template.absolute_address
        packet_record_count = 0
        while True:
            if packet_record_address >= total_data_size:
                break
            template.offset = packet_record_address
            packet_record_address = template.absolute_address + template.size
            packet_record_count += 1
        return packet_record_count

    def set_value(self, value):
        raise RuntimeError("Not implemented, yet.")
