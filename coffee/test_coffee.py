'''
    Coffee Tests
    ~~~~~~~~~~~~
'''

import struct
import unittest

from coffee import channel

class TestExpandFormatString (unittest.TestCase):

    def test_expand_without_F (self):
        format = channel.expand_format_string('BBHBB')
        self.assertEqual(format, 'BBHBB')


    def test_expand_with_F (self):
        format = channel.expand_format_string('BBFHFB')
        self.assertEqual(format, 'BBBBHBBB')


class TestGenerateInputFormat (unittest.TestCase):

    def test_format_too_long (self):
        self.assertRaises(RuntimeError, channel.generate_input_format, [
                ('B', 'label1'),
                ('B', 'label2'),
                ('H', 'label3'),
                ('F', 'label4'),
                ('L', 'label5')
            ])

        def test_format_too_short (self):
            format = channel.generate_input_format([
                    ('B', 'label1'),
                    ('H', 'label2'),
                    ('F', 'label3'),
                ])
            self.assertEqual(format, '!BBHBBBB')


        def test_format_right_size (self):
            format = channel.generate_input_format([
                    ('B', 'label1'),
                    ('H', 'label2'),
                    ('F', 'label3'),
                    ('H', 'label4'),
                ])
            elf.assertEqual(format, '!BBHBBH')


class TestUnpackFloat (unittest.TestCase):

    def test_unpack_float (self):
        self.assertEqual(42.0, channel.unpack_float(42, 0))
        self.assertEqual(0.941, round(channel.unpack_float(0, 240), 3))


class TestUnpackMessage (unittest.TestCase):

    def test_unpack_7_byte_long_message_without_float (self):
        fields = [
            ('H', 'label1'),
            ('B', 'label2'),
            ('H', 'label3'),
            ('H', 'label4'),
        ]
        
        rv = channel.unpack_message(fields, (1, 2, 3, 4))
        for k, v in rv.items():
            self.assertEqual(k, 'label{}'.format(v))


    def test_unpack_padded_message_without_float (self):
        fields = [
            ('H', 'label1'),
            ('B', 'label2'),
            ('H', 'label3'),
        ]
        
        rv = channel.unpack_message(fields, (1, 2, 3, 0, 0))
        for k, v in rv.items():
            self.assertEqual(k, 'label{}'.format(v))


    def test_message_with_floats (self):
        fields = [
            ('H', 'label1'),
            ('B', 'label2'),
            ('F', 'label3'),
            ('B', 'label4')
        ]
        
        rv = channel.unpack_message(fields, (1, 2, 42, 15, 100, 0))
        expect = {
            'label1': 1,
            'label2': 2,
            'label3': 42.05882352941177,
            'label4': 100,
        }

        for k, v in expect.items():
            self.assertEqual(v, rv[k])
        

class MockChannel (channel.Channel):

    def __init__ (self):
        self.written = []

    def send (self, packed):
        self.written.append(packed)


class MockMessage (object):
    pass


class TestChannel (unittest.TestCase):

    def setUp (self):
        self.channel = MockChannel()


    def test_channel_dispatch (self):
        message = MockMessage()
        message.command = 16
        message.format = 'BHFBB'
        
        message.data = [42, 1024]
        message.data.extend(channel.pack_float(42.15))
        message.data.extend([5, 0])

        message.fields = [
                ('H', 'label1'),
                ('F', 'label2'),
                ('B', 'label3')
            ]

        def receive ():
            return struct.pack('!BHBBBBB', 16, 42, 120, 15, 5, 0, 0)

        self.channel.receive = receive
        rv = self.channel.dispatch(message)

        self.assertEqual(rv, {
                'label1': 42, 
                'label2': 120.05882352941177,
                'label3': 5,
            })





if __name__ == '__main__':
    unittest.main()
