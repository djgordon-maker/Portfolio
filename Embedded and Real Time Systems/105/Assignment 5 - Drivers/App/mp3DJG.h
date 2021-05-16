/*
    mp3DJG.h
    Some additional utility functions for controlling the MP3 decoder.

    Developed by Daniel Gordon for embedded systems programming certificate in March 2020
*/
#ifndef __MP3DJG_H
#define __MP3DJG_H

void Mp3Play(HANDLE hMp3, INT8U *pBuf);
void Mp3Stop(HANDLE hMp3);
void Mp3SetVol(HANDLE hMp3, INT8U vol);

#endif