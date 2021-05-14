#ifndef __STACK_H__
#define __STACK_H__

void stack_init(void);
int stack_push(int data);
int stack_pop(int* data);
int stack_full();
int stack_empty();

#endif
