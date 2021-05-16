#include "stack.h"
#define STACK_SIZE 5

//Allocate space in memory for the stack
int StackSpace[STACK_SIZE];

//pointers used to navigate stack
int* stackPtr;

//initialize "empty" stack
void stack_init(void) {
  //stackPtr points to address 0 when stack is empty
  stackPtr = 0;
  //Writes over array to prevent junk data
  for (int i = 0; i<STACK_SIZE; ++i) {
    StackSpace[i] = 0;
  }
}


int stack_push(int data) {
  //if stack is full, throw fault
  if(stack_full()) { return -1; }
  //make stackPtr point at the next empty slot
  if(stackPtr == 0) { stackPtr = &StackSpace[0]; }
  else { stackPtr++; }
  //store data in stack
  *stackPtr = data;
  return 0;
}
int stack_pop(int* data) {
  //if stack is empty, throw fault
  if(stack_empty()) {return -1; }
  //retrive data from stack
  *data = *stackPtr;
  //make stackPtr point at the next full slot
  if(stackPtr == &StackSpace[0]) { stackPtr = 0; }
  else { stackPtr--; }
  return 0;
}

int stack_full() { 
  if(stackPtr == &StackSpace[STACK_SIZE-1]) { return 1; }
  return 0;
}

int stack_empty() {
  if(stackPtr == 0) { return 1; }
  return 0;
}