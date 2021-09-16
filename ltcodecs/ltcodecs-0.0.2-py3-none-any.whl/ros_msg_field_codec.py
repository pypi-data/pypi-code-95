import re
from bitstring import ConstBitStream, BitArray
from .field_codec import FieldCodec
import field_codecs as field_codecs
from rospy import AnyMsg
from typing import Union
import roslib.message


class RosMsgFieldCodec(FieldCodec):
    def __init__(self, ros_type: Union[str, AnyMsg], fields: dict = None, **kwargs):
        self.fields = fields
        self.ros_type = ros_type

        if isinstance(ros_type, str):
            msg_class = roslib.message.get_message_class(ros_type)
            if not msg_class:
                raise TypeError('Invalid ROS type "{}" for message codec {}'.format(ros_type, id))
        else:
            msg_class = ros_type
        self.ros_msg_class = msg_class

        self.field_codecs = {}
        # Handle the case where we have to infer the field list from the ROS msg, since the user didn't specify one.
        if not self.fields:
            slot_names = msg_class.__slots__
            slot_types = msg_class._slot_types

            slots = dict(zip(slot_names, slot_types))

            new_fields = dict.fromkeys(slot_names)
            for field_name in new_fields:
                msg_type = slots[field_name]
                if msg_type in field_codecs.field_codec_classes:
                    field_params = {'codec': msg_type}
                else:
                    # There are two cases here: arrays or nested ROS messages
                    if msg_type.endswith(']'):
                        # either a variable or fixed length array
                        matched = re.match(r'(?P<element_type>.*)\[(?P<array_len>\d*)\]', msg_type)
                        if matched['array_len']:
                            array_len = int(matched['array_len'])
                            field_params = {'codec': 'fixed_len_array',
                                            'length': array_len}
                        else:
                            field_params = {'codec': 'variable_len_array',
                                            'max_length': 10}  # TODO: maybe take this as a parameter?
                        # and the element type is either a standard type or a ROS message
                        if matched['element_type'] in field_codecs.field_codec_classes:
                            field_params['element_type'] = matched['element_type']
                        else:
                            field_params['element_type'] = 'msg'
                            field_params['element_params'] = {'ros_type': matched['element_type']}
                    else:
                        # It's a nested ROS message
                        field_params = {'codec': 'msg',
                                        'ros_type': msg_type}

                new_fields[field_name] = field_params

            self.fields = new_fields

        # Now, build the list of codec classes for each field
        self.field_codecs = {}
        for field_name, field_params in self.fields.items():
            # print(field_name, field_params['codec'])
            # print(field_codecs.field_codec_classes[field_params['codec']])
            try:
                if field_params['codec'] not in field_codecs.metadata_decoders.keys():
                    self.field_codecs[field_name] = field_codecs.field_codec_classes[field_params['codec']](**field_params)
                else:
                    self.field_codecs[field_name] = None
            except KeyError as e:
                raise KeyError("Error parsing codec config for {}.  Got params:\n{}\nError: {}".format(field_name,
                                                                                                       field_params,
                                                                                                       e))

    def encode(self, message: AnyMsg):
        # ROS messages use __slots__, so we can't use __dict__ or vars() to get the attributes as a dict
        message_dict = {}
        for field in message.__slots__:
            message_dict[field] = getattr(message, field)

        encoded_bits = BitArray()
        encoded_dict = {}
        for field_name, field_params in self.fields.items():
            try:
                field_codec = self.field_codecs[field_name]
                if not field_codec:
                    continue
                field_bits, encoded_dict[field_name] = field_codec.encode(message_dict[field_name])
                encoded_bits.append(field_bits)
            except Exception as e:
                #print("Codec: {}, max len bits {}".format(field_codec, field_codec.max_length_bits))
                raise Exception('Error encoding field "{}" with codec {} (max len bits {})'.format(field_name, field_codec, field_codec.max_length_bits)).with_traceback(e.__traceback__)
        return encoded_bits, encoded_dict

    def decode(self, bits_to_decode: ConstBitStream):
        # We go through the bits in sequence until we are decoded.
        # The ConstBitStream has an internal read pointer.
        decoded_message = {}
        for field_name, field_params in self.fields.items():
            field_codec = self.field_codecs[field_name]
            if not field_codec:
                continue
            ## print("Ros decode field {}".format(field_name))
            decoded_message[field_name] = field_codec.decode(bits_to_decode)
        ## print("Ros decode got {}".format(decoded_message))
        return self.ros_msg_class(**decoded_message)

    def decode_as_dict(self, bits_to_decode: ConstBitStream):
        # This function is used to generate an object that we can use for calculating CRCs in the message codec
        # It seems like a bit of a hack, but the alternative would require adding a second return value to every field
        # decoder.  Since this only affects ROS messages, this keeps the bloat down.
        decoded_message = {}
        for field_name, field_params in self.fields.items():
            field_codec = self.field_codecs[field_name]
            if hasattr(field_codec, 'decode_as_dict'):
                decoded_message[field_name] = field_codec.decode_as_dict(bits_to_decode)
            else:
                decoded_message[field_name] = field_codec.decode(bits_to_decode)
        ## print("Ros decode got {}".format(decoded_message))
        return decoded_message

    @property
    def min_length_bits(self):
        return sum([c.min_length_bits for c in self.field_codecs.values()])

    @property
    def max_length_bits(self):
        return sum([c.max_length_bits for c in self.field_codecs.values()])

