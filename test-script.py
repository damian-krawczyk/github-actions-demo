import os
print("Test script run")
secret_value = os.environ['EXAMPLE_SECRET']

if secret_value == 'EXAMPLE_SECRET_VALUE':
    print('SECRET VALUE GATHERED SUCCESSFULLY')