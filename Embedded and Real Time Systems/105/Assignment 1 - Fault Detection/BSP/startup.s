;
; The code that lives at the boot vector 
; When the Cortex starts from power up it 
;   sets the stack pointer register to the value at the boot vector
;   sets the program counter to the value at the reset vector
;   starts execution

; Define a name for this module of code/data (ie the code in this file, only 1 modules per file is allowed)
; this module will be placed at the boot vector of the Cortex by the linker (see the linker cmd line for explanation)
;
      MODULE    startupCode   
;
; Code is split into logical sections using the SECTION directive. This allows
; the position of code and data to be controlled, important to put the reset vector
; in the correct place

; How much stack is needed?
;  This depends upon what is put on it and how deep it goes (and use of recursion...) 
;  On Cortex The stack is 'fully descending' that means that the stack pointer always holds the pointer of the last stacked item. 
;  The CPU will decrement the stack pointer *before* writing to it
; Why does the stack type matter? 
;   Well if the stack is growing downwards how will you known if the bounds of the stack have been exceeded? You don't unless you gaurd against is.
;   A simple way of preventing clobbering of code/data due to stack overflow is to put it at a place in RAM where it cannot continue to growm ie at the bottom of RAM
; Hence the stack pointer is set to the lowest address of RAM plus the desired stack size.
; The stack and its location are setup in the linker configuration file (startupexample.icf)
; Forward declare that stack data section here, its actual location will be determine by the linker file.
;     the alignment is (3) which means 2 ^ 3, AKA 64 bit alignment
      SECTION CSTACK:DATA:NOROOT(3)

       
;
;     Create a data section to hold the Vector table addresses
;     it is called .intvec, it contains DATA 
;     ROOT determines id the linker will include the section even if it is not  used
;     NOROOT will cause the linke to discard unused sections
;     the alignment is (2) which means 2 ^ 2, AKA 32 bit alignment
;     NOTE: .intvec is a convention for the section with the interrupt vectors
      SECTION   .intvec:CODE:ROOT(2)


;       These are the  stock Cortex interrupt vectors (well, some of them) 
;       The only ones used in this example are Reset and SysTick
;       The rest are declared as 'weak' for now
;       (NOTE that IAR needs the name to be  __vector_table for the debugger and C-Spy to work correctly)
      PUBLIC  __vector_table
      
      EXTERN  SysTick_Handler
      EXTERN  FaultPrint
      EXTERN  GenerateFault
      EXTERN  UserFaultPrint

;   This indicates that the following is DATA, even though this is in a CODE section
;   The information is not executable, it is a list of pointers
      DATA
__vector_table  
      DCD       SFE(CSTACK)                 ; Stack Pointer will be set to this (SFE means Section End, ie the highest address in the section)
      DCD       ResetIrqHandler             ; Reset. (This points to the first piece of code that will execute at power on)
      DCD       NMIIrqHandler               ; NMI
      DCD       HardFaultIrqHandler         ; Hard Fault
      DCD       MemManageIrqHandler         ; MPU Fault
      DCD       BusFaultIrqHandler          ; Bus Fault
      DCD       UsageFaultIrqHandler        ; Usage Fault
      DCD       0
      DCD       0
      DCD       0
      DCD       0
      DCD       SVCIrqHandler               ; SVC 
      DCD       DebugIrqHandler             ; Debug Monitor
      DCD       0                       
      DCD       0
      DCD       SysTick_Handler           ; SysTick

      ; The STM32F401 specific interrupt vectors  Follow
      DCD     UnusedIrqHandler              ; WatchDog
      DCD     UnusedIrqHandler              ; PVD through EXTI Line detection
      DCD     UnusedIrqHandler              ; Tamper and TimeStamps through the EXTI line
      DCD     UnusedIrqHandler              ; RTC Wakeup through the EXTI line
      DCD     UnusedIrqHandler              ; Flash 
      DCD     UnusedIrqHandler              ; RCC  - Clocks
      DCD     EXTI0IrqHandler               ; EXTI Line0
      DCD     EXTI1IrqHandler               ; EXTI Line1
      DCD     EXTI2IrqHandler               ; EXTI Line2
      DCD     EXTI3IrqHandler               ; EXTI Line3
      DCD     EXTI4IrqHandler               ; EXTI Line4
      DCD     UnusedIrqHandler              ; DMA1 Stream 0
      DCD     UnusedIrqHandler              ; DMA1 Stream 1
      DCD     UnusedIrqHandler              ; DMA1 Stream 2
      DCD     UnusedIrqHandler              ; DMA1 Stream 3
      DCD     UnusedIrqHandler              ; DMA1 Stream 4
      DCD     UnusedIrqHandler              ; DMA1 Stream 5
      DCD     UnusedIrqHandler              ; DMA1 Stream 6
      DCD     UnusedIrqHandler              ; ADC1
      DCD     0
      DCD     0
      DCD     0
      DCD     0
      DCD     EXTI5Thru9IrqHandler          ; EXTI Lines 5->9
      DCD     UnusedIrqHandler              ; TIM1 Break and TIM9
      DCD     UnusedIrqHandler              ; TIM1 Update and TIM10
      DCD     UnusedIrqHandler              ; TIM1 Trigger and Commutation and TIM11
      DCD     UnusedIrqHandler              ; TIM1 Capture Compare
      DCD     UnusedIrqHandler              ; TIM2
      DCD     UnusedIrqHandler              ; TIM3
      DCD     UnusedIrqHandler              ; TIM4
      DCD     UnusedIrqHandler              ; I2C1 Event
      DCD     UnusedIrqHandler              ; I2C1 Error
      DCD     UnusedIrqHandler              ; I2C2 Event
      DCD     UnusedIrqHandler              ; I2C2 Error
      DCD     UnusedIrqHandler              ; SPI1
      DCD     UnusedIrqHandler              ; SPI2
      DCD     UnusedIrqHandler              ; USART1
      DCD     UnusedIrqHandler              ; USART2
      DCD     0
      DCD     EXTI10Thru15IrqHandler        ; EXTI Lines 10 -> 15
     
      ; There are more IRQs that are not added here......
      
      
      ; These are in the code section (.text)
      SECTION   .text:CODE:ROOT
      
      ; Stub IRQ handlers
      PUBWEAK  NMIIrqHandler
      PUBWEAK  HardFaultIrqHandler
      PUBWEAK  MemManageIrqHandler
      PUBWEAK  BusFaultIrqHandler
      PUBWEAK  UsageFaultIrqHandler
      PUBWEAK  SVCIrqHandler
      PUBWEAK  DebugIrqHandler
      PUBWEAK  SysTickIrqHandler
      PUBWEAK  EXTI0IrqHandler
      PUBWEAK  EXTI1IrqHandler
      PUBWEAK  EXTI2IrqHandler
      PUBWEAK  EXTI3IrqHandler
      PUBWEAK  EXTI4IrqHandler 
      PUBWEAK  EXTI5Thru9IrqHandler
      PUBWEAK  EXTI10Thru15IrqHandler
      
NMIIrqHandler 
MemManageIrqHandler      
BusFaultIrqHandler
UsageFaultIrqHandler      
SVCIrqHandler      
DebugIrqHandler      
SysTickIrqHandler
EXTI0IrqHandler
EXTI1IrqHandler
EXTI2IrqHandler
EXTI3IrqHandler
EXTI4IrqHandler
EXTI5Thru9IrqHandler
EXTI10Thru15IrqHandler

UnusedIrqHandler           
      B         UnusedIrqHandler      ; Loop forever

// HardFaultIrqHandler extracts the PC and LR values from the stack and
// passes them to a function to print them. It then returns to
// the GenerateFault function.

HardFaultIrqHandler
      // TODO: Fill in the missing code below
      
      // Save LR to stack since we will be calling a function below
      PUSH {LR}
      
      MOV R0, SP
      ADD R0, R0, #0x4
      BL  UserFaultPrint


      // Copy the PC and LR values from the stack to R0 and R1 respectively.
      //LDR R0, [SP, #0x1C]
      //LDR R1, [SP, #0x18]
          
      // Copy SP to R0
      MOV R0, SP
      
      // Add offset to R0 so it points to location where PC was pushed on stack
      ADD R0, R0, #0x1C
      
      // Save R0 to stack since we will want to reference it later
      PUSH {R0}
      
      // Copy RO to R1
      MOV R1, R0
      
      // Subtract 4 from R1 so it points to the stacked LR value
      SUB R1, R1, #0x4
      
      // Load the data pointed to by R0 into R0
      LDR R0, [R0]
    
      // Load the data pointed to by R1 into R1
      LDR R1, [R1]
      
      // Call FaultPrint() to print out the PC and LR values.
      // The arguments are passed in R0 and R1.
 //     BL FaultPrint
      
      
      // The diagnostic handler is done. Normally we would end the handler
      // here with a busy spin loop however to gain a little more insight
      // into exception handling we will return from this exception. If we 
      // return to the PC saved on the stack we will just re-execute the 
      // faulting instruction. Instead we will hack the PC value on the stack 
      // to re-enter GenerateFault().
      
      // Load the address of GenerateFault into R1
      // adding 2 (a hack to skip the function's initial push operation).
      LDR R1,=GenerateFault + 2
      
      // Restore R0 from stack. It points to PC in stack
      POP {R0}
      
      // Store R1 to address pointed to by R0
      STR R1, [R0]
      
      // Pop LR from stack
      POP {LR}
            
      // Return from exception handler
      BX        LR
      
      PUBLIC  ResetIrqHandler
      EXTERN  main
      ; Define what happens at reset.
ResetIrqHandler
      
      ; The IAR library handles this usually, but for this sample it will be done manually
      ; for educational purposes
      ;LDR     R0, =__iar_program_start  ; <- this will do the zero init and init data.
      ;BX R0
      
      
      ; For illustration do the full setup of the C Library data regions manually, 
      ; This will call the C function InitializeDataSection
      ; The stack pointer is already setup by the Cortex core
      ; !!the C function must not use any globally initialized variables, as they have not been initialized yet!!
      EXTERN    InitializeDataSection           ; Tell assembler this symbol is in another file
      LDR       R0, =InitializeDataSection      ; Load a register with the address of the function
      BLX       R0                              ; branch and link, absolute address
                                                ; the link register LR, contains the address of the Next instruction below
      
      ; Globals has been initialized, bss set to zero (not C++ so no constructors to call)
      ; Time to call main
      ; note that main on an embedded system does not have the concept of a command line, hence no arguments
      ; are passed in here
      LDR       R5, =main
      BX        R5                              ; branch, absolute address (never returns)
      
      END
