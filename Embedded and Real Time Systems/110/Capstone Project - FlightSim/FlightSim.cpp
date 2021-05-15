
#include <math.h>
#include "app_hsmn.h"
#include "fw_log.h"
#include "fw_assert.h"
#include "DispInterface.h"
#include "SensorInterface.h"
#include "FlightSim.h"
#include "FlightSimInterface.h"

FW_DEFINE_THIS_FILE("FlightSim.cpp")

#define COMPASS_DIV 100                //Number used to separate direction from offset
#define COMPASS_MAX (72*COMPASS_DIV)   //72 is the number of 5 degree segments in 360
#define OFFSET_DIST 60                 //Distance to offset compass before moving to the next segment

namespace APP {

#undef ADD_EVT
#define ADD_EVT(e_) #e_,

static char const * const timerEvtName[] = {
		"FLIGHT_SIM_TIMER_EVT_START",
		FLIGHT_SIM_TIMER_EVT
};

static char const * const internalEvtName[] = {
		"FLIGHT_SIM_INTERNAL_EVT_START",
		FLIGHT_SIM_INTERNAL_EVT
};
static char const * const interfaceEvtName[] = {
		"FLIGHT_SIM_INTERFACE_EVT_START",
		FLIGHT_SIM_INTERFACE_EVT
};

FlightSim::FlightSim() :
		Active((QStateHandler)&FlightSim::InitialPseudoState, FLIGHT_SIM, "FLIGHT_SIM"),
	    m_accelGyroPipe(m_accelGyroStor, ACCEL_GYRO_PIPE_ORDER),
	    m_stateTimer(GetHsm().GetHsmn(), STATE_TIMER),
	    m_reportTimer(GetHsm().GetHsmn(), REPORT_TIMER) {
	    SET_EVT_NAME(FLIGHT_SIM);
	    m_roll_offset = 0;
	    m_pitch_offset = 0;
	    m_roll = 0;
	    m_pitch = 0;
	    m_altitude = 0;
	    m_compass = 0;
	    m_groundSpeed = 0;
}

QState FlightSim::InitialPseudoState(FlightSim * const me, QEvt const * const e) {
	(void)e;
	return Q_TRAN(&FlightSim::Root);
}

QState FlightSim::Root(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_INIT_SIG: {
			EVENT(e);
			return Q_TRAN(&FlightSim::Stopped);
		}
		case FLIGHT_SIM_START_REQ: {
			EVENT(e);
			Evt const &req = EVT_CAST(*e);
			Evt *evt = new FlightSimStartCfm(req.GetFrom(), GET_HSMN(), req.GetSeq(), ERROR_STATE, GET_HSMN());
			Fw::Post(evt);
			return Q_HANDLED();
		}
		case FLIGHT_SIM_STOP_REQ: {
			EVENT(e);
			Evt const &req = EVT_CAST(*e);
			me->GetHsm().SaveInSeq(req);
			return Q_TRAN(&FlightSim::Stopping);
		}
	}
	return Q_SUPER(&QHsm::top);
}

QState FlightSim::Stopped(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case FLIGHT_SIM_START_REQ: {
			EVENT(e);
			Evt const &req = EVT_CAST(*e);
			me->GetHsm().SaveInSeq(req);
			return Q_TRAN(&FlightSim::Starting);
		}
		case FLIGHT_SIM_STOP_REQ: {
			EVENT(e);
			Evt const &req = EVT_CAST(*e);
			Evt *evt = new FlightSimStopCfm(req.GetFrom(), GET_HSMN(), req.GetSeq(), ERROR_SUCCESS);
			Fw::Post(evt);
		}
	}
	return Q_SUPER(&FlightSim::Root);
}

QState FlightSim::Starting(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			uint32_t timeout = FlightSimStartReq::TIMEOUT_MS;
			FW_ASSERT(timeout > DispStartReq::TIMEOUT_MS);
			FW_ASSERT(timeout > SensorAccelGyroOnReq::TIMEOUT_MS);
			me->m_stateTimer.Start(timeout);
			me->GetHsm().ResetOutSeq();
			Evt *evt = new DispStartReq(ILI9341, GET_HSMN(), GEN_SEQ());
			me->GetHsm().SaveOutSeq(*evt);
			Fw::Post(evt);
			evt = new SensorAccelGyroOnReq(IKS01A1_ACCEL_GYRO, GET_HSMN(), GEN_SEQ(), &me->m_accelGyroPipe);
			me->GetHsm().SaveOutSeq(*evt);
			Fw::Post(evt);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			me->m_stateTimer.Stop();
			me->GetHsm().ClearInSeq();
			return Q_HANDLED();
		}
		case DISP_START_CFM:
		case SENSOR_ACCEL_GYRO_ON_CFM: {
			EVENT(e);
			ErrorEvt const &cfm = ERROR_EVT_CAST(*e);
			bool allRecived;
			if(!me->GetHsm().HandleCfmRsp(cfm,allRecived)) {
				Evt *evt = new Failed(GET_HSMN(), cfm.GetError(), cfm.GetOrigin(), cfm.GetReason());
				me->PostSync(evt);
			} else if(allRecived) {
				Evt *evt = new Evt(DONE, GET_HSMN());
				me->PostSync(evt);
			}
			return Q_HANDLED();
		}
		case FAILED:
		case STATE_TIMER: {
			EVENT(e);
			Evt *evt;
			if(e->sig == FAILED) {
				ErrorEvt const &failed = ERROR_EVT_CAST(*e);
				evt = new FlightSimStartCfm(me->GetHsm().GetInHsmn(), GET_HSMN(), me->GetHsm().GetInSeq(),
												failed.GetError(), failed.GetOrigin(), failed.GetReason());
			} else {
				evt = new FlightSimStartCfm(me->GetHsm().GetInHsmn(), GET_HSMN(), me->GetHsm().GetInSeq(),
												ERROR_TIMEOUT, GET_HSMN());
			}
			Fw::Post(evt);
			return Q_TRAN(&FlightSim::Stopping);
		}
		case DONE: {
			EVENT(e);
			Evt *evt = new FlightSimStartCfm(me->GetHsm().GetInHsmn(), GET_HSMN(), me->GetHsm().GetInSeq(),
												ERROR_SUCCESS);
			Fw::Post(evt);
			return Q_TRAN(&FlightSim::Started);
		}
	}
	return Q_SUPER(&FlightSim::Root);
}

QState FlightSim::Stopping(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			uint32_t timeout = FlightSimStopReq::TIMEOUT_MS;
			FW_ASSERT(timeout > DispStopReq::TIMEOUT_MS);
			FW_ASSERT(timeout > SensorAccelGyroOffReq::TIMEOUT_MS);
			me->m_stateTimer.Start(timeout);
			me->GetHsm().ResetOutSeq();
			Evt *evt = new DispStopReq(ILI9341, GET_HSMN(), GEN_SEQ());
			me->GetHsm().SaveOutSeq(*evt);
			Fw::Post(evt);
			evt = new SensorAccelGyroOffReq(IKS01A1_ACCEL_GYRO, GET_HSMN(), GEN_SEQ());
			me->GetHsm().SaveOutSeq(*evt);
			Fw::Post(evt);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			me->m_stateTimer.Stop();
			me->GetHsm().ClearInSeq();
			me->GetHsm().Recall();
			return Q_HANDLED();
		}
		case FLIGHT_SIM_STOP_REQ: {
			EVENT(e);
			me->GetHsm().Defer(e);
			return Q_HANDLED();
		}
		case DISP_STOP_CFM:
		case SENSOR_ACCEL_GYRO_OFF_CFM: {
			EVENT(e);
			ErrorEvt const &cfm = ERROR_EVT_CAST(*e);
			bool allRecived;
			if(!me->GetHsm().HandleCfmRsp(cfm, allRecived)) {
				Evt *evt = new Failed(GET_HSMN(), cfm.GetError(), cfm.GetOrigin(), cfm.GetReason());
				me->PostSync(evt);
			} else if(allRecived) {
				Evt *evt = new Evt(DONE, GET_HSMN());
				me->PostSync(evt);
			}
			return Q_HANDLED();
		}
		case FAILED:
		case STATE_TIMER: {
			EVENT(e);
			FW_ASSERT(0); //should never reach here
			return Q_HANDLED();
		}
		case DONE: {
			EVENT(e);
			Evt *evt = new FlightSimStopCfm(me->GetHsm().GetInHsmn(), GET_HSMN(), me->GetHsm().GetInSeq(), ERROR_SUCCESS);
			Fw::Post(evt);
			return Q_TRAN(&FlightSim::Stopped);
		}
	}
	return Q_SUPER(&FlightSim::Root);
}

QState FlightSim::Started(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			me->m_reportTimer.Start(REPORT_TIMEOUT_MS, Timer::PERIODIC);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			me->m_reportTimer.Stop();
			return Q_HANDLED();
		}
		case Q_INIT_SIG: {
			EVENT(e);
			return Q_TRAN(&FlightSim::Setup);
		}
		case REPORT_TIMER: {
			EVENT(e);
			AccelGyroReport report;
			me->m_avgReport = report;
			int32_t count = 0;
			while (me->m_accelGyroPipe.GetUsedCount()) {
				me->m_accelGyroPipe.Read(&report, 1);
                //LOG("%d: (%d, %d, %d)",count, report.m_aX, report.m_aY, report.m_aZ);
                me->m_avgReport.m_aX += report.m_aX;
                me->m_avgReport.m_aY += report.m_aY;
                me->m_avgReport.m_aZ += report.m_aZ;
                //LOG("%d, %d, %d", me->m_avgReport.m_aX, me->m_avgReport.m_aY, me->m_avgReport.m_aZ);
                count++;
            }
            if (count) {
                me->m_avgReport.m_aX /= count;
                me->m_avgReport.m_aY /= count;
                me->m_avgReport.m_aZ /= count;
            }
            //LOG("(count = %d) %d, %d, %d", count, me->m_avgReport.m_aX, me->m_avgReport.m_aY, me->m_avgReport.m_aZ);
            Evt *evt = new Evt(SIMULATE, GET_HSMN());
            Fw::Post(evt);
            /*// Send to server.
            char buf[50];
            snprintf(buf, sizeof(buf), "%d %d %d\n\r", (int)me->m_avgReport.m_aX, (int)me->m_avgReport.m_aY, (int)me->m_avgReport.m_aZ);
            evt = new WifiSendReq(WIFI_ST, GET_HSMN(), 0, buf);
            Fw::Post(evt);*/
            return Q_HANDLED();
		}
		case DRAW: {
			EVENT(e);
			//Insures compass is in a usable range
			if(me->m_compass < 0) { me->m_compass += COMPASS_MAX; }
			else if(me->m_compass > COMPASS_MAX) { me->m_compass -= COMPASS_MAX; }
			//convert compass value to a number between 0 and 360, rounded down to the nearest 5
			int16_t dir = (me->m_compass/COMPASS_DIV)*5;
			//generate graphical offset for small adjustments
			int16_t offset = ((me->m_compass%COMPASS_DIV)*OFFSET_DIST)/COMPASS_DIV;

            LOG("Pitch: %2d, Roll: %2d, Speed: %3d, Dir: %3d, Altitude: %4d", me->m_pitch, me->m_roll, me->m_groundSpeed, (me->m_compass*360)/COMPASS_MAX, me->m_altitude);
			char buf[30];
			//Draw HUD
			Evt *evt = new DispDrawBeginReq(ILI9341, GET_HSMN(), GEN_SEQ());
			Fw::Post(evt);
			//Draw horizion
			evt = new DispDrawSkyReq(ILI9341, GET_HSMN(), me->m_altitude, me->m_roll);
			Fw::Post(evt);
			//Print compass
			snprintf(buf, sizeof(buf), "%3d  %3d  %3d  %3d  %3d", (dir+350)%360, (dir+355)%360, dir, (dir+5)%360, (dir+10)%360);
			evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 40-offset, 15, COLOR24_WHITE, COLOR24_WHITE, 2);
			Fw::Post(evt);
			//Print speed
			snprintf(buf, sizeof(buf), "%3d mph", me->m_groundSpeed);
			evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 80, 200, COLOR24_BLACK, COLOR24_BLACK, 4);
			Fw::Post(evt);
			//Print DEBUG
//			snprintf(buf, sizeof(buf), "Roll: %d\nPitch: %d", me->m_roll, me->m_pitch);
//			evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 40, 30, COLOR24_BLACK, COLOR24_BLACK, 3);
//			Fw::Post(evt);
			//HUD Complete
			evt = new DispDrawEndReq(ILI9341, GET_HSMN(), GEN_SEQ());
			Fw::Post(evt);
			return Q_HANDLED();
		}
	}
	return Q_SUPER(&FlightSim::Root);
}

QState FlightSim::Setup(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			//Draw setup instructions
            char buf[30];
            Evt *evt = new DispDrawBeginReq(ILI9341, GET_HSMN(), GEN_SEQ());
            Fw::Post(evt);
            snprintf(buf, sizeof(buf), "Hold at a");
            evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 10, 10, COLOR24_BLUE, COLOR24_WHITE, 4);
            Fw::Post(evt);
            snprintf(buf, sizeof(buf), "Comfortable");
            evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 10, 50, COLOR24_BLUE, COLOR24_WHITE, 4);
            Fw::Post(evt);
            snprintf(buf, sizeof(buf), "Angle and");
            evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 10, 90, COLOR24_BLUE, COLOR24_WHITE, 4);
            Fw::Post(evt);
            snprintf(buf, sizeof(buf), "Press Button");
            evt = new DispDrawTextReq(ILI9341, GET_HSMN(), buf, 10, 130, COLOR24_BLUE, COLOR24_WHITE, 4);
            Fw::Post(evt);
            evt = new DispDrawEndReq(ILI9341, GET_HSMN(), GEN_SEQ());
            Fw::Post(evt);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case FLIGHT_SIM_USER_READY: {
			EVENT(e);
			//Save current position as offset
            volatile const float PI = 3.14159265;
			volatile float x = me->m_avgReport.m_aX;
			volatile float y = me->m_avgReport.m_aY;
			volatile float z = me->m_avgReport.m_aZ;

            me->m_pitch_offset = atan(y/sqrt((x*x) + (z*z))) * 180/PI;
            me->m_roll_offset  = atan(x/sqrt((y*y) + (z*z))) * 180/PI;
            me->m_altitude = 0;
            me->m_compass = 0;
            me->m_groundSpeed = 0;

			return Q_TRAN(&FlightSim::OnGround);
		}
	}
	return Q_SUPER(&FlightSim::Started);
}

QState FlightSim::OnGround(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			me->m_altitude = 0;
			Evt *evt = new Evt(DRAW, GET_HSMN());
			Fw::Post(evt);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_INIT_SIG: {
			EVENT(e);
			return Q_TRAN(&FlightSim::LowSpeed);
		}
	}
	return Q_SUPER(&FlightSim::Started);
}

QState FlightSim::LowSpeed(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case SIMULATE: {
			EVENT(e);
			//Calculate
            volatile const float PI = 3.14159265;
			volatile float x = me->m_avgReport.m_aX;
			volatile float y = me->m_avgReport.m_aY;
			volatile float z = me->m_avgReport.m_aZ;

            me->m_pitch = (atan(y/sqrt((x*x) + (z*z))) * 180/PI) - me->m_pitch_offset;
            me->m_roll  = (atan(x/sqrt((y*y) + (z*z))) * 180/PI) - me->m_roll_offset;
            me->m_groundSpeed -= me->m_pitch/10;
            me->m_compass     -= me->m_roll;
            if(me->m_groundSpeed < 0) { me->m_groundSpeed = 0; }
            else if (me->m_groundSpeed > 250) {me->m_groundSpeed = 250; }
            //clear roll to keep horizon flat while on the ground
            me->m_roll = 0;

			Evt *evt = new Evt(DRAW, GET_HSMN());
			Fw::Post(evt);
			if(me->m_groundSpeed > 200) {
				return Q_TRAN(&FlightSim::HighSpeed);
			}
			return Q_HANDLED();
		}
	}
	return Q_SUPER(&FlightSim::OnGround);
}

QState FlightSim::HighSpeed(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case SIMULATE: {
			EVENT(e);
			//Calculate
            volatile const float PI = 3.14159265;
			volatile float x = me->m_avgReport.m_aX;
			volatile float y = me->m_avgReport.m_aY;
			volatile float z = me->m_avgReport.m_aZ;

            me->m_pitch = (atan(y/sqrt((x*x) + (z*z))) * 180/PI) - me->m_pitch_offset;
            me->m_roll  = (atan(x/sqrt((y*y) + (z*z))) * 180/PI) - me->m_roll_offset;
            me->m_compass     -= me->m_roll;

            if (me->m_pitch < -10)   { me->m_groundSpeed -= me->m_pitch/10; }
            else if(me->m_pitch < 0) { me->m_groundSpeed -= me->m_pitch+10; }
            else                     { me->m_altitude += me->m_pitch; }

            if(me->m_groundSpeed < 0)         { me->m_groundSpeed = 0; }
            else if (me->m_groundSpeed > 250) {me->m_groundSpeed = 250; }

            //clear roll to keep horizon flat while on the ground
            me->m_roll = 0;

            Evt *evt = new Evt(DRAW, GET_HSMN());
            Fw::Post(evt);
			if(me->m_altitude > 0) {
				return Q_TRAN(&FlightSim::InFlight);
			}
			if(me->m_groundSpeed < 200) {
				return Q_TRAN(&FlightSim::LowSpeed);
			}
			return Q_HANDLED();
		}
	}
	return Q_SUPER(&FlightSim::OnGround);
}

QState FlightSim::InFlight(FlightSim * const me, QEvt const * const e) {
	switch(e->sig) {
		case Q_ENTRY_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case Q_EXIT_SIG: {
			EVENT(e);
			return Q_HANDLED();
		}
		case SIMULATE: {
			EVENT(e);
			//calcuate
			volatile const float PI = 3.14159265;
			volatile float x = me->m_avgReport.m_aX;
			volatile float y = me->m_avgReport.m_aY;
			volatile float z = me->m_avgReport.m_aZ;

			me->m_pitch = (atan(y/sqrt((x*x) + (z*z))) * 180/PI) - me->m_pitch_offset;
			me->m_roll  = (atan(x/sqrt((y*y) + (z*z))) * 180/PI) - me->m_roll_offset;
			me->m_altitude += me->m_pitch;
			me->m_compass     -= me->m_roll;
			if(me->m_pitch < 0) { me->m_groundSpeed -= me->m_pitch/10; }
			else 				{ me->m_groundSpeed -= me->m_pitch/15; }
			if(me->m_groundSpeed < 150) { me->m_altitude -= 150; }

			Evt *evt = new Evt(DRAW, GET_HSMN());
			Fw::Post(evt);
			if(me->m_altitude <= 0) {
				return Q_TRAN(&FlightSim::HighSpeed);
			}
			return Q_HANDLED();
		}
	}
	return Q_SUPER(&FlightSim::Started);
}

} //namespace APP
