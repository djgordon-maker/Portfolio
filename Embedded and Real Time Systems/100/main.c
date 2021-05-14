#include "stm32f401xe.h"

#define SYS_CLOCK_HZ 16000000

void delay(uint32_t delayInMicroseconds);

uint32_t count;
uint8_t  ready;      

int main()
{
  //set up pin 5 (LED) as output
  RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
  GPIOA->MODER |= GPIO_MODER_MODE5_0;
  
  //set up SysTick to tick every millisecond
  SysTick->LOAD = (SYS_CLOCK_HZ/1000)-1;
  SysTick->VAL = 0x0;
  SysTick->CTRL = 5; //does not use interupt
  
  //main loop
  while(1) {
    delay(2000);
    if(ready) {
      GPIOA->ODR ^= GPIO_ODR_OD5;
      ready = 0;
    }
  }
  return 0;
}

//delay function uses global to not hog processor
//TODO: pass pointer to a counter to allow different delays to run in parallel
//TODO: pass pointer to a function which would be called after defined time has passed
void delay(uint32_t delayInMicroseconds) {
  if(count <= 0) { 
    count = delayInMicroseconds;  //if not currently counting, begin count
  } else {  
    int ControlReg = SysTick->CTRL;
    ControlReg &= SysTick_CTRL_COUNTFLAG_Msk;
    if(ControlReg) { --count; }  //checks count flag to see if SysTick has reched zero
  }
  if(count <= 0) { ready = 1; } 
}
