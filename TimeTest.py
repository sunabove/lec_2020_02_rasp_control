# Python program to explain time.time_ns() method
	
# importing time module
import time
	
# Get the epoch
obj = time.gmtime(0)
epoch = time.asctime(obj)
print("epoch is:", epoch)
	
# Get the time in seconds
# since the epoch
# using time.time() method
time_sec = time.time()

# Print the time
# in seconds since the epoch
print("Time in seconds since the epoch:", time_sec)

# Print the time
# in nanoseconds since the epoch
for i in range( 1, 10 ) :
    time_nanosec = time.time_ns()
    print( f"[{i:04}] Time in nanose:", time_nanosec)
    time.sleep( i )
