  EXTERN PrintString      //used to print myStr
  EXTERN myStr            //defined in main.c

  PUBLIC div2Asm          //allows function to be called

//The next part tells the linker how to link our code
  SECTION .text:CODE:REORDER:NOROOT(2) 
  
  THUMB 

div2Asm             //Label for the function
  PUSH {R0, LR}     //Preserve the parameter and return location before printing
  LDR  R0, =myStr   //Load the double pointer to the string into R0
  LDR  R0, [R0]     //Unpack the pointer, makes R0 the pointer to the string
  BL PrintString    //Print myStr
  POP {R0, LR}      //Restore parameter and return location
  ASR R0, R0, #1    //Divide parameter by 2
  BX LR             //Return to C land

  END