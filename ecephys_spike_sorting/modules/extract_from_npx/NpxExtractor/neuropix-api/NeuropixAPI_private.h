#pragma once

#include "NeuropixAPI.h"

#ifdef __cplusplus
extern "C" {
#endif	

	typedef enum
	{
		ChannelType_None = 0,
		ChannelType_LFP = (1 << 0),
		ChannelType_AP = (1 << 1),
		ChannelType_ADC = (1 << 2)
	}channeltype_t;

	struct probechannelstatistics {
		uint32_t channelnr;
		uint32_t samplecount;
		double min;
		double max;
		double avg;
		double stddev;
	};

	/********************* Non volatile memory write functions ****************************/
	/**
	* \brief Write the BSC version data to the EEPROM memory
	*
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @param version_major: the BSC FPGA boot code version number
	* @param version_minor: the BSC FPGA boot code revision number
	* @returns NO_LINK if no datalink, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC setBSCVersion(unsigned char slotID, unsigned char version_major, unsigned char version_minor);
	/* @brief Write the Head Stage version to EEPROM memory
	*
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @param port: for which HS (valid range 0 to 3)
	* @param version_major: the HS board version number
	* @param version_minor: the HS board revision number
	* @param version_build: the HS board build number (NULL allowed)
	* @returns SUCCESS correct acknowledgment byte returned by the slave, TIMEOUT if no I2C acknowledgement is received, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC setHSVersion(unsigned char slotID, signed char port, unsigned char version_major, unsigned char version_minor);

	/**
	* @brief Write probe ID
	* The probe ID is stored on the EEPROM memory on the flex. The probe ID is a 16 digit number.
	*
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @param port: for which HS (valid range 0 to 3)
	* @param id: the probe ID code to return
	* @returns NO_LINK if no datalink, TIMEOUT if no I2C acknowledgement is received, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC writeId(unsigned char slotID, signed char port, uint64_t id);
	NP_EXPORT	NP_ErrorCode NP_APIC writeProbePN(unsigned char slotID, signed char port, const char* pn);
	NP_EXPORT	NP_ErrorCode NP_APIC setFlexVersion(unsigned char slotID, signed char port, unsigned char version_major, unsigned char version_minor);
	NP_EXPORT	NP_ErrorCode NP_APIC writeFlexPN(unsigned char slotID, signed char port, const char* pn);
	/**
	* @brief Write the headstage serial number to EEPROM
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @param port: for which HS (valid range 0 to 3)
	* @param id: the probe ID code to return
	* @returns NO_LINK if no datalink, TIMEOUT if no I2C acknowledgement is received, SUCCESS if successful, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered, WRONG_PORT in case a port number outside the range is entered, NO_LOCK if no clock signal arrives at the deserializer (=missing or malfunctioning cable, HS or probe).
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC writeHSSN(unsigned char slotID, signed char port, uint64_t sn);
	NP_EXPORT	NP_ErrorCode NP_APIC writeHSPN(unsigned char slotID, signed char port, const char* pn);


	/********************* Debug functions ****************************/
	NP_EXPORT void         NP_APIC dbg_setlevel(int level);
	NP_EXPORT int          NP_APIC dbg_getlevel(void);
	NP_EXPORT void         NP_APIC dbg_getversion_datetime(char* dst, size_t maxlen);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_setQBSCSWTrigger(uint8_t slotID);
	NP_EXPORT NP_ErrorCode NP_APIC openEmulationProbe(uint8_t slotID, int8_t port);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_setEmulatorMode(uint8_t slotID, emulatormode_t mode);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_getEmulatorMode(uint8_t slotID, emulatormode_t* mode);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_setProbeEmulationMode(uint8_t slotID, int8_t port, bool state);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_getProbeEmulationMode(uint8_t slotID, int8_t port, bool* state);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_read_SRCHAIN1(uint8_t slotID, int8_t port, void* dst, size_t len);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_read_SRCHAIN2(uint8_t slotID, int8_t port, void* dst, size_t len);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_read_SRCHAIN3(uint8_t slotID, int8_t port, void* dst, size_t len);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_diagstats_reset(uint8_t slotID);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_diagstats_read(uint8_t slotID, struct np_diagstats* diag);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_disablescale(uint8_t slotID, bool disable);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_headstageReadRegister(uint8_t slotID, int8_t port, uint8_t address, uint8_t* value);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_headstageWriteRegister(uint8_t slotID, int8_t port, uint8_t address, uint8_t value);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_setchannelgain(uint8_t slotID, int8_t port, int channel, double gainAP, double gainLFP);
	NP_EXPORT NP_ErrorCode NP_APIC dbg_getchannelgain(uint8_t slotID, int8_t port, int channel, double* gainAP, double* gainLFP);

	/* @brief Set the offset correction data
	* ADC offset correction can be programmed per channel.
	*
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @param port: for which HS (valid range 0 to 3)
	* @param adcchannel nr: 0..31
	* @param offset: 6 bit offset to be subtraced from the ADC value when the raw ADC data crosses the threshold value
	* @param threshold: 10 bit threshold value. if the raw ADC value crosses this threshold,
	* @returns SUCCESS if succesful, error code otherwise.
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC setOffsetCorrection(unsigned char slotID, signed char port, int adcchannel, uint16_t offset, uint16_t threshold);

	/**
	* @brief Starts a continuous stream of data from the BS FPGA
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC startInfiniteStream(uint8_t slotID);

	/**
	* @brief Stops a continuous stream of data from the BS FPGA
	* @param slotID: which slot in the PXI chassis (valid range depends on the chassis)
	* @returns SUCCESS if successful, NO_LINK if no datalink, NO_SLOT if no Neuropix card is plugged in the selected PXI chassis slot, WRONG_SLOT in case a slot number outside the chassis range is entered.
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC stopInfiniteStream(uint8_t slotID);



	NP_EXPORT NP_ErrorCode NP_APIC probeChannelStatistics_Reset(uint8_t slotID, int8_t portID, channeltype_t channels);
	NP_EXPORT NP_ErrorCode NP_APIC probeChannelStatistics_Start(uint8_t slotID, int8_t portID, channeltype_t channels, int maxsamplecount);
	NP_EXPORT NP_ErrorCode NP_APIC probeChannelStatistics_Stop(uint8_t slotID, int8_t portID, channeltype_t channels);
	NP_EXPORT NP_ErrorCode NP_APIC probeChannelStatistics_ReadLFP(uint8_t slotID, int8_t portID, struct probechannelstatistics* stats, int firstchannel, int count);
	NP_EXPORT NP_ErrorCode NP_APIC probeChannelStatistics_ReadAP(uint8_t slotID, int8_t portID, struct probechannelstatistics* stats, int firstchannel, int count);
	NP_EXPORT NP_ErrorCode NP_APIC probeChannelStatistics_ReadADC(uint8_t slotID, int8_t portID, struct probechannelstatistics* stats, int firstchannel, int count);


	NP_EXPORT NP_ErrorCode NP_APIC bist_fft(double* real, size_t samplecount, size_t channelcount);
	NP_EXPORT NP_ErrorCode NP_APIC bist_fftpeakdetect(uint8_t slotID, int8_t port, double* peakfreq, double* peakampl, size_t samplecount, size_t channelcount);

	/*
	  Set the state to prevents the QBSC to reboot into normal image when openBS is called.
	*/
	NP_EXPORT	NP_ErrorCode NP_APIC dbg_preventQBSCnormalboot(int state);

#ifdef __cplusplus
}
#endif	
