/************************************************************************************

Copyright (c) 2001-2016  University of Washington Extension.

Module Name:

    tasks.c

Module Description:

    The tasks that are executed by the test application.

2016/2 Nick Strathy adapted it for NUCLEO-F401RE 

************************************************************************************/
#include <stdarg.h>

#include "bsp.h"
#include "print.h"
#include "mp3Util.h"
#include "mp3DJG.h"

#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ILI9341.h>
#include <Adafruit_FT6206.h>

Adafruit_ILI9341 lcdCtrl = Adafruit_ILI9341(); // The LCD controller

Adafruit_FT6206 touchCtrl = Adafruit_FT6206(); // The Touchscreen controller



#define PENRADIUS 3

long MapTouchToScreen(long x, long in_min, long in_max, long out_min, long out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}


#include "train_crossing.h"

#define BUFSIZE 256
#define bgColor 0x01E0
#define uiColor 0xE71F
#define BUTTON_WIDTH   55
#define BUTTON_HEIGHT  80
#define VOL_DOWN_X     32
#define STOP_X         91 
#define PLAY_X         149
#define VOL_UP_X       208
#define BOT_ROW_Y      275


/************************************************************************************

   Allocate the stacks for each task.
   The maximum number of tasks the application can have is defined by OS_MAX_TASKS in os_cfg.h

************************************************************************************/

static OS_STK   Mp3TaskStk[APP_CFG_TASK_START_STK_SIZE];
static OS_STK   DisplayTaskStk[APP_CFG_TASK_START_STK_SIZE];
static OS_STK   TouchInputTaskStk[APP_CFG_TASK_START_STK_SIZE];


     
// Task prototypes
void LcdTouchDemoTask(void* pdata); //Task used in Assignment 5
void Mp3DemoTask(void* pdata);      //Task used in Assignment 5
void Mp3Task(void* pdata);          //Manage audio playback
void ControlTask(void* pdata);      //Disision making task
void DisplayTask(void* pdata);      //Manage visual feedback
void TouchInputTask(void* pdata);   //Monitor touchscreen commands



// Useful functions
void PrintToLcdWithBuf(char *buf, int size, char *format, ...);

// enums for communication, constatns for use in mailboxes and queues
enum InputState {VOL_DOWN, STOP, PLAY, VOL_UP};
InputState rewind  = VOL_DOWN;
InputState stop    = STOP;
InputState play    = PLAY;
InputState fastfwd = VOL_UP;


// Globals
OS_EVENT * mboxStream;   //mailbox opened by Mp3Task()
BOOLEAN nextSong = OS_FALSE;
// message queue components

#define QMAXENTRIES 4            // maximum entries in the queue

typedef struct                   // a queue entry
{
	const INT8U *msg;
}QMsg_t;

OS_EVENT * displayQ;             // queue checked by DisplayTask()
void * qMsgVPtrs[QMAXENTRIES];   // an array of void pointers which is the actual queue
QMsg_t qMsgBlocks[QMAXENTRIES];  // a pool of message nodes that may be used as queue entries
OS_MEM *qMsgMemPart;             // pointer to a uCOS memory partition to manage the pool of message nodes
const INT8U Q_STOP = 0;
const INT8U Q_PAUSE = 1;
const INT8U Q_PLAY = 2;

//Menu buttons
Adafruit_GFX_Button volDownBtn   = Adafruit_GFX_Button();
Adafruit_GFX_Button stopBtn = Adafruit_GFX_Button();
Adafruit_GFX_Button playBtn = Adafruit_GFX_Button();
Adafruit_GFX_Button volUpBtn   = Adafruit_GFX_Button();

//Cursor corrodinates for status display
int16_t statusX = 80;
int16_t statusY = 100;
int16_t volX    = 170;
int16_t volY    = 40;
/************************************************************************************

   This task is the initial task running, started by main(). It starts
   the system tick timer and creates all the other tasks. Then it deletes itself.

************************************************************************************/
void StartupTask(void* pdata)
{
	char buf[BUFSIZE];

    PjdfErrCode pjdfErr;
    INT32U length;
    INT8U  err;
    static HANDLE hSD = 0;
    static HANDLE hSPI = 0;
    
    PrintWithBuf(buf, BUFSIZE, "StartupTask: Begin\n");
    PrintWithBuf(buf, BUFSIZE, "StartupTask: Starting timer tick\n");

    // Start the system tick
    OS_CPU_SysTickInit(OS_TICKS_PER_SEC);
    
    // Initialize SD card
    PrintWithBuf(buf, PRINTBUFMAX, "Opening handle to SD driver: %s\n", PJDF_DEVICE_ID_SD_ADAFRUIT);
    hSD = Open(PJDF_DEVICE_ID_SD_ADAFRUIT, 0);
    if (!PJDF_IS_VALID_HANDLE(hSD)) while(1);


    PrintWithBuf(buf, PRINTBUFMAX, "Opening SD SPI driver: %s\n", SD_SPI_DEVICE_ID);
    // We talk to the SD controller over a SPI interface therefore
    // open an instance of that SPI driver and pass the handle to 
    // the SD driver.
    hSPI = Open(SD_SPI_DEVICE_ID, 0);
    if (!PJDF_IS_VALID_HANDLE(hSPI)) while(1);
    
    length = sizeof(HANDLE);
    pjdfErr = Ioctl(hSD, PJDF_CTRL_SD_SET_SPI_HANDLE, &hSPI, &length);
    if(PJDF_IS_ERROR(pjdfErr)) while(1);

    
    // The maximum number of tasks the application can have is defined by OS_MAX_TASKS in os_cfg.h
    PrintWithBuf(buf, BUFSIZE, "StartupTask: Creating the application tasks\n");
    
    //set up mailbox and queue for intertask communication
    mboxStream  = OSMboxCreate(NULL);
    displayQ    = OSQCreate(qMsgVPtrs, QMAXENTRIES);
    
    //allocate memory for queue to exist
    qMsgMemPart = OSMemCreate(qMsgBlocks, QMAXENTRIES, sizeof(QMsg_t), &err);
    
    // Create the project tasks
    OSTaskCreate(Mp3Task, (void*)0, &Mp3TaskStk[APP_CFG_TASK_START_STK_SIZE-1], APP_TASK_MP3_PRIO);
    OSTaskCreate(DisplayTask, (void*)0, &DisplayTaskStk[APP_CFG_TASK_START_STK_SIZE-1], APP_TASK_DISPLAY_PRIO);
    OSTaskCreate(TouchInputTask, (void*)0, &TouchInputTaskStk[APP_CFG_TASK_START_STK_SIZE-1], APP_TASK_INPUT_PRIO);
    
    // Delete ourselves, letting the work be done in the new tasks.
    PrintWithBuf(buf, BUFSIZE, "StartupTask: deleting self\n");
	OSTaskDel(OS_PRIO_SELF);
}

void Mp3Task(void* pdata) {
  PjdfErrCode pjdfErr;         //Holds return value from PJDF functions
  INT8U err;                   //captures error from memory 
  INT32U length;               //Tells Ioctl the lentgh of passed array
  char buf[BUFSIZE];           //Buffer for UART
  boolean isStreaming = false; //Remembers mp3 status between loops
  InputState *cmdMsg;          //Recives input command from MBox
  QMsg_t *pQmsgToSend;         //queue message to displayQ
  INT8U currVol;               //current volume
  INT8U *pSong;                //Pointer to a point of a song
  INT8U *currSong;             //Pointer to the begining of the current Song
  INT32U currSongSize;         //Size of the current Song
  INT32U currSongPos;          //Position within the current Song
  
  PrintWithBuf(buf, BUFSIZE, "Mp3Task: starting\n");
  
  //Open MP3 driver
  PrintWithBuf(buf, BUFSIZE, "Mp3Task: Opening MP3 driver: %s\n", PJDF_DEVICE_ID_MP3_VS1053);
  HANDLE hMp3 = Open(PJDF_DEVICE_ID_MP3_VS1053, 0);
  if(!PJDF_IS_VALID_HANDLE(hMp3)) while(1);
  
  //Open SPI driver
  PrintWithBuf(buf, BUFSIZE, "Mp3Task: Opening MP3 SPI driver: %s\n", PJDF_DEVICE_ID_SPI1);
  HANDLE hSPI = Open(PJDF_DEVICE_ID_SPI1, 0);
  if(!PJDF_IS_VALID_HANDLE(hMp3)) while(1);
  
  //Wrap the SPI driver in the MP3 driver
  length = sizeof(HANDLE);
  pjdfErr = Ioctl(hMp3, PJDF_CTRL_MP3_SET_SPI_HANDLE, &hSPI, &length);
  if(PJDF_IS_ERROR(pjdfErr)) while(1);  
  
  //Initialize the MP3 controler
  PrintWithBuf(buf, BUFSIZE, "Mp3Task: Initializing MP3 driver\n");
  Mp3Init(hMp3);
  currVol = 0x10;
    
  //assign first song to be played
  currSong     = (INT8U*)Train_Crossing;
  currSongSize = sizeof(Train_Crossing);
  currSongPos  = 0;
  pSong        = currSong;
  
  PrintWithBuf(buf, BUFSIZE, "Mp3Task: Entering Loop\n");
  while(1) {
    //Check for incoming commands
    cmdMsg = (InputState*)OSMboxAccept(mboxStream);
    if(cmdMsg) {
      //prepare to send message to the queue
      pQmsgToSend = (QMsg_t*)OSMemGet(qMsgMemPart, &err);
      if (err != OS_ERR_NONE) {
        PrintWithBuf(buf, BUFSIZE, "Not enough message blocks");
        while (OS_TRUE);
      }
      //implement commands if found
      switch(*cmdMsg) {
      case VOL_DOWN:
        PrintWithBuf(buf, BUFSIZE, "Mp3Task: VOL_DOWN recived\n");
        if(currVol < 0xF0) currVol += 0x10;
        Mp3SetVol(hMp3, currVol);
        pQmsgToSend->msg = &currVol;
        break;
      case STOP:
        PrintWithBuf(buf, BUFSIZE, "Mp3Task: STOP recived\n");
        //stop streaming and reset song to begining
        Mp3Stop(hMp3);
        isStreaming = false;
        pSong = currSong;
        currSongPos = 0;
        pQmsgToSend->msg = &Q_STOP;
        break;
      case PLAY:
        if(isStreaming) {
          //pause stream, able to continue playing
          PrintWithBuf(buf, BUFSIZE, "Mp3Task: PAUSE recived\n");
          isStreaming = false;
          pQmsgToSend->msg = &Q_PAUSE;
        } else {
          PrintWithBuf(buf, BUFSIZE, "Mp3Task: PLAY recived\n");
          //initialize the stream, continues stream where left off
          isStreaming = true;
          Mp3StreamInit(hMp3);
          pQmsgToSend->msg = &Q_PLAY;
        }
        break;
      case VOL_UP:
        PrintWithBuf(buf, BUFSIZE, "Mp3Task: VOL_UP recived\n");
        if(currVol > 0x10) currVol -= 0x10;
        Mp3SetVol(hMp3, currVol);
        pQmsgToSend->msg = &currVol;
        break;    
      }
      OSQPost(displayQ, pQmsgToSend);
    }
    //If streaming, continusly fill MP3 decoder buffer
    //Otherwise, allow other tasks to run
    if(isStreaming) {
      if(currSongSize - currSongPos < MP3_DECODER_BUF_SIZE) {
        //the song has ended, tell ControlTask() to stop
        OSMboxPost(mboxStream, &stop);   
      } else {
        //fill the buffer and progress the song
        Mp3Play(hMp3, pSong);
        currSongPos += MP3_DECODER_BUF_SIZE;
        pSong += MP3_DECODER_BUF_SIZE;
      }
    } else {
     OSTimeDly(500);
    }
  }
}

//returns a darker shade than the color passed to it
uint16_t Darker(uint16_t color) {
  uint16_t dark = color & 0xE79C;
  return (dark >> 2);
}

//draws text at the specified position
void DrawText(int16_t x, int16_t y, char *text) {
  char buf[BUFSIZE];
  lcdCtrl.fillRect(0, y, ILI9341_TFTWIDTH, 20, bgColor);
  lcdCtrl.setCursor(x, y);
  lcdCtrl.setTextColor(uiColor);
  lcdCtrl.setTextSize(2);
  PrintToLcdWithBuf(buf, BUFSIZE, text);
}

//draws a small number that the specified position
void DrawInt8(int16_t x, int16_t y, INT8U num) {
  char buf[BUFSIZE];
  lcdCtrl.fillRect(0, y, ILI9341_TFTWIDTH, 20, bgColor);
  lcdCtrl.setCursor(x, y);
  lcdCtrl.setTextColor(uiColor);
  lcdCtrl.setTextSize(2);
  PrintToLcdWithBuf(buf, BUFSIZE, "%d", num);
}

//draws the play button
void DrawPlay() {
  lcdCtrl.fillRect(PLAY_X-(BUTTON_WIDTH/3), BOT_ROW_Y-(BUTTON_HEIGHT/3), (2*BUTTON_WIDTH/3), (2*BUTTON_HEIGHT/3), uiColor);
  lcdCtrl.fillTriangle(PLAY_X-(BUTTON_WIDTH/4), BOT_ROW_Y-(BUTTON_HEIGHT/3), PLAY_X+(BUTTON_WIDTH/4), BOT_ROW_Y, PLAY_X-(BUTTON_WIDTH/4), BOT_ROW_Y+(BUTTON_HEIGHT/3), Darker(uiColor));
}
//draws the pause button
void DrawPause() {
  lcdCtrl.fillRect(PLAY_X-(BUTTON_WIDTH/3), BOT_ROW_Y-(BUTTON_HEIGHT/3), (2*BUTTON_WIDTH/3), (2*BUTTON_HEIGHT/3), uiColor);
  lcdCtrl.fillRect(PLAY_X-(3*BUTTON_WIDTH/10), BOT_ROW_Y-(BUTTON_HEIGHT/4), (BUTTON_WIDTH/5), (BUTTON_HEIGHT/2), Darker(uiColor));
  lcdCtrl.fillRect(PLAY_X+(BUTTON_WIDTH/10), BOT_ROW_Y-(BUTTON_HEIGHT/4), (BUTTON_WIDTH/5), (BUTTON_HEIGHT/2), Darker(uiColor));
}
void DrawMenu() {
  //assumes ui is lighter than background
  uint16_t dark_uiColor = Darker(uiColor);
  lcdCtrl.fillScreen(bgColor);
  DrawText(statusX, statusY, "Stopped");
  DrawText(volX-25, volY-20, "Volume");
  DrawInt8(volX, volY, 0x0F);
  
  volDownBtn.initButton(&lcdCtrl, VOL_DOWN_X, BOT_ROW_Y, BUTTON_WIDTH, BUTTON_HEIGHT, dark_uiColor, uiColor, dark_uiColor, "VOL-", 2);
  stopBtn.initButton(&lcdCtrl, STOP_X, BOT_ROW_Y, BUTTON_WIDTH, BUTTON_HEIGHT, dark_uiColor, uiColor, dark_uiColor, "", 2);
  playBtn.initButton(&lcdCtrl, PLAY_X, BOT_ROW_Y, BUTTON_WIDTH, BUTTON_HEIGHT, dark_uiColor, uiColor, dark_uiColor, "", 2);
  volUpBtn.initButton(&lcdCtrl, VOL_UP_X, BOT_ROW_Y, BUTTON_WIDTH, BUTTON_HEIGHT, dark_uiColor, uiColor, dark_uiColor, "VOL+", 2);
  volDownBtn.drawButton();
  stopBtn.drawButton();
  lcdCtrl.fillRect(STOP_X-(BUTTON_WIDTH/3), BOT_ROW_Y-(BUTTON_HEIGHT/4), (2*BUTTON_WIDTH/3), (2*BUTTON_WIDTH/3), dark_uiColor);
  playBtn.drawButton();
  DrawPlay();
  volUpBtn.drawButton();
}


void DisplayTask(void* pdata) {
  INT8U err;           //Recives error from 
  PjdfErrCode pjdfErr; //Holds return value from PJDF functions
  INT32U length;       //Tells Ioctl the lentgh of passed array
  char buf[BUFSIZE];   //Buffer for printing text
  QMsg_t *dispMsgRx;   //Recives messages from displayQ
  INT8U dispMsg;       //extracts data from dispMsgRx
  
  PrintWithBuf(buf, BUFSIZE, "DisplayTask: starting\n");
  
  //Open LCD driver
  PrintWithBuf(buf, BUFSIZE, "DisplayTask: Opening LCD driver: %s\n", PJDF_DEVICE_ID_LCD_ILI9341);
  HANDLE hLcd = Open(PJDF_DEVICE_ID_LCD_ILI9341, 0);
  if (!PJDF_IS_VALID_HANDLE(hLcd)) while(1);  
  
  //Open SPI driver
  PrintWithBuf(buf, BUFSIZE, "DisplayTask: Opening LCD SPI driver: %s\n", LCD_SPI_DEVICE_ID);
  HANDLE hSPI = Open(LCD_SPI_DEVICE_ID, 0);
  if (!PJDF_IS_VALID_HANDLE(hSPI)) while(1);
  
  //Wrap the SPI in the LCD Driver
  length = sizeof(HANDLE);
  pjdfErr = Ioctl(hLcd, PJDF_CTRL_LCD_SET_SPI_HANDLE, &hSPI, &length);
  if(PJDF_IS_ERROR(pjdfErr)) while(1);
  
  //Initialize LCD controller
  PrintWithBuf(buf, BUFSIZE, "DisplayTask: Initializing LCD controller\n");
  lcdCtrl.setPjdfHandle(hLcd);
  lcdCtrl.begin();
  
  DrawMenu();
  
  PrintWithBuf(buf, BUFSIZE, "DisplayTask: Entering Loop\n");
  while(1) { 
    //wait for message in queue
    dispMsgRx = (QMsg_t*)OSQPend(displayQ, 0, &err);
    memcpy(&dispMsg, dispMsgRx->msg, sizeof(dispMsgRx->msg));
    OSMemPut(qMsgMemPart, dispMsgRx);
    PrintWithBuf(buf, BUFSIZE, "DisplayTask: Draw Status\n");
    switch(dispMsg) {
    case Q_STOP:
      DrawText(statusX, statusY, "Stopped");
      DrawPlay();
      break;
    case Q_PAUSE:
      DrawText(statusX+5, statusY, "Paused");
      DrawPlay();
      break;
    case Q_PLAY:
      DrawText(statusX, statusY, "Playing");
      DrawPause();
      break;
    default:
      dispMsg = 16-(dispMsg/16);
      DrawInt8(volX, volY, dispMsg);
    }
  }
}

void TouchInputTask(void* pdata) {
  OS_CPU_SR  cpu_sr;      //CPU status register needed to call OS_ENTER_CRITICAL()
  PjdfErrCode pjdfErr;    //Holds return value from PJDF functions
  INT32U  length;         //Tells Ioctl the lentgh of passed array
  INT8U   touchAddr;      //Used to initialize the TouchScreen driver  
  static HANDLE hTs = 0;  //TouchScreen Handle  
  char buf[BUFSIZE];      //Buffer for UART
  
  PrintWithBuf(buf, BUFSIZE, "TouchInputTask: starting\n");
  
  //Open touchscreen driver
  PrintWithBuf(buf, BUFSIZE, "TouchInputTask: Opening FT6206 touchscreen driver: %s\n", PJDF_DEVICE_ID_I2C1);
  hTs = Open(PJDF_DEVICE_ID_I2C1, 0);
  if(!PJDF_IS_VALID_HANDLE(hTs)) while(1);
  
  //Initialize touchscreen controller
  PrintWithBuf(buf, BUFSIZE, "TouchInputTask: Initalizing touchscreen controller\n");
  touchCtrl.setPjdfHandle(hTs);
  touchAddr = FT6206_ADDR<<1;
  length = 1;
  pjdfErr = Ioctl(hTs, PJDF_CTRL_I2C_SET_DEVICE_ADDRESS, &touchAddr, &length);
  if(PJDF_IS_ERROR(pjdfErr)) while(1);
  
  if (!touchCtrl.begin(40)) {  // pass in 'sensitivity' coefficient
        PrintWithBuf(buf, BUFSIZE, "Couldn't start FT6206 touchscreen controller\n");
        while (1);
  }
  
  PrintWithBuf(buf, BUFSIZE, "TouchInputTask: Entering Loop\n");
  while(1) { 
    //determine if screen was touched
    boolean touched = false;    
    OS_ENTER_CRITICAL();
    touched = touchCtrl.touched();
    OS_EXIT_CRITICAL();
    
    //if not touched, restart loop
    if(!touched) {
      volDownBtn.press(false);
      stopBtn.press(false);
      playBtn.press(false);
      volUpBtn.press(false);
      OSTimeDly(5);
      continue;
    }
        
    //determine where screen was touched
    TS_Point rawPoint;
    OS_ENTER_CRITICAL();
    rawPoint = touchCtrl.getPoint();
    OS_EXIT_CRITICAL();

    if (rawPoint.x == 0 && rawPoint.y == 0) {
      continue; // usually spurious, so ignore
    }
        
    // transform touch orientation to screen orientation.
    TS_Point p = TS_Point();
    p.x = MapTouchToScreen(rawPoint.x, 0, ILI9341_TFTWIDTH, ILI9341_TFTWIDTH, 0);
    p.y = MapTouchToScreen(rawPoint.y, 0, ILI9341_TFTHEIGHT, ILI9341_TFTHEIGHT, 0);
    
    //determine if a button was pressed
    if(volDownBtn.contains(p.x, p.y)) {
      PrintWithBuf(buf, BUFSIZE, "TouchInputTask: rewind pressed at (%d, %d)\n", p.x, p.y);
      volDownBtn.press(true);
      if(volDownBtn.justPressed()) OSMboxPost(mboxStream, &rewind);
    } else if(stopBtn.contains(p.x, p.y)) {
      PrintWithBuf(buf, BUFSIZE, "TouchInputTask: stop button pressed at (%d, %d)\n", p.x, p.y);
      stopBtn.press(true);
      if(stopBtn.justPressed()) OSMboxPost(mboxStream, &stop);
    } else if(playBtn.contains(p.x, p.y)) {
      PrintWithBuf(buf, BUFSIZE, "TouchInputTask: play button pressed at (%d, %d)\n", p.x, p.y);
      playBtn.press(true);
      if(playBtn.justPressed()) OSMboxPost(mboxStream, &play);
    } else if(volUpBtn.contains(p.x, p.y)) {
      PrintWithBuf(buf, BUFSIZE, "TouchInputTask: fast forward button pressed at (%d, %d)\n", p.x, p.y);
      volUpBtn.press(true);
      if(volUpBtn.justPressed()) OSMboxPost(mboxStream, &fastfwd);
    } else {
      PrintWithBuf(buf, BUFSIZE, "TouchInputTask: nothing pressed at (%d, %d)\n", p.x, p.y);
    }
  }
}

static void DrawLcdContents()
{
	char buf[BUFSIZE];
    lcdCtrl.fillScreen(ILI9341_BLACK);
    
    // Print a message on the LCD
    lcdCtrl.setCursor(40, 60);
    lcdCtrl.setTextColor(ILI9341_GREEN);  
    lcdCtrl.setTextSize(2);
    PrintToLcdWithBuf(buf, BUFSIZE, "Hello World!");

}

/************************************************************************************

   Runs LCD/Touch demo code

************************************************************************************/
void LcdTouchDemoTask(void* pdata)
{
    OS_CPU_SR  cpu_sr;
    PjdfErrCode pjdfErr;
    INT32U length;
    INT8U  touchAddr;
    
    static HANDLE hTs = 0;
    
    char buf[BUFSIZE];
    PrintWithBuf(buf, BUFSIZE, "LcdTouchDemoTask: starting\n");
    
    PrintWithBuf(buf, BUFSIZE, "Opening LCD driver: %s\n", PJDF_DEVICE_ID_LCD_ILI9341);
    // Open handle to the LCD driver
    HANDLE hLcd = Open(PJDF_DEVICE_ID_LCD_ILI9341, 0);
    if (!PJDF_IS_VALID_HANDLE(hLcd)) while(1);

	PrintWithBuf(buf, BUFSIZE, "Opening LCD SPI driver: %s\n", LCD_SPI_DEVICE_ID);
    // We talk to the LCD controller over a SPI interface therefore
    // open an instance of that SPI driver and pass the handle to 
    // the LCD driver.
    HANDLE hSPI = Open(LCD_SPI_DEVICE_ID, 0);
    if (!PJDF_IS_VALID_HANDLE(hSPI)) while(1);

    length = sizeof(HANDLE);
    pjdfErr = Ioctl(hLcd, PJDF_CTRL_LCD_SET_SPI_HANDLE, &hSPI, &length);
    if(PJDF_IS_ERROR(pjdfErr)) while(1);

	PrintWithBuf(buf, BUFSIZE, "Initializing LCD controller\n");
    lcdCtrl.setPjdfHandle(hLcd);
    lcdCtrl.begin();

    DrawLcdContents();
    
    PrintWithBuf(buf, BUFSIZE, "Initializing FT6206 touchscreen controller\n");
    hTs = Open(PJDF_DEVICE_ID_I2C1, 0);
    touchCtrl.setPjdfHandle(hTs);
    touchAddr = FT6206_ADDR<<1;
    length = 1;
    pjdfErr = Ioctl(hTs, PJDF_CTRL_I2C_SET_DEVICE_ADDRESS, &touchAddr, &length);
    if(PJDF_IS_ERROR(pjdfErr)) while(1);
    
    if (! touchCtrl.begin(40)) {  // pass in 'sensitivity' coefficient
        PrintWithBuf(buf, BUFSIZE, "Couldn't start FT6206 touchscreen controller\n");
        while (1);
    }
    
    int currentcolor = ILI9341_RED;

    while (1) { 
        boolean touched = false;
        
        // TODO: Poll for a touch on the touch panel
        OS_ENTER_CRITICAL();
        touched = touchCtrl.touched();
        OS_EXIT_CRITICAL();
        
        if (! touched) {
            OSTimeDly(5);
            continue;
        }
        
        TS_Point rawPoint;
       
        // TODO: Retrieve a point  
        OS_ENTER_CRITICAL();
        rawPoint = touchCtrl.getPoint();
        OS_EXIT_CRITICAL();

        if (rawPoint.x == 0 && rawPoint.y == 0)
        {
            continue; // usually spurious, so ignore
        }
        
        // transform touch orientation to screen orientation.
        TS_Point p = TS_Point();
        p.x = MapTouchToScreen(rawPoint.x, 0, ILI9341_TFTWIDTH, ILI9341_TFTWIDTH, 0);
        p.y = MapTouchToScreen(rawPoint.y, 0, ILI9341_TFTHEIGHT, ILI9341_TFTHEIGHT, 0);
        PrintWithBuf(buf, BUFSIZE, "dot at X=%d, Y=%d\n", p.x, p.y);
        
        lcdCtrl.fillCircle(p.x, p.y, PENRADIUS, currentcolor);
    }
}
/************************************************************************************

   Runs MP3 demo code

************************************************************************************/
void Mp3DemoTask(void* pdata)
{
    PjdfErrCode pjdfErr;
    INT32U length;

    OSTimeDly(2000); // Allow other task to initialize LCD before we use it.
    
	char buf[BUFSIZE];
	PrintWithBuf(buf, BUFSIZE, "Mp3DemoTask: starting\n");

	PrintWithBuf(buf, BUFSIZE, "Opening MP3 driver: %s\n", PJDF_DEVICE_ID_MP3_VS1053);
    // Open handle to the MP3 decoder driver
    HANDLE hMp3 = Open(PJDF_DEVICE_ID_MP3_VS1053, 0);
    if (!PJDF_IS_VALID_HANDLE(hMp3)) while(1);

	PrintWithBuf(buf, BUFSIZE, "Opening MP3 SPI driver: %s\n", MP3_SPI_DEVICE_ID);
    // We talk to the MP3 decoder over a SPI interface therefore
    // open an instance of that SPI driver and pass the handle to 
    // the MP3 driver.
    HANDLE hSPI = Open(MP3_SPI_DEVICE_ID, 0);
    if (!PJDF_IS_VALID_HANDLE(hSPI)) while(1);

    length = sizeof(HANDLE);
    pjdfErr = Ioctl(hMp3, PJDF_CTRL_MP3_SET_SPI_HANDLE, &hSPI, &length);
    if(PJDF_IS_ERROR(pjdfErr)) while(1);

    // Send initialization data to the MP3 decoder and run a test
	PrintWithBuf(buf, BUFSIZE, "Starting MP3 device test\n");
    Mp3Init(hMp3);
    int count = 0;
    
    while (1)
    {
        OSTimeDly(500);
        PrintWithBuf(buf, BUFSIZE, "Begin streaming sound file  count=%d\n", ++count);
        Mp3Stream(hMp3, (INT8U*)Train_Crossing, sizeof(Train_Crossing)); 
        PrintWithBuf(buf, BUFSIZE, "Done streaming sound file  count=%d\n", count);
    }
}


// Renders a character at the current cursor position on the LCD
static void PrintCharToLcd(char c)
{
    lcdCtrl.write(c);
}

/************************************************************************************

   Print a formated string with the given buffer to LCD.
   Each task should use its own buffer to prevent data corruption.

************************************************************************************/
void PrintToLcdWithBuf(char *buf, int size, char *format, ...)
{
    va_list args;
    va_start(args, format);
    PrintToDeviceWithBuf(PrintCharToLcd, buf, size, format, args);
    va_end(args);
}




