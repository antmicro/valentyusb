import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, NullTrigger, Timer
from cocotb.result import TestFailure, TestSuccess, ReturnValue

from cocotb_usb.host import UsbTest
from cocotb_usb.utils import grouper_tofit
from cocotb_usb.usb.endpoint import *
from cocotb_usb.usb.pid import *

dut_csrs = 'csr.csv'

@cocotb.test()
def get_device_descriptor(dut):
    harness = UsbTest(dut, dut_csrs)
    yield harness.reset()
    yield harness.connect()

    yield harness.clear_pending(EndpointType.epaddr(0, EndpointType.OUT))
    yield harness.clear_pending(EndpointType.epaddr(0, EndpointType.IN))

    # Device has no address set yet
    device_address_uninitialized = 0
    yield harness.write(harness.csrs['usb_address'], device_address_uninitialized)

    # Set address (to 20)
    device_address = 20
    yield harness.control_transfer_out(
        device_address_uninitialized,
        [0x00, 0x05, device_address, 0x00, 0x00, 0x00, 0x00, 0x00],
        # 18 byte descriptor, max packet size 8 bytes
        None,
    )

    yield harness.write(harness.csrs['usb_address'], device_address)

    device_descriptor_request = [
            0x80, # Device-to-host, standard, device
            0x06, # Get descriptor
            0x00, # Descriptor index 0
            0x01, # Descriptor type 1
            0x00, 0x00, # No LangID specified
            0x00, 0x0A, # Len 10
        ]

    device_descriptor_response = [
            0x12, # Length 18
            0x01, # Descriptor type: device
            0x02, 0x00, # Compliant with USB Spec 2.0
            0x00, # Device Class: Device
            0x00, # Device SubClass
            0x00, # DeviceProtocol
            0x40, # MaxPacketSize
            0x1d, 0x6b, # idVendor
            0x01, 0x05, # idProduct
            0x01, 0x00, # bcdDevice
            0x01, # iManufacturer
            0x02, # iProduct
            0x03, # iSerialNumber
            0x01, # bNumConfigurations
        ]

    yield harness.control_transfer_in(
        device_address,
        device_descriptor_request,
        device_descriptor_response,
    )

@cocotb.test()
def get_configuration_descriptor(dut):
    harness = UsbTest(dut, dut_csrs)
    yield harness.reset()
    yield harness.connect()

    yield harness.clear_pending(EndpointType.epaddr(0, EndpointType.OUT))
    yield harness.clear_pending(EndpointType.epaddr(0, EndpointType.IN))

    device_address = 20

    yield harness.write(harness.csrs['usb_address'], device_address)

    config_descriptor_request = [
            0x80, # Device-to-host, standard, device
            0x06, # Get descriptor
            0x00, # Descriptor index 0
            0x02, # Descriptor type 2
            0x00, 0x00, # No LangID specified
            0x00, 0x09, # Len 9
        ]
    config_descriptor_response = [
            0x09, # Length 9
            0x02, # Descriptor type: config
            0x20, 0x00, # Total length 32
            0x01, # NumInterfaces
            0x01, # bConfigurationValue
            0x00, # iConfiguration
            0x80, # bmAttributes
            0x32, # bMaxPower
        ]
    yield harness.control_transfer_in(
        device_address,
        config_descriptor_request,
        config_descriptor_response,
    )
