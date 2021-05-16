/*
    mp3DJG.c
    Some additional utility functions for controlling the MP3 decoder.

    Developed by Daniel Gordon for embedded systems programming certificate in March 2020
    
*/

#include "bsp.h"
#include "mp3Util.h"

//void delay(uint32_t time);

//extern BOOLEAN nextSong;

// Mp3Play
// Fills the buffer for the MP3 decoder
// Assumes MP3Init and MP3StreamInit from mp3Util.h have been called
// hMp3: an open handle to the MP3 decoder
// pBuf: data to be sent to MP3 decoder
void Mp3Play(HANDLE hMp3, INT8U *pBuf) {
  INT32U chunkLen = MP3_DECODER_BUF_SIZE;
  
  Ioctl(hMp3, PJDF_CTRL_MP3_SELECT_DATA, 0, 0);
  Write(hMp3, pBuf, &chunkLen);
}

// Mp3Stop
// Commands a Soft Reset, with the intention of stopping the MP3 decoder from streaming
// hMp3: an open handle to the MP3 decoder
void Mp3Stop(HANDLE hMp3) {
  INT32U length = BspMp3SoftResetLen;
  
  Ioctl(hMp3, PJDF_CTRL_MP3_SELECT_COMMAND, 0, 0);
  Write(hMp3, (void*)BspMp3SoftReset, &length);
}

// Mp3SetVol
// Modifies the volume in the MP3 decoder
// hMp3: an open handle to the MP3 decoder
// vol: value volume will be set to
void Mp3SetVol(HANDLE hMp3, INT8U vol) {
  INT8U VolCmd[] = {0x02, 0x0B, vol, vol};
  INT32U length = sizeof(VolCmd);
  
  Ioctl(hMp3, PJDF_CTRL_MP3_SELECT_COMMAND, 0, 0);
  Write(hMp3, (void*)VolCmd, &length);
}