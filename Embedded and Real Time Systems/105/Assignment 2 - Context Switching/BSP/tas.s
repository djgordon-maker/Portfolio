  PUBLIC testAndSet


  SECTION .text:CODE:REORDER:NOROOT(2)   
  THUMB 


//R0 holds the address to a locking variable
testAndSet
  //Prepare to load a 1 into the locking variable
  MOV R1, #1
  //Disable interupts
  CPSID I
  //Find out if the resource is available
try
  LDREX R2, [R0]
  CMP   R2, #0
  //If available, lock resource
  ITT     EQ
  STREXEQ R2, R1, [R0]
  CMPEQ   R2, #0
  //If not available or STR not successfull, try again
  BNE    try
  //Resource is locked, Enable interupts and return
  CPSIE I
  BX LR
  
  END
