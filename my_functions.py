# import time
# from threading import Thread

# def my_function(callback):
#     # for i in range(1,10000):
#     #     output = i
#     #     time.sleep(0.3)
#     #     # Emit the output to the frontend
#     #     yield output
#     #     time.sleep(0.7)
#     #     output = f'''count -- > {i} '''
#     #     yield output
#     for i in range(1,10000):
#         # addd a result pop here every tome from the second time onwards
#         output = i
#         time.sleep(0.3)
#         # Emit the output to the frontend
#         callback(output)
#         time.sleep(0.7)
#         output = f'''count -- > {i} '''
#         callback(output)

# def start_my_function(callback):
#     thread = Thread(target=my_function, args=(callback,))
#     thread.start()
