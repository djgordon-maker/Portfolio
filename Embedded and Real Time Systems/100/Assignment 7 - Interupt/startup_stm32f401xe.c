#include "stm32f401xe.h"

extern int CSTACK$$Limit;
extern void __iar_program_start(void);

void NMI_Handler(void); 
void HardFault_Handler(void);
void MemManage_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);
void SVC_Handler(void);
void DebugMon_Handler(void);
void PendSV_Handler(void);
void SysTick_Handler(void);

int const __vector_table[] @".intvec" = { 
  (int)&CSTACK$$Limit,       //0x00 Initial SP value 
  (int)&__iar_program_start, //0x04 Reset 
  (int)&NMI_Handler,         //0x08 NMI       
  (int)&HardFault_Handler,   //0x0c Hard fault 
  (int)&MemManage_Handler,   //0x10 Memory management fault 
  (int)&BusFault_Handler,    //0x14 Bus fault  
  (int)&UsageFault_Handler,  //0x18 Usuage fault 
  0x0,                       //0x1c Reserved 
  0x0,                       //0x20 Reserved 
  0x0,                       //0x24 Reserved 
  0x0,                       //0x28 Reserved 
  (int)&SVC_Handler,         //0x2c SVCall 
  (int)&DebugMon_Handler,    //0x30 Reserved for Debug
  0x0,                       //0x34 Reserved 
  (int)&PendSV_Handler,      //0x38 PendSV 
  (int)&SysTick_Handler      //0x3c Systick
};

void NMI_Handler(void) { while(1) {} }
void HardFault_Handler(void) { while(1) {} }
void MemManage_Handler(void) { while(1) {} }
void BusFault_Handler(void) { while(1) {} }
void UsageFault_Handler(void) { while(1) {} }
void SVC_Handler(void) { /*empty*/ }
void DebugMon_Handler(void) { /*empty*/ }
void PendSV_Handler(void) { /*empty*/ }
void SysTick_Handler(void) { /*reached zero; restart count */ }