# type
Command = "01"
Event   = "04"
Chip_Reset = "00"

# Opcode Tx
HCIExt_ResetSystemCmd       = "1D FC"
GAP_DeviceInit              = "00 FE"
# EventCode Rx
HCI_LE_ExtEvent             = "FF"
HCI_CommandCompleteEvent    = "0e"
HCI_LE_GenericReportEvent   = "3e"
HCIExt_ResetSystemCmdDone   = "1D 04"

#Event
GAP_DeviceInformation       = "0D 06"
GAP_DeviceDiscoveryDone     = "01 06"

#Status
SUCCESS = "00"

Packet = {  "Command"           :   0x01,
            "Asynchronous Data" :   0X02,
            "Synchronous Data"  :   0X03,
            "Event"             :   0X04,
            "Extended Command"  :   0X09
        }
