//define base registers used by program
#define RCC_BASE    0x40023800                             //Reset and Clock Control
#define GPIOA_BASE  0x40020000                             //General Purpose I/O Port A
//define control registers used by program
#define RCC_AHB1ENR (*(unsigned int*) (RCC_BASE + 0x30))   //AHB1 Enable Register
#define GPIOA_MODER (*(unsigned int*) GPIOA_BASE)          //GPIOA Mode Register
#define GPIOA_ODR   (*(unsigned int*) (GPIOA_BASE + 0x14)) //GPIOA Output Data Register
//define masks used on control registers
#define GPIOA       0x1                                    //used on RCC_AHB1ENR to enable GPIOA
#define MODER5      0x400                                  //used on GPIOA_MODER to make PA5 an output pin
#define ODR5        0x20                                   //used on GPIOA_ODR to write to PA5
//unit of time for one dot
int unit = 500000;

void dash() {
  int count = 0;
  GPIOA_ODR |= ODR5;  //Write '1' to PA5 without affecting other pins
  while (count < 3*unit) { count++; }
  count = 0;
  GPIOA_ODR &= ~ODR5;  //Write '0' to PA5 without affecting other pins
  while (count < unit) { count++; }
}

void dot() {
  int count = 0;
  GPIOA_ODR |= ODR5;  //Write '1' to PA5 without affecting other pins
  while (count < unit) { count++; }
  count = 0;
  GPIOA_ODR &= ~ODR5;  //Write '0' to PA5 without affecting other pins
  while (count < unit) { count++; }
}


//assume light has already been off for 1 unit
void next() {
  int count = 0;
  while (count < 2*unit) { count++;}
}

int main() {
  //setup control registers
  RCC_AHB1ENR |= GPIOA;
  GPIOA_MODER |= MODER5;
 
  //Send "Daniel" in morse code
  //-.. .- -. .. . .-.. 
  //D
  dash();
  dot();
  dot();
  next();
  //a
  dot();
  dash();
  next();
  //n
  dash();
  dot();
  next();
  //i
  dot();
  dot();
  next();
  //e
  dot();
  next();
  //l
  dot();
  dash();
  dot();
  dot();
  
  return 0;
}


