# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:47:30 2020

@author: vipul
"""
#variable declaration
'''a='12.0'
b=12
print(a)
print(type(a))
print(type(b))'''

l = [12,34,67,89,123]
print(l[-1])

t = (34,67,89,12,45,56)
print(t[1])

d = {'name':'Bipul','email':'abc@abc.com'}
print(d['name'])

for i in range(0,10):
    i = i*2
    print(i)

   
def compare(a,b):
    if (a=='Bipul'):
        print('Its bipul You are no.',b)
    elif (a=='Gaurav'):
        print('Hello no', b)
    else:
        print('Some one else at no', b)

compare('Bipul',12)
compare('Gaurav',13)
compare('Pavan',56)

def abc(k,l):
    #return(k+l)
    m = k+l

print(abc(3,6)+2)




