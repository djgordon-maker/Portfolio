#include <stdint.h>
#include "print.h"

/*
 *
 * Part of a fault exception handler. Prints the given register values.
 * pc: the value of the program counter when the fault occurred.
 * lr: the value of the link register when the fault occurred.
 *
 */
void FaultPrint(uint32_t pc, uint32_t lr)
{
    // TODO: Print an error message specifying the PC and LR values when the fault occurred
    PrintString("\nValue of PC: ");
    PrintHex(pc);
    PrintString("\nValue of LR: ");
    PrintHex(lr);
    PrintString("\n");
}

void UserFaultPrint(uint32_t* stack){
  PrintString("\nValue of R0:   ");
  PrintHex(stack[0]);
  PrintString("\nValue of R1:   ");
  PrintHex(stack[1]);
  PrintString("\nValue of R2:   ");
  PrintHex(stack[2]);
  PrintString("\nValue of R3:   ");
  PrintHex(stack[3]);
  PrintString("\nValue of R12:  ");
  PrintHex(stack[4]);
  PrintString("\nValue of LR:   ");
  PrintHex(stack[5]);
  PrintString("\nValue of PC:   ");
  PrintHex(stack[6]);
  PrintString("\nValue of APSR: ");
  PrintHex(stack[7]);
  PrintString("\n\n");
}
