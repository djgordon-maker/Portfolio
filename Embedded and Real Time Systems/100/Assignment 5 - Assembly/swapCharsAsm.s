  
  PUBLIC swapCharsAsm          //allows function to be called

//The next part tells the linker how to link our code
  SECTION .text:CODE:REORDER:NOROOT(2) 
  
  THUMB   
  
/******************************************
*  int swapCharsAsm(char*,char*);
*  Takes two char pointers and swaps their values
*  Assumes pointers are loaded into R0 and R1
*  returns 0 if the chars are identical
*  returns 1 if the chars are different
********************************************/

swapCharsAsm   //Label for the function
    LDRB R2, [R0] //Load value of first pointer into R2
    LDRB R3, [R1] //Load value of second pointer into R3
    CMP R2, R3   //Compare the values stored in the registers
    BEQ  eq      //Branch if the chars are equal
    STRB R2, [R1] //Store the value from the first pointer into the second pointer
    STRB R3, [R0] //Store the value from the second pointer into the first pointer
    MOV R0, #1   //Move a 1 into R0 because the chars were not equal
    BX LR        //Return to C-land
eq  MOV R0, #0   //Move a 0 into R0 becuase the chars are equal
    BX LR        //Return to C-land, did not swap chars because they are the same
    
 END