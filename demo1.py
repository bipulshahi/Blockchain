# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 12:34:52 2020

@author: vipul
"""

class Employee:
    def __init__(self, first, second, contact, salary):
        self.first=first
        self.second=second
        self.contact=contact
        self.salary=salary
        
    def fullname(self):
        return '{} {}'.format(self.first,self.second)
        
emp1 = Employee('Bipul','Shahi','98765431',40000)
emp2 = Employee('Kunal','Singh','98678978',30000)

print(Employee.fullname(emp1))
print(Employee.fullname(emp2))

print(emp1.fullname())







