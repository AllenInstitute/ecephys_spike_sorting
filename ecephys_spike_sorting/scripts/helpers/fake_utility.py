import sys, time
for i in range(10):
   print(i)
   sys.stdout.flush()
   time.sleep(1)

raise(ValueError('Testing pipe stderr'))