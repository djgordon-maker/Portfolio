void swap_pointer(int**, int**);
int  swapCharsAsm(char*, char*);
  
int main()
{
  int x = 20;
  int y = 40;
  int* xPtr = &x;
  int* yPtr = &y;
  swap_pointer(&xPtr, &yPtr);
  
  char charA = '[';
  char charB = '[';
  int ans = swapCharsAsm(&charA, &charB);
  
  charA = 'd';
  charB = 'g';
  ans = swapCharsAsm(&charA, &charB);
  
  return 0;
}

void swap_pointer(int** ptrA, int** ptrB){
  int* temp_ptr = *ptrA;
  *ptrA = *ptrB;
  *ptrB =  temp_ptr;
}
