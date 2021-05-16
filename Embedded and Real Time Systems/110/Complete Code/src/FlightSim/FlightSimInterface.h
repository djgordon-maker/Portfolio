/*******************
 * EMBSYS110 FINAL PROJECT
 * Author: Daniel Gordon
 *
 * This state machine is a very simple flight simulator
 * It uses the accelerometer for controls, and displays results on the LCD screen
 */

#ifndef FLIGHT_SIM_INTERFACE_H
#define FLIGHT_SIM_INTERFACE_H

#include "fw_def.h"
#include "fw_evt.h"
#include "app_hsmn.h"

using namespace QP;
using namespace FW;

namespace APP {

#define FLIGHT_SIM_INTERFACE_EVT \
	ADD_EVT(FLIGHT_SIM_START_REQ) \
	ADD_EVT(FLIGHT_SIM_START_CFM) \
	ADD_EVT(FLIGHT_SIM_STOP_REQ) \
	ADD_EVT(FLIGHT_SIM_STOP_CFM) \
	ADD_EVT(FLIGHT_SIM_USER_READY)

#undef ADD_EVT
#define ADD_EVT(e_) e_,

enum {
	FLIGHT_SIM_INTERFACE_EVT_START = INTERFACE_EVT_START(FLIGHT_SIM),
	FLIGHT_SIM_INTERFACE_EVT
};

enum {
	FLIGHT_SIM_REASON_UNSPEC = 0,
};

class FlightSimStartReq : public Evt {
public:
	enum {
		TIMEOUT_MS = 400
	};
	FlightSimStartReq(Hsmn to, Hsmn from, Sequence seq) :
		Evt(FLIGHT_SIM_START_REQ, to, from, seq) {}
};

class FlightSimStartCfm : public ErrorEvt {
public:
    FlightSimStartCfm(Hsmn to, Hsmn from, Sequence seq,
                   Error error, Hsmn origin = HSM_UNDEF, Reason reason = 0) :
        ErrorEvt(FLIGHT_SIM_START_CFM, to, from, seq, error, origin, reason) {}
};

class FlightSimStopReq : public Evt {
public:
    enum {
        TIMEOUT_MS = 400
    };
    FlightSimStopReq(Hsmn to, Hsmn from, Sequence seq) :
        Evt(FLIGHT_SIM_STOP_REQ, to, from, seq) {}
};

class FlightSimStopCfm : public ErrorEvt {
public:
    FlightSimStopCfm(Hsmn to, Hsmn from, Sequence seq,
                   Error error, Hsmn origin = HSM_UNDEF, Reason reason = 0) :
        ErrorEvt(FLIGHT_SIM_STOP_CFM, to, from, seq, error, origin, reason) {}
};

class FlightSimUserReady : public Evt {
public:
	FlightSimUserReady(Hsmn to, Hsmn from, Sequence seq = 0) :
		Evt(FLIGHT_SIM_USER_READY, to, from, seq) {}
};

} //namespace APP

#endif //FLIGHT_SIM_INTERFACE_H
