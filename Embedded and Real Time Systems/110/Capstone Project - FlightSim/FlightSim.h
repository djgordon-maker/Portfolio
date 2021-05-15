/*******************
 * EMBSYS110 FINAL PROJECT
 * Author: Daniel Gordon
 *
 * This state machine is a very simple flight simulator
 * It uses the accelerometer for controls, and displays results on the LCD screen
 */

#ifndef FLIGHT_SIM_H
#define FLIGHT_SIM_H

#include "qpcpp.h"
#include "fw_active.h"
#include "fw_timer.h"
#include "fw_evt.h"
#include "app_hsmn.h"
#include "SensorAccelGyroInterface.h"

using namespace QP;
using namespace FW;

namespace APP {

class FlightSim : public Active {
public:
	FlightSim();

protected:
    static QState InitialPseudoState(FlightSim * const me, QEvt const * const e);
    static QState Root(FlightSim * const me, QEvt const * const e);
    	static QState Stopped(FlightSim * const me, QEvt const * const e);
    	static QState Starting(FlightSim * const me, QEvt const * const e);
    	static QState Stopping(FlightSim * const me, QEvt const * const e);
    	static QState Started(FlightSim * const me, QEvt const * const e);
    		static QState Setup(FlightSim * const me, QEvt const * const e);
    		static QState OnGround(FlightSim * const me, QEvt const * const e);
    			static QState LowSpeed(FlightSim * const me, QEvt const * const e);
    			static QState HighSpeed(FlightSim * const me, QEvt const * const e);
    		static QState InFlight(FlightSim * const me, QEvt const * const e);


   enum {
    	ACCEL_GYRO_PIPE_ORDER = 7,
   };
   AccelGyroReport m_accelGyroStor[1 << ACCEL_GYRO_PIPE_ORDER];
   AccelGyroPipe m_accelGyroPipe;
   AccelGyroReport m_avgReport;

   int16_t m_altitude;
   int16_t m_groundSpeed;
   int16_t m_compass;
   int16_t m_pitch;
   int16_t m_roll;
   int16_t m_pitch_offset;
   int16_t m_roll_offset;

   enum {
           REPORT_TIMEOUT_MS = 250
   };

   Timer m_stateTimer;
   Timer m_reportTimer;

#define FLIGHT_SIM_TIMER_EVT \
   ADD_EVT(STATE_TIMER) \
   ADD_EVT(REPORT_TIMER)

#define FLIGHT_SIM_INTERNAL_EVT \
	ADD_EVT(DONE) \
	ADD_EVT(FAILED) \
	ADD_EVT(SIMULATE) \
	ADD_EVT(DRAW)

#undef ADD_EVT
#define ADD_EVT(e_) e_,

   enum {
	   FLIGHT_SIM_TIMER_EVT_START = TIMER_EVT_START(FLIGHT_SIM),
	   FLIGHT_SIM_TIMER_EVT
   };

   enum {
	   FLIGHT_SIM_INTERNAL_EVT_START = INTERNAL_EVT_START(FLIGHT_SIM),
	   FLIGHT_SIM_INTERNAL_EVT
   };

   class Failed : public ErrorEvt {
   public:
	   Failed(Hsmn hsmn, Error error, Hsmn origin, Reason reason) :
		   ErrorEvt(FAILED, hsmn, hsmn, 0, error, origin, reason) {}
   };
};

} //namespace APP

#endif // FLIGHT_SIM_H
