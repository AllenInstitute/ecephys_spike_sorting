#pragma once

#ifdef __cplusplus
extern "C" {
#endif	

#include <stdint.h>
#include <stdbool.h>
#include <Windows.h>

#define NP_EXPORT __declspec(dllexport)
#define NP_APIC __stdcall

#define PROBE_ELECTRODE_COUNT 960
#define PROBE_CHANNEL_COUNT   384
#define PROBE_SUPERFRAMESIZE  12


#define ELECTRODEPACKET_STATUS_TRIGGER    (1<<0)
#define ELECTRODEPACKET_STATUS_SYNC       (1<<6)

#define ELECTRODEPACKET_STATUS_LFP        (1<<1)
#define ELECTRODEPACKET_STATUS_ERR_COUNT  (1<<2)
#define ELECTRODEPACKET_STATUS_ERR_SERDES (1<<3)
#define ELECTRODEPACKET_STATUS_ERR_LOCK   (1<<4)
#define ELECTRODEPACKET_STATUS_ERR_POP    (1<<5)
#define ELECTRODEPACKET_STATUS_ERR_SYNC   (1<<7)

struct electrodePacket {
	uint32_t timestamp[PROBE_SUPERFRAMESIZE];
	int16_t apData[PROBE_SUPERFRAMESIZE][PROBE_CHANNEL_COUNT];
	int16_t lfpData[PROBE_CHANNEL_COUNT];
	uint16_t Status[PROBE_SUPERFRAMESIZE];
	//uint16_t SYNC[PROBE_SUPERFRAMESIZE];
};

struct ADC_Calib {
	int ADCnr;
	int CompP;
	int CompN;
	int Slope;
	int Coarse;
	int Fine;
	int Cfix;
	int offset;
	int threshold;
};

/**
* Neuropix API error codes
*/
typedef enum {
	
	SUCCESS = 0,/**< The function returned sucessfully */
	FAILED = 1, /**< Unspecified failure */
	ALREADY_OPEN = 2,/**< A board was already open */
	NOT_OPEN = 3,/**< The function cannot execute, because the board or port is not open */
	IIC_ERROR = 4,/**< An error occurred while accessing devices on the BS i2c bus */
	VERSION_MISMATCH = 5,/**< FPGA firmware version mismatch */
	PARAMETER_INVALID = 6,/**< A parameter had an illegal value or out of range */
	UART_ACK_ERROR = 7,/**< uart communication on the serdes link failed to receive an acknowledgement */
	TIMEOUT = 8,/**< the function did not complete within a restricted period of time */
	WRONG_CHANNEL = 9,/**< illegal channel number */
	WRONG_BANK = 10,/**< illegal electrode bank number */
	WRONG_REF = 11,/**< a reference number outside the valid range was specified */
	WRONG_INTREF = 12,/**< an internal reference number outside the valid range was specified */
	CSV_READ_ERROR = 13,/**< an parsing error occurred while reading a malformed CSV file. */
	BIST_ERROR = 14,/**< a BIST operation has failed */
	FILE_OPEN_ERROR = 15,/**< The file could not be opened */
	READBACK_ERROR = 16,/**< a BIST readback verification failed */
	READBACK_ERROR_FLEX = 17,/**< a BIST Flex EEPROM readback verification failed */
	READBACK_ERROR_HS = 18,/**< a BIST HS EEPROM readback verification failed */
	READBACK_ERROR_BSC = 19,/**< a BIST HS EEPROM readback verification failed */
	TIMESTAMPNOTFOUND = 20,/**< the specified timestamp could not be found in the stream */
	FILE_IO_ERR = 21,/**< a file IO operation failed */
	OUTOFMEMORY = 22,/**< the operation could not complete due to insufficient process memory */
	LINK_IO_ERROR = 23,/**< serdes link IO error */
	NO_LOCK = 24,/**< missing serializer clock. Probably bad cable or connection */
	WRONG_AP = 25,/**< AP gain number out of range */
	WRONG_LFP = 26,/**< LFP gain number out of range */
	ERROR_SR_CHAIN_1 = 27,/**< Validation of SRChain1 data upload failed */
	ERROR_SR_CHAIN_2 = 28,/**< Validation of SRChain2 data upload failed */
	ERROR_SR_CHAIN_3 = 29,/**< Validation of SRChain3 data upload failed */
	PCIE_IO_ERROR = 30,/**< a PCIe data stream IO error occurred. */
	NO_SLOT = 31,/**< no Neuropix board found at the specified slot number */
	WRONG_SLOT = 32,/**<  the specified slot is out of bound */
	WRONG_PORT = 33,/**<  the specified port is out of bound */
	STREAM_EOF = 34,
	HDRERR_MAGIC = 35,
	HDRERR_CRC = 36,
	WRONG_PROBESN = 37,
	WRONG_TRIGGERLINE = 38,
	PROGRAMMINGABORTED = 39, /**<  the flash programming was aborted */
	VALUE_INVALID = 40, /**<  The parameter value is invalid */
	NOTSUPPORTED = 0xFE,/**<  the function is not supported */
	NOTIMPLEMENTED = 0xFF/**<  the function is not implemented */
}NP_ErrorCode;

/**
* Operating mode of the probe
*/
typedef enum {
	RECORDING = 0, /**< Recording mode: (default) pixels connected to channels */
	CALIBRATION = 1, /**< Calibration mode: test signal input connected to pixel, channel or ADC input */
	DIGITAL_TEST = 2, /**< Digital test mode: data transmitted over the PSB bus is a fixed data pattern */
}probe_opmode_t;

/**
* Test input mode
*/
typedef enum {
	PIXEL_MODE = 0, /**< HS test signal is connected to the pixel inputs */
	CHANNEL_MODE = 1, /**< HS test signal is connected to channel inputs */
	NO_TEST_MODE = 2, /**< no test mode */
	ADC_MODE = 3, /**< HS test signal is connected to the ADC inputs */
}testinputmode_t;

typedef enum {
	EXT_REF = 0,  /**< External electrode */
	TIP_REF = 1,  /**< Tip electrode */
	INT_REF = 2   /**< Internal electrode */
}channelreference_t;

typedef enum {
	EMUL_OFF = 0, /**< No emulation data is generated */
	EMUL_STATIC = 1, /**< static data per channel: value = channel number */
	EMUL_LINEAR = 2, /**< a linear ramp is generated per channel (1 sample shift between channels) */
}emulatormode_t;

typedef enum {
	SIGNALLINE_NONE           = 0,
	SIGNALLINE_PXI0           = (1 << 0),
	SIGNALLINE_PXI1           = (1 << 1),
	SIGNALLINE_PXI2           = (1 << 2),
	SIGNALLINE_PXI3           = (1 << 3),
	SIGNALLINE_PXI4           = (1 << 4),
	SIGNALLINE_PXI5           = (1 << 5),
	SIGNALLINE_PXI6           = (1 << 6),
	SIGNALLINE_SHAREDSYNC     = (1 << 7),
	SIGNALLINE_LOCALTRIGGER   = (1 << 8),
	SIGNALLINE_LOCALSYNC      = (1 << 9),
	SIGNALLINE_SMA            = (1 << 10),
	SIGNALLINE_SW             = (1 << 11),
	SIGNALLINE_LOCALSYNCCLOCK = (1 << 12)

}signalline_t;

typedef enum {
	TRIGOUT_NONE = 0,
	TRIGOUT_SMA  = 1, /**< PXI SMA trigger output */
	TRIGOUT_PXI0 = 2, /**< PXI signal line 0 */
	TRIGOUT_PXI1 = 3, /**< PXI signal line 1 */
	TRIGOUT_PXI2 = 4, /**< PXI signal line 2 */
	TRIGOUT_PXI3 = 5, /**< PXI signal line 3 */
	TRIGOUT_PXI4 = 6, /**< PXI signal line 4 */
	TRIGOUT_PXI5 = 7, /**< PXI signal line 5 */
	TRIGOUT_PXI6 = 8, /**< PXI signal line 6 */
}triggerOutputline_t;

typedef enum {
	TRIGIN_SW   = 0, /**< Software trigger selected as input */
	TRIGIN_SMA  = 1, /**< PXI SMA line selected as input */

	TRIGIN_PXI0 = 2, /**< PXI signal line 0 selected as input */
	TRIGIN_PXI1 = 3, /**< PXI signal line 1 selected as input */
	TRIGIN_PXI2 = 4, /**< PXI signal line 2 selected as input */
	TRIGIN_PXI3 = 5, /**< PXI signal line 3 selected as input */
	TRIGIN_PXI4 = 6, /**< PXI signal line 4 selected as input */
	TRIGIN_PXI5 = 7, /**< PXI signal line 5 selected as input */
	TRIGIN_PXI6 = 8, /**< PXI signal line 6 selected as input */
	TRIGIN_SHAREDSYNC = 9, /**< shared sync line selected as input */
	
	TRIGIN_SYNCCLOCK  = 10, /**< Internal SYNC clock */

	TRIGIN_USER1 = 11, /**< User trigger 1 (FUTURE) */
	TRIGIN_USER2 = 12, /**< User trigger 2 (FUTURE) */
	TRIGIN_USER3 = 13, /**< User trigger 3 (FUTURE) */
	TRIGIN_USER4 = 14, /**< User trigger 4 (FUTURE) */
	TRIGIN_USER5 = 15, /**< User trigger 5 (FUTURE) */
	TRIGIN_USER6 = 16, /**< User trigger 6 (FUTURE) */
	TRIGIN_USER7 = 17, /**< User trigger 7 (FUTURE) */
	TRIGIN_USER8 = 18, /**< User trigger 8 (FUTURE) */
	TRIGIN_USER9 = 19, /**< User trigger 9 (FUTURE) */

	TRIGIN_NONE = -1 /**< No trigger input selected */
}triggerInputline_t;


typedef void* np_streamhandle_t;

struct np_sourcestats {
	uint32_t timestamp;
	uint32_t packetcount;
	uint32_t samplecount;
	uint32_t fifooverflow;
};

struct np_diagstats {
	uint64_t totalbytes;         /**< total amount of bytes received */
	uint32_t packetcount;        /**< Amount of packets received */
	uint32_t triggers;           /**< Amount of triggers received */
	uint32_t err_badmagic;		 /**< amount of packet header bad MAGIC markers */
	uint32_t err_badcrc;		 /**< amount of packet header CRC errors */
	uint32_t err_droppedframes;	 /**< amount of dropped frames in the stream */
	uint32_t err_count;			 /**< Every psb frame has an incrementing count index. If the received frame count value is not as expected possible data loss has occured and this flag is raised. */
	uint32_t err_serdes;		 /**< incremented if a deserializer error (hardware pin) occured during receiption of this frame this flag is raised */
	uint32_t err_lock;			 /**< incremented if a deserializer loss of lock (hardware pin) occured during receiption of this frame this flag is raised */
	uint32_t err_pop;			 /**< incremented whenever the ‘next blocknummer’ round-robin FiFo is flagged empty during request of the next value (for debug purpose only, irrelevant for end-user software) */
	uint32_t err_sync;			 /**< Front-end receivers are out of sync. => frame is invalid. */
};

typedef struct {
	uint32_t MAGIC; // includes 'Type' field as lower 4 bits

	uint16_t samplecount;
	uint8_t seqnr;
	uint8_t format;

	uint32_t timestamp;

	uint8_t status;
	uint8_t sourceid;
	uint16_t crc;

}pckhdr_t;


/********************* Parameter configuration functions ****************************/
#define MINSTREAMBUFFERSIZE (1024*32)
#define MAXSTREAMBUFFERSIZE (1024*1024*32)
#define MINSTREAMBUFFERCOUNT (2)
#define MAXSTREAMBUFFERCOUNT (1024)
typedef enum {
	NP_PARAM_BUFFERSIZE       = 1,
	NP_PARAM_BUFFERCOUNT      = 2,
	NP_PARAM_SYNCMASTER       = 3,
	NP_PARAM_SYNCFREQUENCY_HZ = 4,
	NP_PARAM_SYNCPERIOD_MS    = 5,
	NP_PARAM_SYNCSOURCE       = 6,
	NP_PARAM_SIGNALINVERT     = 7,
}np_parameter_t;

NP_EXPORT NP_ErrorCode NP_APIC setParameter(np_parameter_t paramid, int value);
NP_EXPORT NP_ErrorCode NP_APIC getParameter(np_parameter_t paramid, int* value);
NP_EXPORT NP_ErrorCode NP_APIC setParameter_double(np_parameter_t paramid, double value);
NP_EXPORT NP_ErrorCode NP_APIC getParameter_double(np_parameter_t paramid, double* value);

/********************* Opening and initialization functions ****************************/

/**
* @brief returns get a mask of available PXI slots.
* @return SUCCESS if the scan completed successfully.
*/
NP_EXPORT NP_ErrorCode NP_APIC scanPXI(uint32_t* availableslotmask);

/**
* @brief The ‘openBS’ function initializes the BS FPGA and BSC FPGA and opens the communication channel
*
* - BS FPGA reset
* - Check hardware and software versions : BSC FPGA, BS FPGA, API
*
* @param slotID : which slot in the PXI chassis (valid range depends on the chassis)
*
* @return SUCCESS if successful, NO_SLOT if no Neuropix BS card is plugged in the selected PXI chassis slot, WRONG_SLOT if the slot number is out of range for the chassis, VERSION_MISMATCH if API and BS FPGA version are not compatible, IIC_ERROR in case of error on the I2C bus on the BS card, ALREADY_OPEN if function called twice.
*/
NP_EXPORT	NP_ErrorCode NP_APIC openBS(unsigned char slotID);

/**
* @brief The ‘closeBS’ function closes the BS connection 
* Close access and teardown communication with BS
*
* @param slotID : which slot in the PXI chassis (valid range depends on the chassis)
*
* @return SUCCESS if successful, NOT_OPEN if no Neuropix BS card was open on this slot. WRONG_SLOT if the slot number is out of range for the chassis.
*/
NP_EXPORT	NP_ErrorCode NP_APIC closeBS(unsigned char slotID);

/**
* @brief The ‘openProbe’ function enables the power supply to the cable to the HS. The function initializes the serdes link and HS, but not the probe itself. The argument selects which of the 4 headstage ports on the BSC to enable.
* Calling the ‘openProbe’ function with a certain port number does not close any previously opened ports. The ‘openProbe’ function initializes the serdes and HS:
* - Enable the power supply on the cable to the HS, via the EN_HSx signal from the BSC FPGA (ref. [BSC]).
* - Configure the deserializer registers as described in [BSC].
* - Configure the serializer registers as described in [HS].
* - Set the DIG_NRESET bit in the REC_MOD register of the probe memory map to 0. Wait 1ms. Set the DIG_NRESET bit in the REC_MOD register to 1.
* - Set the REC bit in the OP_MODE register of the probe memory map to 1 (required to enable the PSB_SYNC signal).
* - Set the REC_NRST_IN signal of the BSC FPGA high via the AXI chip2chip interface [BSC]. This signal is transmitted via the GPI/GPO channel of the serdes to the probe, and will enable the PSB bus. The PSB_SYNC line is visualized as a heartbeat signal on the BSC.
* - Set the GPIO1 signal from the serializer high [HS]. This makes the heartbeat signal visible on the HS.
* - Set BS FPGA for this port in electrode mode.
* - Enable data zeroing on BS FPGA, enable Lock checking.
* The ‘openProbe’ function should execute fast (<500ms), such that the user can use the ‘openProbe’ function to quickly query if a port has hardware connected.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: which HS/probe (valid range 1 to 4)
* @return SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe, ALREADY_OPEN if function called twice.).
*/
NP_EXPORT	NP_ErrorCode NP_APIC openProbe(unsigned char slotID, signed char port);

/*
	Similar as openProbe, but opens the port/probe only for Headstage Tester operation
*/
NP_EXPORT	NP_ErrorCode NP_APIC openProbeHSTest(unsigned char slotID, signed char port);


/**
* @brief Initialize
* The function resets the connected probe to the default settings: load the default settings for configuration registers and memory map; and subsequently initialize the probe in recording mode
* Set the memory map to the default values (ref. 3.1.3).
* - Set the test configuration register map to the default values (ref. 3.1.3).
* - Set the GPIO1 signal from the serializer low ((serializer register 0x0E and 0x0F, ref. [HS]). This makes the heartbeat signal no longer visible on the HS.
* - Set the shank configuration register map to the default values indicated in [Shank configuration].
* - Set the base configuration register map to the default values indicated in [Base configuration], excluding the ADC comparator values (ADCxxSlope, ADCxxFine, ADCxxCoarse, ADCxxCfix, ADCxxCompP, ADCxxCompN).
* - Set the REC bit in the OP_MODE register in the memory map to high (ref. 3.1.3). All other bits in the OP_MODE register are set low.
* - Set the PSB_F bit in the REC_MOD register in the memory map to high (ref. 3.1.3).
*
* @param slotID which slot in the PXI chassis (valid range depends on the chassis)
* @param port which HS/probe (valid range 1 to 4)
* @return SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC init(unsigned char slotID, signed char port);

/*
* @brief Load calibration data
* The probe calibration is programmed via the probes’ base configuration register. The probe calibration data is stored in a .csv file.
* The following function reads the .csv file containing the calibration data, updates the base configuration register variable in the API and subsequently writes the base configuration register to the probe. The function also checks if the selected calibration file is for the connected probe, by checking the S/N of the connected probe with the S/N in the calibration csv file.
* This function sets the ADC calibration values (compP and compN, Slope, Coarse, Fine and Cfix):
* The first row of the ADC calibration csv file contains the probes’ serial number. Below the first row are 7 columns of data:
*   - First column: ADC number (1-32)
*   - Second column: CompP calibration factor in hex format
*   - Third column: CompN calibration factor in hex format
*   - Fourth column: Cfix calibration factor in hex format
*   - Fifth column: Slope calibration factor in hex format
*   - Sixth column: Coarse calibration factor in hex format
*   - Seventh column: Fine calibration factor in hex format
* The name of the file is: [ASIC’s serial number]_ADC_Calibration.csv
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param filename: the filename to read from (.csv)
* @returns: SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe). WRONG_PROBESN is the Probe serial number does not match
*/
NP_EXPORT	NP_ErrorCode NP_APIC setADCCalibration(unsigned char slotID, signed char port, const char* filename);

/* @brief Set the gain correction data
* The probe gain correction data is stored in a csv file. There is a gain correction factor for each electrode, both for AP and LFP, and for each gain setting. The gain correction parameter is loaded to the basestation FPGA, where it is applied in the scale module (ref. chapter 4.2).
* The following function reads the gain correction parameters from the specified .csv file and writes these to the BS FPGA. The function also checks if the selected gain correction file is for the connected probe, by checking the S/N of the connected probe with the S/N in the gain correction csv file.
* The first row of the gain correction csv file contains the probes’ serial number. Below the first row are 3 columns of data:
*    - first column: electrode number (1 – 960),
*    - 2nd to 9th column: AP gain correction factors for AP gain x50 to 3000 (ref. chapter 5.7.6: ‘ap_gain’ parameter values 0 to 7).
*    - 10th to 17th column: LFP gain correction factors for LFP gains x50 to 3000 (ref. chapter 5.7.6: ‘lfp_gain’ parameter values 0 to 7).
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns: SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC setGainCalibration(unsigned char slotID, signed char port, const char* filename);

/* @brief Close
* The ‘close’ function shuts down the power supply to the cable on the selected port, via the EN_HSx signal from the BSC FPGA (ref. [BSC]). In case the ‘port’ argument is set to -1, all ports on the BSC are shut down PXIe link is released.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range -1 to 3)
* @returns SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC close(unsigned char slotID, signed char port);

/* @brief Log file
* The system can log commands an status information to a text file (api_log.txt). This functionality is default disabled, after calling the ‘open’ function.
* The log is saved in separate text files per serdes port and per PXI slot. The log file name contains the serdes port number and PXI slot number.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param enable: enable (true) or disable (false) the logging
* @returns SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setLog(unsigned char slotID, signed char port, bool enable);


/********************* Interface to Base station FPGA memory map ****************************/
/* @brief Write to base station memory map
* This function allows the user to write 1 data byte to a specified address on the BSC FPGA memory map
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param register: the register address to write to
* @param data: the data word to write
* @returns SUCCESS correct acknowledgment byte returned by the slave, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC writeBSCMM(unsigned char slotID, uint32_t address, uint32_t data);

/* @brief Read from base station memory map
* this functions reads 1 data byte from a specified address on the BSC FPGA memory map
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param register: the register address to read from
* @param data: the data word read
* @returns SUCCESS correct acknowledgment byte returned by the slave, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC readBSCMM(unsigned char slotID, uint32_t address, uint32_t* data);

/********************* UART/I2C interface to serdes ports ****************************/

/* @brief Write to I2C bus
* this function allows the user to write N data bytes to a specified address on a slave device.
* Writing more than 1 byte to the probes’ memory map is only applicable for register addresses related to the shift registers. For all other register addresses only 1 byte should be written.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param device: the device address (slave) to write to
* @param register: the register address to write to
* @param data: the date to write
* @param size: amoutn of bytes to write
* @returns SUCCESS correct acknowledgment byte returned by the slave, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC writeI2C(unsigned char slotID, signed char port, unsigned char device, unsigned char address, unsigned char data);

/* @brief Read from I2C bus
* This functions reads N data bytes from a specified address on a slave device
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param device: the device address (slave) to read from
* @param register: the register address to read from
* @param data: vector containing the data read over the I2C bus
* @param size: the number of bytes to read
* @returns SUCCESS correct acknowledgment byte returned by the slave, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC readI2C(unsigned char slotID, signed char port, unsigned char device, unsigned char address, unsigned char* data);

/********************* Hardware/software versions ****************************/

/* @brief Read the Head Stage version from EEPROM memory
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param version_major: the HS board version number
* @param version_build: the HS board build number (NULL allowed)
* @returns SUCCESS correct acknowledgment byte returned by the slave, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC getHSVersion(unsigned char slotID, signed char port, unsigned char* version_major, unsigned char* version_minor);


/*
* @brief Get the API software version
*
* @param version_major: the API version number
* @param version_minor: the API revision number
*/
NP_EXPORT	void  NP_APIC getAPIVersion(unsigned char* version_major, unsigned char* version_minor);

/**
* @brief Get the BSC FPGA boot code version
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param version_major: the BSC FPGA boot code version number
* @param version_minor: the BSC FPGA boot code revision number
* @param version_build: the BSC FPGA boot code build number
* @returns SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered,
*/
NP_EXPORT	NP_ErrorCode NP_APIC getBSCBootVersion(unsigned char slotID, unsigned char* version_major, unsigned char* version_minor, uint16_t* version_build);

/**
* @brief Get the BS FPGA boot code version
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param version_major: the BS FPGA boot code version number
* @param version_minor: the BS FPGA boot code revision number
* @param version_build: the BS FPGA boot code build number (NULL allowed)
* @returns SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered,
*/
NP_EXPORT	NP_ErrorCode NP_APIC getBSBootVersion(unsigned char slotID, unsigned char* version_major, unsigned char* version_minor, uint16_t* version_build);

/**
* \brief Read the BSC hardware version from the EEPROM memory
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param version_major: the BSC FPGA boot code version number
* @param version_minor: the BSC FPGA boot code revision number
* @param version_build: the BSC FPGA boot code build number (NULL allowed)
* @returns NO_LINK if no datalink, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered
*/
NP_EXPORT	NP_ErrorCode NP_APIC getBSCVersion(unsigned char slotID, unsigned char* version_major, unsigned char* version_minor);




/********************* Serial Numbers ****************************/

/**
* @brief Read the probe ID
* The probe ID is stored on the EEPROM memory on the flex. The probe ID is a 16 digit number.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param id: the probe ID code to return
* @returns NO_LINK if no datalink, TIMEOUT if no I2C acknowledgement is received, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC readId(unsigned char slotID, signed char port, uint64_t* id);



NP_EXPORT	NP_ErrorCode NP_APIC readProbePN(unsigned char slotID, signed char port, char* pn,size_t len);
NP_EXPORT	NP_ErrorCode NP_APIC getFlexVersion(unsigned char slotID, signed char port, unsigned char* version_major, unsigned char* version_minor);
NP_EXPORT	NP_ErrorCode NP_APIC readFlexPN(unsigned char slotID, signed char port, char* pn, size_t len);


/**
* @brief Get the headstage serial number
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param id: the probe ID code to return
* @returns NO_LINK if no datalink, TIMEOUT if no I2C acknowledgement is received, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC readHSSN(unsigned char slotID, signed char port, uint64_t* sn);




NP_EXPORT	NP_ErrorCode NP_APIC readHSPN(unsigned char slotID, signed char port, char* pn,size_t maxlen);


/**
* @brief Read the BSC serial number from EEPROM
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param sn: the BSC S/N to return
* @returns NO_LINK if no datalink, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC readBSCSN(unsigned char slotID, uint64_t* sn);

/**
* @brief Write the BSC serial number to EEPROM
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param sn: the BSC S/N to return
* @returns NO_LINK if no datalink, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC writeBSCSN(unsigned char slotID, uint64_t sn);

NP_EXPORT	NP_ErrorCode NP_APIC readBSCPN(unsigned char slotID,  char* pn, size_t len);
NP_EXPORT	NP_ErrorCode NP_APIC writeBSCPN(unsigned char slotID, const char* pn);

/********************* System Configuration ****************************/

/**
* @brief Enable or disable the head stage heartbeat LED
* The HS LED heartbeat blinking is enabled/disabled by the GPIO1 signal which is controlled through serializer registers.
* The default blinking status of the HS LED after calling the ‘open’ function is enabled. The default status after calling the ‘init’ function is disabled.
* The function sets the GPIO1 signal from the serializer (serializer register 0x0E and 0x0F, ref. [HS]). This makes the heartbeat signal visible on the HS.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param enable: enable (true) or disable (false) HS heartbeat LED
* @returns SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
*/
NP_EXPORT	NP_ErrorCode NP_APIC setHSLed(unsigned char slotID, signed char port, bool enable);

/**
* @brief Set the ADC operating mode
* The function sets the system in ADC mode or electrode mode. This mode defines how data is demuxed on the BS FPGA and transmitted in packets to the PC. The default status after calling the ‘open’ function is electrode mode.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param mode: electrode (true) or ADC (false) mode
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setDataMode(unsigned char slotID, bool mode);
NP_EXPORT	NP_ErrorCode NP_APIC getDataMode(unsigned char slotID, bool* mode);

/**
* @brief Read the temperator of the BS FPGA
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param temperature: the BS temperature, in degrees Celsius.
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC getTemperature(unsigned char slotID, float* temperature);

/**
* @brief Enable or disable the HS test signal
* The HS contains a test signal generator which can be used for probe integrity checks. The output of the test signal generator is connected to the CAL_SIGNAL input of the probe.
* The test signal on the HS is enabled by a gate signal coming from the probe which is controlled via a register in the probes’ memory map. The test signal is default off after calling the ‘init’ function.
* The function sets the OSC_STDB bit in the CAL_MOD register of the probe memory map. Asserting the bit enables the test signal.
*
@param slotID: which slot in the PXI chassis (valid range depends on the chassis)
@param port: for which HS (valid range 1 to 4)
@param enable: enable (true) or disable (false) the test signal.
@returns SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setTestSignal(unsigned char slotID, signed char port, bool enable);

/********************* Probe Configuration ****************************/

/**
* @brief set the probe operating mode
* The function supports the following modes:
*   - Recording: the default operation mode. The pixels are connected to the channels. The recorded signal is digitized and output on the PSB bus. Set the REC bit in the OP_MODE register high. All the other bits in the OP_MODE register are set low.
*   - Calibration: the test signal input (CAL_SIGNAL) is connected to either the pixel, channel or ADC input (selected via the CAL_MOD register). The recorded signal is digitized and output on the PSB bus. Set the CAL and REC bit in the OP_MODE register high. All the other bits in the OP_MODE register are set low.
*   - Digital test: the data transmitted over the PSB bus is a fixed data pattern. Set the DIG_TEST and REC bit in the OPMODE register to activate this mode. All the other bits in the OP_MODE register are set low.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param mode: the selected probe operation mode.
* @returns SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received , NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setOPMODE(unsigned char slotID, signed char port, probe_opmode_t mode);

/**
* @brief set the test signal input mode
* The CAL_SIGNAL input of the probe, which is connected to the HS test signal via the HS and flex, can be connected to either the probes’ pixel inputs, channel inputs, or ADC inputs. The following function configures the CAL_MOD register of the probes’ memory map.
* The function supports the following modes:
*   - Pixel: the HS test signal is connected to the pixel inputs. Set the PIX_CAL bit in the CAL_MOD register to activate this mode. All other bits in the CAL_MOD register are set low.
*   - Channel: the HS test signal is connected to the channel inputs. Set the CH_CAL bit in the CAL_MOD register to activate this mode. All other bits in the CAL_MOD register are set low.
*   - None: All bits in the CAL_MOD register are set low.
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param mode: the selected test signal mode
* @returns SUCCESS if successful, TIMEOUT if no I2C acknowledgement is received , NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setCALMODE(unsigned char slotID, signed char port,	testinputmode_t mode);

/**
* @brief Recording reset
* The following function sets/resets the REC_NRESET signal to the probe. The REC_NRESET is controlled via the serdes link by the REC_NRST output pin of the BSC FPGA (ref [BSC]).
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param value: logic high (true) or logic low (false)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setREC_NRESET(unsigned char slotID, signed char port, bool value);

/**
* @brief Set which electrode is connected to a channel.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param channel: the channel number (valid range: 0 to 383, excluding 191)
* @param electrode_bank: the electrode bank number to connect to (valid range: 0 to 2 or 0xFF to disconnect)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the range is entered, WRONG_BANK in case an electrode bank number outside the range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC selectElectrode(unsigned char slotID, signed char port, uint32_t channel, uint8_t electrode_bank);

/**
* @brief Set the channel reference of the given channel.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param channel: the channel number (valid range: 0 to 383)
* @param reference: the sleected reference input (valid range: 0 to 2)
* @param intRefElectrodeBank: the selected internal reference electrode (valid range: 0 to 2)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the valid range is entered, WRONG_REF in case a reference number outside the valid range is entered, WRONG_INTREF in case a internal reference electrode number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setReference(unsigned char slotID, signed char port, unsigned int channel, channelreference_t reference, uint8_t intRefElectrodeBank);

/**
* @brief Set the AP and LFP gain of the given channel.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param channel: the channel number (valid range: 0 to 383)
* @param ap_gain: the AP gain value (valid range: 0 to 7)
* @param lfp_gain: the LFP gain value (valid range: 0 to 7)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the valid range is entered, WRONG_AP in case an AP gain number outside the valid range is entered, WRONG_LFP in case an LFP gain number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setGain(unsigned char slotID, signed char port, unsigned int channel, unsigned char ap_gain, unsigned char lfp_gain);

/**
* @brief Get the AP and LFP gain of the given channel.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param channel: the channel number (valid range: 0 to 383)
* @param ap_gain: the AP gain value (valid range: 0 to 7)
* @param lfp_gain: the LFP gain value (valid range: 0 to 7)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the valid range is entered.
*/
NP_EXPORT  NP_ErrorCode NP_APIC getGain(uint8_t slotID, int8_t port, int channel, int* APgainselect, int* LFPgainselect);

/**
* @brief Set the high-pass corner frequency for the given AP channel.
* The function checks whether the input parameters ‘slotID’ and ‘port’ are valid and updates the base configuration register variable in the API. The function does not transmit the base configuration shift register to the memory map of the probe.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param channel: the channel number (valid range: 0 to 383)
* @param disableHighPass: the highpass cut-off frequency of the AP channels
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setAPCornerFrequency(unsigned char slotID, signed char port, unsigned int channel,	bool disableHighPass);

/**
* @brief Set the given channel in stand-by mode.
* The function checks whether the input parameters ‘slotID’ and ‘port’ are valid and updates the base configuration register variable in the API. The function does not transmit the base configuration shift register to the memory map of the probe.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param channel: the channel number (valid range: 0 to 383)
* @param standby: the standby value to write
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setStdb(unsigned char slotID, signed char port, unsigned int channel, bool standby);

/**
* @brief Write probe configuration settings to the probe.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param readCheck : if enabled, read the configuration shift registers back to check
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, WRONG_CHANNEL in case a channel number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC writeProbeConfiguration(unsigned char slotID, signed char port, bool readCheck);

/********************* Trigger Configuration ****************************/
/**
* \brief Re-arm the data capture trigger
* In anticipation of receiving a start trigger, the system is set in ‘arm’ mode. In ‘arm’ mode, neural data packets from the probe are not buffered in the FIFO on the basestation, and the time stamp is fixed at 0. Upon receiving the start trigger, the system starts to buffer the incoming neural data in the basestation FIFO buffer and start the timestamp generator.
* After the system has received a start trigger and is buffering incoming neural data, calling the API ‘arm’ function again stops the buffering of neural data packets, clears the basestation FIFO, stops the time stamp generator and resets the timestamp to 0.
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC arm(unsigned char slotID);


NP_EXPORT	NP_ErrorCode NP_APIC setTriggerBinding(uint8_t slotID, signalline_t outputline, signalline_t inputlines);
NP_EXPORT	NP_ErrorCode NP_APIC getTriggerBinding(uint8_t slotID, signalline_t outputline, signalline_t* inputlines);
/**
* \brief Select the source of the trigger
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param source: the trigger source as a selection mask
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_TRIGGER in case a source number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setTriggerInput(uint8_t slotID, triggerInputline_t inputline);
NP_EXPORT	NP_ErrorCode NP_APIC getTriggerInput(uint8_t slotID, triggerInputline_t* input);

NP_EXPORT	NP_ErrorCode NP_APIC setTriggerOutput(uint8_t slotID, triggerOutputline_t line, triggerInputline_t inputline);
NP_EXPORT	NP_ErrorCode NP_APIC getTriggerOutput(uint8_t slotID, triggerOutputline_t* output, triggerInputline_t* source);
//NP_EXPORT	NP_ErrorCode NP_APIC getTriggerOutput(uint8_t slotID, triggerOutputline_t line, triggerInputline_t* inputline);

NP_EXPORT  NP_ErrorCode NP_APIC setTriggerEdge(unsigned char slotID, bool rising);
/**
* \brief Generate a software trigger
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC setSWTrigger(unsigned char slotID);


/********************* Built In Self Test ****************************/

/**
* @brief Basestation platform BIST
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistBS(unsigned char slotID);

/**
* @brief Head Stage heartbeat test
* The heartbeat signal generated by the PSB_SYNC signal of the probe. The PSB_SYNC signal starts when the probe is powered on, the OP_MODE register in the probes’ memory map set to 1, and the REC_NRESET signal set high.
* The heartbeat signal is visible on the headstage (can be disabled by API functions) and on the BSC. This is in the first place a visual check.
* In order to facilitate a software check of the BSC heartbeat signal, the PSB_SYNC signal is also routed to the BS FPGA. A function is provided to check whether the PSB_SYNC signal contains a 0.5Hz clock.
* The presence of a heartbeat signal acknowledges the functionality of the power supplies on the headstage for serializer and probe, the POR signal, the presence of the master clock signal on the probe, the functionality of the clock divider on the probe, an basic communication over the serdes link.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistHB(unsigned char slotID, signed char port);

/**
* @brief Start Serdes PRBS test
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistStartPRBS(unsigned char slotID, signed char port);

/**
* @brief Stop Serdes PRBS test
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param prbs_err: the number of prbs errors
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistStopPRBS(unsigned char slotID, signed char port, unsigned char* prbs_err);

/**
* @brief Test I2C memory map access
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered, NO_ACK in case no acknowledgment is received, READBACK_ERROR in case the written and readback word are not the same.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistI2CMM(unsigned char slotID, signed char port);

/**
* @brief Test all EEPROMs (Flex, headstage, BSC). by verifying a write/readback cycle on an unused memory location
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered, NO_ACK_FLEX in case no acknowledgment is received from the flex eeprom, READBACK_ERROR_FLEX in case the written and readback word are not the same from the flex eeprom, NO_ACK_HS in case no acknowledgment is received from the HS eeprom, READBACK_ERROR_HS in case the written and readback word are not the same from the HS eeprom, NO_ACK_BSC in case no acknowledgment is received from the BSC eeprom, READBACK_ERROR_BSC in case the written and readback word are not the same from the BSC eeprom.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistEEPROM(unsigned char slotID, signed char port);


/**
* @brief Test the shift registers
* This test verifies the functionality of the shank and base shift registers (SR_CHAIN 1 to 3). The function configures the shift register two times with the same code. After the 2nd write cycle the SR_OUT_OK bit in the STATUS register is read. If OK, the shift register configuration was successful. The test is done for all 3 registers. The configuration code used for the test is a dedicated code (to make sure the bits are not all 0 or 1).
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered, ERROR_SR_CHAIN_1 in case the SR_OUT_OK bit is not ok when writing SR_CHAIN_1, ERROR_SR_CHAIN_2 in case the SR_OUT_OK bit is not ok when writing SR_CHAIN_2, ERROR_SR_CHAIN_3 in case the SR_OUT_OK bit is not ok when writing SR_CHAIN_3.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistSR(unsigned char slotID, signed char port);

/**
* @brief Test the PSB bus on the headstage
* A test mode is implemented on the probe which enables the transmission of a known data pattern over the PSB bus. The following function sets the probe in this test mode, records a small data set, and verifies whether the acquired data matches the known data pattern.
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistPSB(unsigned char slotID, signed char port);

/**
* @brief The probe is configured for noise analysis. Via the shank and base configuration registers and the memory map, the electrode inputs are shorted to ground. The data signal is recorded and the noise level is calculated. The function analyses if the probe performance falls inside a specified tolerance range (go/no-go test).
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @returns SUCCESS if successful, BIST_ERROR of test failed. NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered.
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistNoise(unsigned char slotID, signed char port);

struct bistElectrodeStats {
	double peakfreq_Hz;
	double min;
	double max;
	double avg;
};

/**
* @brief The probe is configured for recording of a test signal which is generated on the headstage. This configuration is done via the shank and base configuration registers and the memory map. The data signal is recorded and the frequency and amplitude of the recorded signal are extracted for each electrode. The function analyses if the probe performance falls inside specified a tolerance range (go/no-go test).
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param pass: true if >=90% of the electrodes passed the test sucessfully
* @param stats: Optionally output argument (NULL if not used). If used, input is an array of size 960, which gets populated by electrode signal statistics in mV
*
* @returns SUCCESS if successful, BIST_ERROR of test failed. NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the valid range is entered, WRONG_PORT in case a port number outside the valid range is entered.
*
*/
NP_EXPORT	NP_ErrorCode NP_APIC bistSignal(uint8_t slotID, int8_t port, bool* pass, struct bistElectrodeStats* stats);
/********************* Data Acquisition ****************************/


/**
* @brief Open an acquisition stream from an existing file.
* @param filename Specifies an existing file with probe acquisition data.
* @param port specifies the target port
* @param lfp if true, specifies that LFP data will be extracted. otherwise AP data only
* @param stream a pointer to the stream pointer that will receive the handle to the opened stream
* @param filename Specifies an existing file with probe acquisition data.
* @returns FILE_OPEN_ERROR if unable to open file
*/
NP_EXPORT	NP_ErrorCode NP_APIC streamOpenFile(const char* filename, int8_t port, bool lfp, np_streamhandle_t* pstream);

/**
* @brief Closes an acquisition stream.
* Closes the stream along with the optional recording file.
* @returns (TBD)
*/
NP_EXPORT	NP_ErrorCode NP_APIC streamClose(np_streamhandle_t stream);

/**
* @brief Moves the stream pointer to given timestamp.
* Stream seek is only supported on streams that are backed by a recording file store.
* @param stream: the acquisition stream handle
* @param filepos: The file position to navigate to.
* @param actualtimestamp: returns the timestamp at the stream pointer (NULL allowed)
* @returns TIMESTAMPNOTFOUND if no valid data packet is found beyond the specified file position
*/
NP_EXPORT	NP_ErrorCode NP_APIC streamSeek(np_streamhandle_t stream, uint64_t filepos, uint32_t* actualtimestamp);

NP_EXPORT	NP_ErrorCode NP_APIC streamSetPos(np_streamhandle_t sh, uint64_t filepos);

/**
* @brief Report the current file position in the filestream.
* @param stream: the acquisition stream handle
* @returns the current file position at the stream cursor position.
*/
NP_EXPORT	uint64_t NP_APIC streamTell(np_streamhandle_t stream);

/**
* @brief read probe data from a recorded file stream.
* Example:
*    #define SAMPLECOUNT 128
*    uint16_t interleaveddata[SAMPLECOUNT * 384];
*    uint32_t timestamps[SAMPLECOUNT];
*
*    np_streamhandle_t sh;
*    streamOpenFile("myrecording.bin",1, false, &sh);
*    streamRead(sh, timestamps, interleaveddata, SAMPLECOUNT);
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param timestamps: Optional timestamps buffer (NULL if not used). size should be 'samplecount'
* @param data: buffer of size samplecount*384. The buffer will be populated with channel interleaved, 16 bit per sample data.
* @returns amount of actual time stamps read.
*/
NP_EXPORT int NP_APIC streamRead(
	np_streamhandle_t sh,
	uint32_t* timestamps,
	int16_t* data,
	int samplecount);

NP_EXPORT NP_ErrorCode NP_APIC streamReadPacket(
	np_streamhandle_t sh,
	pckhdr_t* header,
	int16_t* data,
	size_t elementstoread, 
	size_t* elementread);

/**
* @brief Blocking live read from the AP Fifo. 
* Example:

*    #define SAMPLECOUNT 128
*    uint16_t interleaveddata[SAMPLECOUNT * 384];
*    uint32_t timestamps[SAMPLECOUNT];
*
*    readAPFifo(0,0, timestamps, interleaveddata, SAMPLECOUNT);
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param timestamps: Optional timestamps buffer (NULL if not used). size should be 'samplecount'
* @param data: buffer of size samplecount*384. The buffer will be populated with channel interleaved, 16 bit per sample data.
* @returns amount of actual time stamps read.
*/
NP_EXPORT size_t NP_APIC readAPFifo(uint8_t slotid, uint8_t port, uint32_t* timestamps, int16_t* data, int samplecount);

/**
* @brief Blocking live read from the LFP Fifo.
* Example:

*    #define SAMPLECOUNT 128
*    uint16_t interleaveddata[SAMPLECOUNT * 384];
*    uint32_t timestamps[SAMPLECOUNT];
*
*    readAPFifo(0,0, timestamps, interleaveddata, SAMPLECOUNT);
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param timestamps: Optional timestamps buffer (NULL if not used). size should be 'samplecount'
* @param data: buffer of size samplecount*384. The buffer will be populated with channel interleaved, 16 bit per sample data.
* @returns amount of actual time stamps read.
*/
NP_EXPORT size_t NP_APIC readLFPFifo(unsigned char slotid, signed char port, uint32_t* timestamps, int16_t* data, int samplecount);

NP_EXPORT size_t NP_APIC readADCFifo(unsigned char slotid, signed char port, uint32_t* timestamps, int16_t* data, int samplecount);

/**
* @brief Blocking live read from the electrode data Fifo.
* Example:

*    #define SAMPLECOUNT 128
*    struct electrodePacket[SAMPLECOUNT];
*    size_t count = SAMPLECOUNT;
*    readElectrodeData(1,1, &electrodePacket[0], &count, count);
*
* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param packets: read buffer to copy the packets from the fifo to.
* @param actualAmount: actual amount of packets read from the fifo.
* @param requestedAmount: amount of packets to try to read from the fifo.
*/
NP_EXPORT NP_ErrorCode NP_APIC readElectrodeData(
										unsigned char slotid, 
										signed char port, 
										struct electrodePacket* packets, 
										size_t* actualAmount, 
										size_t requestedAmount);

/**
* @brief Get the filling state of the ElectrodeDataFifo.
*
* @param slotid: which slot in the PXI chassis (valid range depends on the chassis)
* @param port: for which HS (valid range 1 to 4)
* @param packetsavailable: returns the amount unread of packets in the fifo. NULL allowed for no return.
* @param headroom: returns the amount of space left in the fifo. NULL allowed for no return.
*/
NP_EXPORT NP_ErrorCode NP_APIC getElectrodeDataFifoState(
										unsigned char slotid, 
										signed char port, 
										size_t* packetsavailable, 
										size_t* headroom);

/*** TEST MODULE FUNCTIONS *****/
NP_EXPORT NP_ErrorCode NP_APIC HSTestVDDA1V2(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestVDDD1V2(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestVDDA1V8(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestVDDD1V8(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestOscillator(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestMCLK(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestPCLK(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestPSB(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestI2C(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestNRST(uint8_t slotID, int8_t port);
NP_EXPORT NP_ErrorCode NP_APIC HSTestREC_NRESET(uint8_t slotID, int8_t port);

/********************* Firmware update functions ****************************/
NP_EXPORT NP_ErrorCode NP_APIC qbsc_update(unsigned char  slotID, const char* filename, int(*callback)(size_t byteswritten));
NP_EXPORT NP_ErrorCode NP_APIC bs_update(unsigned char  slotID, const char* filename, int(*callback)(size_t byteswritten));

/********************* Stream API ****************************/
NP_EXPORT NP_ErrorCode NP_APIC setFileStream(unsigned char  slotID, const char* filename);
NP_EXPORT NP_ErrorCode NP_APIC enableFileStream(unsigned char  slotID, bool enable);

NP_EXPORT NP_ErrorCode NP_APIC getADCparams(unsigned char slotID, signed char port, int adcnr, struct ADC_Calib* data);
NP_EXPORT NP_ErrorCode NP_APIC setADCparams(unsigned char slotID, signed char port, const struct ADC_Calib* data);

NP_EXPORT const char* np_GetErrorMessage(NP_ErrorCode code);

#ifdef __cplusplus
}
#endif	
