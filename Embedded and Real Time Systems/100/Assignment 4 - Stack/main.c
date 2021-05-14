#include <assert.h>
#include "stack.h"


int main()
{
  int result = 42;
  
  //test 1: detect an empty stack
  stack_init();
  assert(stack_empty());
  
  //test 2: push and pop a single item
  assert(stack_push(5) == 0);
  assert(stack_pop(&result) == 0);
  assert(result == 5);
  
  //test 3: fail to pop from an empty stack
  assert(stack_pop(&result) == -1);
  
  //test 4: detect a full stack
  stack_push(10);
  stack_push(11);
  stack_push(12);
  stack_push(13);
  stack_push(14);
  assert(stack_full());
         
  //test 5: fail to push to an full stack
  assert(stack_push(15) == -1);

  //test 6: pop one item and repeat last two tests
  stack_pop(&result);
  assert(result == 14);
  stack_push(16);
  assert(stack_push(17) == -1);
  assert(stack_full());
  
  //test 7: pop every item from the stack
  stack_pop(&result);
  assert(result == 16);  
  stack_pop(&result);
  assert(result == 13);  
  stack_pop(&result);
  assert(result == 12);  
  stack_pop(&result);
  assert(result == 11);  
  stack_pop(&result);
  assert(result == 10);
  assert(stack_empty());
  assert(stack_pop(&result) == -1);
  
  //test 8: fill and empty the stack twice
  stack_push(18);
  stack_push(19);
  stack_push(20);
  stack_push(21);
  stack_push(22); 
  assert(stack_push(23) == -1);
  assert(stack_full());
  
  stack_pop(&result);
  assert(result == 22);
  stack_pop(&result);
  assert(result == 21);
  stack_pop(&result);
  assert(result == 20);
  stack_pop(&result);
  assert(result == 19);
  stack_pop(&result);
  assert(result == 18);
  assert(stack_pop(&result) == -1);
  assert(result == 18);
  assert(stack_empty());
  
  stack_push(24);
  stack_push(25);
  stack_push(26);
  stack_push(27);
  stack_push(28); 
  assert(stack_push(29) == -1);
  assert(stack_full());
  
  stack_pop(&result);
  assert(result == 28);
  stack_pop(&result);
  assert(result == 27);
  stack_pop(&result);
  assert(result == 26);
  stack_pop(&result);
  assert(result == 25);
  stack_pop(&result);
  assert(result == 24);
  assert(stack_pop(&result) == -1);
  assert(result == 24);
  assert(stack_empty());
  
  return 0;
}
